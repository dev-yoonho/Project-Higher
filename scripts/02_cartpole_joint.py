r"""Cartpole 수레의 목표 위치와 실제 관절 위치 비교.

실행: isaaclab.bat -p C:\makerobot\scripts\02_cartpole_joint.py
목표: 3초마다 0 → +0.5 → -0.5m 반복. 막대는 구동하지 않아 흔들릴 수 있다.
복습: C:\makerobot\STUDY_NOTES.md
"""

import argparse
import math

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="Observe a cart joint tracking position targets.")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
simulation_app = AppLauncher(args).app

# Isaac Sim 앱이 시작된 뒤 관련 모듈을 불러온다.
import torch

import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets import Articulation
from isaaclab_assets import CARTPOLE_CFG

DT = 0.01  # 한 물리 스텝의 가상 시간(s)
HOLD_STEPS = 300  # 3초마다 목표 변경
PRINT_STEPS = 50  # 0.5초마다 출력
TARGET_POSITIONS = (0.0, 0.5, -0.5)  # 직선 관절 위치(m)

# 위치 오차에 반응하는 세기, 속도를 줄이는 세기, 최대 힘. 학습용 시작값이다.
CART_STIFFNESS = 100.0  # N/m
CART_DAMPING = 20.0  # N·s/m
CART_FORCE_LIMIT = 50.0  # N


def main():
    sim = sim_utils.SimulationContext(
        sim_utils.SimulationCfg(dt=DT, gravity=(0.0, 0.0, -9.81), device=args.device)
    )
    try:

        # 기본 모델의 기준점은 z=2m다.
        sim.set_camera_view(eye=[4.0, -6.0, 4.0], target=[0.0, 0.0, 2.0])

        floor_cfg = sim_utils.CuboidCfg(
            size=(8.0, 6.0, 0.1),
            collision_props=sim_utils.CollisionPropertiesCfg(),
            visual_material=sim_utils.PreviewSurfaceCfg(diffuse_color=(0.5, 0.5, 0.5)),
        )
        floor_cfg.func("/World/Floor", floor_cfg, translation=(0.0, 0.0, -0.05))
        light_cfg = sim_utils.DomeLightCfg(intensity=2000.0)
        light_cfg.func("/World/Light", light_cfg)

        # Articulation은 여러 강체(링크)가 관절로 연결된 모델을 다룬다.
        robot_cfg = CARTPOLE_CFG.copy()
        robot_cfg.prim_path = "/World/Cartpole"

        # 수레는 직선 관절(m), 막대는 회전 관절(rad). 0.1rad≈5.7도다.
        robot_cfg.init_state.joint_pos = {"slider_to_cart": 0.0, "cart_to_pole": 0.1}

        # 구동기는 힘/토크를 만드는 모델이다. 위치·속도 제어 계산은 엔진이 맡는다.
        robot_cfg.actuators = {
            "cart_actuator": ImplicitActuatorCfg(
                joint_names_expr=["slider_to_cart"],
                effort_limit_sim=CART_FORCE_LIMIT,
                stiffness=CART_STIFFNESS,
                damping=CART_DAMPING,
            ),
            # 막대는 구동 토크 0. 관절을 고정한 것이 아니므로 자유롭게 회전한다.
            "pole_actuator": ImplicitActuatorCfg(
                joint_names_expr=["cart_to_pole"],
                effort_limit_sim=0.0,
                stiffness=0.0,
                damping=0.0,
            ),
        }
        robot = Articulation(robot_cfg)

        sim.reset()

        # 배열 순서를 추측하지 않고 관절 이름으로 번호를 찾는다.
        cart_ids, _ = robot.find_joints("slider_to_cart")
        pole_ids, _ = robot.find_joints("cart_to_pole")
        if len(cart_ids) != 1 or len(pole_ids) != 1:
            raise RuntimeError(f"Expected one cart joint and one pole joint; got {robot.joint_names}")
        cart_id, pole_id = cart_ids[0], pole_ids[0]

        # 시작할 때만 위치·속도를 직접 설정한다. 반복 중에는 목표만 바꾼다.
        root_state = robot.data.default_root_state.clone()
        robot.write_root_pose_to_sim(root_state[:, :7])
        robot.write_root_velocity_to_sim(root_state[:, 7:])
        robot.write_joint_state_to_sim(
            robot.data.default_joint_pos.clone(), robot.data.default_joint_vel.clone()
        )
        robot.reset()

        # 명령 모양: (모델 수, 선택한 관절 수). 이번에는 (1, 1)이다.
        position_target = torch.zeros((robot.num_instances, 1), device=sim.device)
        velocity_target = torch.zeros_like(position_target)

        # 목표 위치에 도달한 뒤 정지하도록 목표 속도는 0으로 둔다.
        robot.set_joint_velocity_target(velocity_target, joint_ids=cart_ids)

        print(f"[INFO] Joints: {robot.joint_names}", flush=True)
        print("[INFO] Position targets: 0.0 -> +0.5 -> -0.5 m, every 3 simulated seconds.", flush=True)
        print("[INFO] Pole is unpowered. Close the window to exit.", flush=True)

        step = 0
        while simulation_app.is_running():
            phase = (step // HOLD_STEPS) % len(TARGET_POSITIONS)
            target = TARGET_POSITIONS[phase]
            position_target.fill_(target)
            if step % HOLD_STEPS == 0:
                print(f"[TARGET] t={step * DT:.2f} s | target={target:+.3f} m", flush=True)

            # 목표 저장 → 구동기에 전달. 현재 위치를 순간이동시키는 호출이 아니다.
            robot.set_joint_position_target(position_target, joint_ids=cart_ids)
            robot.write_data_to_sim()

            # 제어 원리: 힘≈stiffness×위치 오차−damping×속도. 힘 한계도 적용한다.
            sim.step()
            robot.update(DT)
            step += 1

            if step % PRINT_STEPS == 0:
                position = robot.data.joint_pos[0, cart_id].item()
                velocity = robot.data.joint_vel[0, cart_id].item()
                pole_angle = robot.data.joint_pos[0, pole_id].item()
                error = target - position  # 절댓값이 작을수록 목표에 가깝다.

                # 막대 각도는 읽을 때 rad, 출력할 때만 도(deg)로 변환한다.
                print(
                    f"t={step * DT:.2f} s | target={target:+.3f} m | "
                    f"cart={position:+.3f} m | error={error:+.3f} m | "
                    f"v={velocity:+.3f} m/s | pole={math.degrees(pole_angle):+.1f} deg",
                    flush=True,
                )
    finally:
        sim.clear_all_callbacks()
        sim.clear_instance()


if __name__ == "__main__":
    try:
        main()
    finally:
        simulation_app.close()
