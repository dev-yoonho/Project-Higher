from collections.abc import Sequence

import torch

import isaaclab.sim as sim_utils
from isaaclab.assets import Articulation
from isaaclab.envs import DirectRLEnv
from isaaclab.markers import VisualizationMarkers, VisualizationMarkersCfg
from isaaclab.sim.spawners.from_files import GroundPlaneCfg, spawn_ground_plane
from isaaclab.utils.assets import ISAAC_NUCLEUS_DIR
from isaaclab.utils.math import quat_apply, quat_from_euler_xyz

from .quickstart_lab_env_cfg import QuickstartLabEnvCfg


def define_markers():
    arrow_path = f"{ISAAC_NUCLEUS_DIR}/Props/UIElements/arrow_x.usd"

    return VisualizationMarkers(
        VisualizationMarkersCfg(
            prim_path="/Visuals/jetbot_directions",
            markers={
                "forward": sim_utils.UsdFileCfg(
                    usd_path=arrow_path,
                    scale=(0.25, 0.25, 0.5),
                    visual_material=sim_utils.PreviewSurfaceCfg(
                        diffuse_color=(0.0, 1.0, 1.0),
                    ),
                ),
                "command": sim_utils.UsdFileCfg(
                    usd_path=arrow_path,
                    scale=(0.25, 0.25, 0.5),
                    visual_material=sim_utils.PreviewSurfaceCfg(
                        diffuse_color=(1.0, 0.0, 0.0),
                    ),
                ),
            },
        )
    )


class QuickstartLabEnv(DirectRLEnv):
    cfg: QuickstartLabEnvCfg

    def __init__(self, cfg, render_mode=None, **kwargs):
        super().__init__(cfg, render_mode, **kwargs)

        self.wheel_ids, _ = self.robot.find_joints(
            self.cfg.wheel_names, preserve_order=True
        )
        self.actions = torch.zeros((self.num_envs, 2), device=self.device)

        # 세계 좌표계 기준 목표 방향. Z=0인 평면 방향이다.
        self.commands = torch.zeros((self.num_envs, 3), device=self.device)
        self.commands[:, 0] = 1.0

        self.marker_indices = torch.cat(
            (
                torch.zeros(self.num_envs, dtype=torch.long, device=self.device),
                torch.ones(self.num_envs, dtype=torch.long, device=self.device),
            )
        )

    def _setup_scene(self):
        self.robot = Articulation(self.cfg.robot_cfg)
        spawn_ground_plane("/World/ground", cfg=GroundPlaneCfg())

        self.scene.clone_environments(copy_from_source=False)
        if self.device == "cpu":
            self.scene.filter_collisions(global_prim_paths=["/World/ground"])
        self.scene.articulations["robot"] = self.robot

        light_cfg = sim_utils.DomeLightCfg(
            intensity=2000.0, color=(0.75, 0.75, 0.75)
        )
        light_cfg.func("/World/Light", light_cfg)

        self.direction_markers = define_markers()

    def _pre_physics_step(self, actions: torch.Tensor):
        self.actions = actions.clone()

    def _apply_action(self):
        # 좌우 바퀴의 목표 각속도(rad/s).
        self.robot.set_joint_velocity_target(
            self.actions, joint_ids=self.wheel_ids
        )

    def _get_observations(self):
        self._visualize_markers()

        forward_w = quat_apply(
            self.robot.data.root_link_quat_w,
            self.robot.data.FORWARD_VEC_B,
        )

        # 같은 방향=1, 직각=0, 정반대=-1.
        alignment = torch.sum(forward_w * self.commands, dim=-1)

        # 평지에서 목표가 몸체 왼쪽이면 양수, 오른쪽이면 음수.
        side = torch.cross(forward_w, self.commands, dim=-1)[:, 2]
        forward_speed = self.robot.data.root_com_lin_vel_b[:, 0]

        obs = torch.stack((alignment, side, forward_speed), dim=-1)
        return {"policy": obs}

    def _get_rewards(self):
        # 몸체의 앞 방향을 세계 좌표계의 방향으로 변환한다.
        forward_w = quat_apply(
            self.robot.data.root_link_quat_w,
            self.robot.data.FORWARD_VEC_B,
        )

        # 전진은 양수, 후진은 음수인 몸체 기준 속도(m/s).
        forward_speed = self.robot.data.root_com_lin_vel_b[:, 0]

        # 같은 방향=1, 직각=0, 정반대=-1.
        alignment = torch.sum(forward_w * self.commands, dim=-1)

        return forward_speed + alignment

    def _get_dones(self):
        time_out = self.episode_length_buf >= self.max_episode_length - 1
        terminated = torch.zeros_like(time_out)
        return terminated, time_out

    def _visualize_markers(self):
        forward_pos = self.robot.data.root_pos_w.clone()
        command_pos = forward_pos.clone()

        # 겹쳐 가려지는 것을 줄이도록 서로 다른 높이에 표시한다.
        forward_pos[:, 2] += 0.35
        command_pos[:, 2] += 0.55

        # 목표 방향을 세계 Z축 주위 회전각(rad)으로 변환한다.
        yaw = torch.atan2(self.commands[:, 1], self.commands[:, 0])
        zeros = torch.zeros_like(yaw)
        command_quat = quat_from_euler_xyz(zeros, zeros, yaw)

        self.direction_markers.visualize(
            translations=torch.cat((forward_pos, command_pos), dim=0),
            orientations=torch.cat(
                (self.robot.data.root_quat_w, command_quat), dim=0
            ),
            marker_indices=self.marker_indices,
        )

    def _reset_idx(self, env_ids: Sequence[int] | None):
        if env_ids is None:
            env_ids = self.robot._ALL_INDICES
        super()._reset_idx(env_ids)

        # 초기화되는 환경에만 새 방향을 정한다. 크기는 1로 맞춘다.
        directions = torch.randn((len(env_ids), 3), device=self.device)
        directions[:, 2] = 0.0
        directions /= torch.linalg.vector_norm(
            directions, dim=-1, keepdim=True
        ).clamp_min(1e-8)
        self.commands[env_ids] = directions

        root_state = self.robot.data.default_root_state[env_ids].clone()
        root_state[:, :3] += self.scene.env_origins[env_ids]

        joint_pos = self.robot.data.default_joint_pos[env_ids].clone()
        joint_vel = self.robot.data.default_joint_vel[env_ids].clone()

        self.robot.write_root_state_to_sim(root_state, env_ids=env_ids)
        self.robot.write_joint_state_to_sim(
            joint_pos, joint_vel, env_ids=env_ids
        )
        self.robot.set_joint_velocity_target(
            torch.zeros_like(joint_vel), env_ids=env_ids
        )
