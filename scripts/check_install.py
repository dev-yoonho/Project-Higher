"""Bounded installation check; does not train a policy.

Run in env_isaaclab: python scripts/check_install.py --headless
Add --task Isaac-Cartpole-v0 to also exercise a small GPU task.
"""

import argparse
import json

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--steps", type=int, default=120)
parser.add_argument("--task", default=None)
parser.add_argument("--num_envs", type=int, default=4)
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
if args.steps < 1 or args.num_envs < 1:
    parser.error("--steps and --num_envs must be positive")

app = AppLauncher(args).app
env = None
sim = None
try:
    import h5py
    import torch
    from rsl_rl.runners import OnPolicyRunner  # noqa: F401

    with h5py.File("install_check.h5", "w", driver="core", backing_store=False) as data:
        data.create_dataset("values", data=[1, 2, 3])
        if data["values"][:].tolist() != [1, 2, 3]:
            raise RuntimeError("HDF5 round-trip failed")

    if args.task:
        import gymnasium as gym
        import isaaclab_tasks  # noqa: F401
        from isaaclab_tasks.utils import parse_env_cfg

        cfg = parse_env_cfg(args.task, device=args.device, num_envs=args.num_envs)
        cfg.seed = 42
        env = gym.make(args.task, cfg=cfg)
        env.reset()
        with torch.inference_mode():
            actions = torch.zeros(env.action_space.shape, device=env.unwrapped.device)
            for _ in range(args.steps):
                obs, rewards, terminated, truncated, info = env.step(actions)
                if not torch.isfinite(rewards).all():
                    raise RuntimeError("Non-finite rewards")
                policy_obs = obs["policy"]
                if not torch.isfinite(policy_obs).all():
                    raise RuntimeError("Non-finite policy observations")
    else:
        from isaaclab.sim import SimulationCfg, SimulationContext

        sim = SimulationContext(SimulationCfg(dt=0.01, device=args.device))
        sim.set_camera_view([2.5, 2.5, 2.5], [0.0, 0.0, 0.0])
        sim.reset()
        for _ in range(args.steps):
            sim.step()

    torch.cuda.synchronize()
    print("INSTALL_CHECK_PASS " + json.dumps({
        "task": args.task or "empty_scene",
        "headless": args.headless,
        "steps": args.steps,
        "num_envs": args.num_envs if args.task else 0,
        "device": args.device,
        "gpu": torch.cuda.get_device_name(0),
        "torch": torch.__version__,
        "rsl_rl_import": "ok",
        "h5py": h5py.__version__,
        "hdf5": h5py.version.hdf5_version,
        "hdf5_roundtrip": "ok",
    }), flush=True)
finally:
    if env is not None:
        env.close()
    elif sim is not None:
        sim.clear_all_callbacks()
        sim.clear_instance()
    app.close()
