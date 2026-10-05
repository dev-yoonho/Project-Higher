import argparse

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser()
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()

app_launcher = AppLauncher(args)
simulation_app = app_launcher.app

import gymnasium as gym
import torch

from isaaclab_tasks.utils import parse_env_cfg
import quickstart_lab.tasks

def main():
    task = "Template-Quickstart-Lab-Direct-v0"
    cfg = parse_env_cfg(task, device=args.device, num_envs=1)
    env = gym.make(task, cfg=cfg)

    try:
        env.reset()
        step_dt = env.unwrapped.step_dt
        print(f"[Time] 환경 step 한 번 = {step_dt:.6f}초")

        actions = torch.zeros(
            env.action_space.shape,
            device=env.unwrapped.device,
        )

        with torch.inference_mode():
            for step in range(1, 181):
                if not simulation_app.is_running():
                    break

                env.step(actions)

                if step % 60 ==0:
                    sim_time = step * step_dt

                    print(
                        f"[TIME] step={step}, "
                        f"누적 가상 시간={sim_time:.2f}초"
                    )
    finally:
        env.close()

if __name__ == "__main__":
    try:
        main()
    finally:
        simulation_app.close()