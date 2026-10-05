import argparse
import time

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser()
parser.add_argument("--left", type=float, default=5.0)
parser.add_argument("--right", type=float, default=5.0)
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()

app_launcher = AppLauncher(args)
simulation_app = app_launcher.app

import gymnasium as gym
import torch

import quickstart_lab.tasks
from isaaclab_tasks.utils import parse_env_cfg


def main():
    task = "Template-Quickstart-Lab-Direct-v0"
    cfg = parse_env_cfg(task, device=args.device, num_envs=1)
    cfg.viewer.eye = (2.5, 2.5, 1.8)
    cfg.viewer.lookat = (0.0, 0.0, 0.2)

    env = gym.make(task, cfg=cfg)
    try:
        env.reset()
        robot_env = env.unwrapped
        dt = robot_env.step_dt

        # 순서: 왼쪽, 오른쪽. 단위는 바퀴 목표 각속도 rad/s.
        actions = torch.tensor(
            [[args.left, args.right]],
            dtype=torch.float32,
            device=robot_env.device,
        )
        print(f"[TARGET] left={args.left}, right={args.right} rad/s")

        with torch.inference_mode():
            for step in range(600):
                if not simulation_app.is_running():
                    break

                start = time.perf_counter()
                _, _, terminated, truncated, _ = env.step(actions)

                if (step + 1) % 60 == 0:
                    wheel_vel = robot_env.robot.data.joint_vel[
                        0, robot_env.wheel_ids
                    ].tolist()
                    print(
                        f"[DRIVE] time={(step + 1) * dt:.2f}s "
                        f"wheel_vel={wheel_vel}"
                    )

                if (terminated | truncated).any().item():
                    print("[RESET] Episode ended; returned to start.")

                # 가상 시간이 너무 빨리 지나가지 않도록 표시 속도를 맞춘다.
                time.sleep(max(0.0, dt - (time.perf_counter() - start)))
    finally:
        env.close()


if __name__ == "__main__":
    try:
        main()
    finally:
        simulation_app.close()