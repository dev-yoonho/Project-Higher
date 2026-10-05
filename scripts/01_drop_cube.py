r"""상자의 낙하와 바닥 접촉 관찰.

실행: isaaclab.bat -p C:\makerobot\scripts\01_drop_cube.py
복습: C:\makerobot\STUDY_NOTES.md
"""

import argparse

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="Drop one cube onto a fixed floor.")

AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()

simulation_app = AppLauncher(args).app

# Isaac Sim 앱이 시작된 뒤 시뮬레이션 모듈을 불러온다.
import isaaclab.sim as sim_utils
from isaaclab.assets import RigidObject, RigidObjectCfg

# 단위: 시간 s, 길이 m. DT는 한 스텝의 가상 시간이다.
DT = 0.01

START_HEIGHT = 1.0  # 상자 중심의 출발 높이

CUBE_SIZE = 0.2

RESET_STEPS = 300  # 3초마다 낙하를 다시 관찰한다.


def main():
    # +z가 위쪽이므로 중력 가속도는 z=-9.81m/s²다.
    sim = sim_utils.SimulationContext(
        sim_utils.SimulationCfg(dt=DT, gravity=(0.0, 0.0, -9.81), device=args.device)
    )
    try:

        sim.set_camera_view(eye=[2.5, 2.5, 1.8], target=[0.0, 0.0, 0.5])

        # 충돌 형상만 설정한 고정 바닥. 중심 -0.05m + 반높이 0.05m = 윗면 0m.
        floor_cfg = sim_utils.CuboidCfg(
            size=(4.0, 4.0, 0.1),
            collision_props=sim_utils.CollisionPropertiesCfg(),

            visual_material=sim_utils.PreviewSurfaceCfg(diffuse_color=(0.5, 0.5, 0.5)),
        )

        floor_cfg.func("/World/Floor", floor_cfg, translation=(0.0, 0.0, -0.05))

        light_cfg = sim_utils.DomeLightCfg(intensity=2000.0)
        light_cfg.func("/World/Light", light_cfg)

        # 강체는 움직이되 형태가 변하지 않는 물체다. 바닥과 닿도록 충돌 형상도 준다.
        cube = RigidObject(
            RigidObjectCfg(
                prim_path="/World/Cube",
                spawn=sim_utils.CuboidCfg(
                    size=(CUBE_SIZE, CUBE_SIZE, CUBE_SIZE),

                    rigid_props=sim_utils.RigidBodyPropertiesCfg(disable_gravity=False),
                    mass_props=sim_utils.MassPropertiesCfg(mass=1.0),

                    collision_props=sim_utils.CollisionPropertiesCfg(),

                    # 반발 계수 0: 충돌 후 튕김을 줄인다.
                    physics_material=sim_utils.RigidBodyMaterialCfg(restitution=0.0),
                    visual_material=sim_utils.PreviewSurfaceCfg(diffuse_color=(0.1, 0.4, 0.9)),
                ),

                init_state=RigidObjectCfg.InitialStateCfg(pos=(0.0, 0.0, START_HEIGHT)),
            )
        )

        sim.reset()  # 장면 생성 후 물리 계산과 상태 접근을 준비한다.

        print(f"[INFO] Drop ready: center z={START_HEIGHT} m; cube side={CUBE_SIZE} m; floor top z=0.", flush=True)
        print(f"[INFO] Repeats every {RESET_STEPS * DT:g} simulated seconds. Close the window to exit.", flush=True)

        step = 0
        while simulation_app.is_running():
            if step == RESET_STEPS:
                # 시작 상태로 직접 재배치한다. 물리적으로 튀어 오르는 현상이 아니다.
                cube.write_root_state_to_sim(cube.data.default_root_state.clone())

                cube.reset()  # 외력 관련 버퍼 초기화. 재배치는 위 줄이 수행한다.
                step = 0
                print("[INFO] Restart drop (script reset).", flush=True)

            # 명령 전달 → 물리 계산 → 읽을 상태의 시간 갱신. 중력은 엔진이 적용한다.
            cube.write_data_to_sim()

            sim.step()

            cube.update(DT)
            step += 1

            if step % 10 == 0 and step <= 60:
                # [물체 번호, 좌표 성분]: 2는 z. 이번 모델의 기준점은 상자 중심이다.
                z = cube.data.root_pos_w[0, 2].item()

                vz = cube.data.root_com_lin_vel_w[0, 2].item()  # vz<0이면 하강

                # 바닥에 놓이면 중심 높이≈0.1m, 속도≈0을 예상한다.
                print(f"t={step * DT:.2f} s | center z={z:.3f} m | vz={vz:.3f} m/s", flush=True)
    finally:

        sim.clear_all_callbacks()
        sim.clear_instance()


if __name__ == "__main__":
    try:
        main()
    finally:

        simulation_app.close()
