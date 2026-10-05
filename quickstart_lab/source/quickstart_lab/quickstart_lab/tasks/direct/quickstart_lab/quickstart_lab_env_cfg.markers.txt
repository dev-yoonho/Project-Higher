import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets import ArticulationCfg
from isaaclab.envs import DirectRLEnvCfg
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.sim import SimulationCfg
from isaaclab.utils import configclass
from isaaclab.utils.assets import ISAAC_NUCLEUS_DIR


@configclass
class QuickstartLabEnvCfg(DirectRLEnvCfg):
    decimation = 2
    episode_length_s = 5.0

    action_space = 2       # 좌우 바퀴 목표 각속도, rad/s
    observation_space = 3 # 몸체 기준 선속도 x·y·z, m/s
    state_space = 0

    sim: SimulationCfg = SimulationCfg(
        dt=1 / 120,
        render_interval=decimation,
    )

    robot_cfg: ArticulationCfg = ArticulationCfg(
        prim_path="/World/envs/env_.*/Robot",
        spawn=sim_utils.UsdFileCfg(
            usd_path=f"{ISAAC_NUCLEUS_DIR}/Robots/NVIDIA/Jetbot/jetbot.usd",
        ),
        actuators={
            "wheels": ImplicitActuatorCfg(
                joint_names_expr=["left_wheel_joint", "right_wheel_joint"],
                stiffness=None,
                damping=None,  # 모델에 저장된 구동 설정 사용
            ),
        },
    )

    scene: InteractiveSceneCfg = InteractiveSceneCfg(
        num_envs=4,
        env_spacing=4.0,
        replicate_physics=True,
    )

    wheel_names = ["left_wheel_joint", "right_wheel_joint"]