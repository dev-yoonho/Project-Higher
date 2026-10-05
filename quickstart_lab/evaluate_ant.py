import argparse
import time
from pathlib import Path

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser()
parser.add_argument("--checkpoint", required=True)
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
checkpoint = Path(args.checkpoint).resolve()
if not checkpoint.is_file():
    raise FileNotFoundError(checkpoint)

app = AppLauncher(args).app

import gymnasium as gym
import torch
from skrl.utils.runner.torch import Runner

import isaaclab_tasks
from isaaclab.managers import (
    DatasetExportMode, RecorderManagerBaseCfg, RecorderTerm, RecorderTermCfg,
)
from isaaclab.utils import configclass
from isaaclab_rl.skrl import SkrlVecEnvWrapper
from isaaclab_tasks.utils import load_cfg_from_registry, parse_env_cfg


class PositionRecorder(RecorderTerm):
    def record_post_step(self):
        self._env.eval_x = self._env.scene["robot"].data.root_pos_w[:, 0].clone()
        return None, None

@configclass
class EvalRecorderCfg(RecorderManagerBaseCfg):
    dataset_export_mode = DatasetExportMode.EXPORT_NONE
    export_in_record_pre_reset = False
    position = RecorderTermCfg(class_type=PositionRecorder)


def main():
    task = "Isaac-Ant-v0"
    cfg = parse_env_cfg(task, device=args.device or "cuda:0", num_envs=4)
    cfg.seed = 42
    cfg.recorders = EvalRecorderCfg()
    agent_cfg = load_cfg_from_registry(task, "skrl_cfg_entry_point")
    agent_cfg["seed"] = 42
    agent_cfg["trainer"]["close_environment_at_exit"] = False
    agent_cfg["agent"]["experiment"]["write_interval"] = 0
    agent_cfg["agent"]["experiment"]["checkpoint_interval"] = 0

    raw_env = gym.make(task, cfg=cfg)
    base = raw_env.unwrapped
    env = SkrlVecEnvWrapper(raw_env, ml_framework="torch")
    try:
        runner = Runner(env, agent_cfg)
        runner.agent.load(str(checkpoint))
        runner.agent.set_running_mode("eval")
        obs, _ = env.reset()

        start_x = base.scene["robot"].data.root_pos_w[:, 0].clone()
        measured = torch.zeros(base.num_envs, dtype=torch.bool, device=base.device)
        results = []
        print(f"[EVAL] {checkpoint}")

        for step in range(1, base.max_episode_length + 2):
            if not app.is_running():
                break
            started = time.perf_counter()

            with torch.inference_mode():
                outputs = runner.agent.act(obs, timestep=0, timesteps=0)
                actions = outputs[-1].get("mean_actions", outputs[0])
                obs, _, terminated, truncated, _ = env.step(actions)

            fell = terminated.flatten()
            timed_out = truncated.flatten()
            newly_done = (fell | timed_out) & ~measured
            for i in newly_done.nonzero(as_tuple=True)[0].tolist():
                seconds = step * base.step_dt
                dx = (base.eval_x[i] - start_x[i]).item()
                fall = bool(fell[i].item())
                timeout = bool(timed_out[i].item())
                reason = "fall+timeout" if fall and timeout else ("fall" if fall else "timeout")
                results.append((i, seconds, dx, fall))
                measured[i] = True
                print(
                    f"[RESULT] env={i} time={seconds:.2f}s "
                    f"dx={dx:.3f}m mean_vx={dx / seconds:.3f}m/s end={reason}"
                )
            if measured.all().item():
                break
            if not args.headless:
                time.sleep(max(0.0, base.step_dt - (time.perf_counter() - started)))

        if len(results) == base.num_envs:
            n = len(results)
            print(
                f"[SUMMARY] episodes={n} "
                f"mean_dx={sum(r[2] for r in results) / n:.3f}m "
                f"mean_time={sum(r[1] for r in results) / n:.2f}s "
                f"falls={sum(r[3] for r in results)}/{n}"
            )
        else:
            print(f"[INCOMPLETE] measured={len(results)}/{base.num_envs}")
    finally:
        env.close()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.stderr.flush()
        sys.stdout.flush()
        raise
    finally:
        app.close()