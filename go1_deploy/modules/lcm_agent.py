import time
from typing import List

import lcm
import numpy as np
import torch
import cv2
import torchvision
 
from go1_deploy.modules import lc_addr
from go1_deploy.lcm_types.pd_tau_targets_lcmt import pd_tau_targets_lcmt
from go1_deploy.modules.base_node import BaseNode
from go1_deploy.modules.state_estimator import JOINT_IDX_MAPPING

lc = lcm.LCM(lc_addr)

class LCMAgent(BaseNode):
    # DOFs in simulation ordering
    dof_names = [
        'FL_hip_joint',
        'FL_thigh_joint',
        'FL_calf_joint',
        'FR_hip_joint',
        'FR_thigh_joint',
        'FR_calf_joint',
        'RL_hip_joint',
        'RL_thigh_joint',
        'RL_calf_joint',
        'RR_hip_joint',
        'RR_thigh_joint',
        'RR_calf_joint',
    ]

    def __init__(
        self, 
        env_cfg,
        device: str, 
        debug=False,
    ):
        super().__init__()

        self.env_cfg = env_cfg
        self.device = device
        self.debug = debug

        self.default_joint_angles = env_cfg.init_state.default_joint_angles
        self.stiffness_dict = env_cfg.control.stiffness
        self.damping_dict = env_cfg.control.damping
        self.action_scale = env_cfg.control.action_scale
        self.hip_scale_reduction = None
        self.obs_scales = env_cfg.normalization.obs_scales
        self.num_dofs = 12
        self.p_gains = np.zeros(self.num_dofs)
        self.d_gains = np.zeros(self.num_dofs)
        self._prepare_cfg()

        self.t = 0
        self.dt = env_cfg.sim.dt * env_cfg.control.decimation
        # Settings for lock-step polling, unused
        self.dt_ms = self.dt * 1000
        self.offset_ms = self.dt_ms / 10 * 2  # Lock-step with depth encoder
        self.sleep_ms = 0

        self.just_started = True

        self.n_proprio = env_cfg.env.n_proprio
        self.n_scan = env_cfg.env.n_scan
        self.n_priv = env_cfg.env.n_priv
        self.n_priv_latent = env_cfg.env.n_priv_latent

        self.history_len = env_cfg.env.history_len
        self.clip_actions = env_cfg.normalization.clip_actions
        self.clip_observations = env_cfg.normalization.clip_observations
        self.update_interval = env_cfg.depth.update_interval
        self.near_clip = env_cfg.depth.near_clip
        self.far_clip = env_cfg.depth.far_clip
        self.width, self.height = env_cfg.depth.original_resolution
        
        self.previous_actions = torch.zeros((1, 12), device=self.device, dtype=torch.float32)  # using unitree indexing
        self.previous_contacts = torch.zeros((1, 4), device=device, dtype=torch.float32)  # using unitree indexing
        self.previous_body_ang_vel = torch.zeros(3, device=self.device)
        self.obs_history_buf = torch.zeros(1, self.history_len, self.n_proprio, device=device, dtype=torch.float32)
        self.extras = {}

        self.resize_transform = torchvision.transforms.Resize(
            (self.height, self.width), interpolation=torchvision.transforms.InterpolationMode.BICUBIC
        )

        self.create_buffer_infos = {
            "lcm_agent-obs_proprio": ((1, 48), np.float32),
        }
        self.access_buffer_infos = {
            "state_estimator-euler": ((1, 3), np.float32),
            "state_estimator-deuler": ((1, 3), np.float32),
            "state_estimator-joint_pos": ((1, 12), np.float32),
            "state_estimator-joint_vel": ((1, 12), np.float32),
            "state_estimator-contact_state": ((1, 4), np.float32),
            "state_estimator-joysticks": ((4,), np.float32),
            "state_estimator-trigger": ((2,), np.float32)
        }
        # We call this directly instead of using a wrapper because it must be available before DeploymentRunner.run()
        self._create_buffers()
        self._access_buffers()

    def _prepare_cfg(self):
        assert self.num_dofs == len(self.dof_names), "Number of DOFs mismatch"
        self.default_dof_pos = torch.zeros(self.num_dofs, device=self.device)[None, ...]
        for i, name in enumerate(self.dof_names):
            self.default_dof_pos[0, i] = self.default_joint_angles[name]
            found = False
            for dof_name in self.stiffness_dict.keys():
                if dof_name in name:
                    self.p_gains[i] = self.stiffness_dict[dof_name]
                    self.d_gains[i] = self.damping_dict[dof_name]
                    found = True
            assert found, f"PD gains not found for joint {name}"

    def publish_action(self, action, hard_reset=False, debug=False) -> List:
        """
        WARNING: Make sure the drive mode is set to POSITION, other modes not supported right now.
        
        IMPORTANT: actions is expected to be in the UNITREE indexing format. 
        
        Note that we do not scale the hip positions
        """
        command_for_robot = pd_tau_targets_lcmt()
        joint_pos_target = action[0, :12].detach()

        # Scale the actions
        joint_pos_target *= self.action_scale
        joint_pos_target = joint_pos_target.flatten()

        # Add offset
        joint_pos_target += self.default_dof_pos[0]

        # Convert to real robot indexing
        joint_pos_target = joint_pos_target.cpu().numpy()
        joint_pos_target = joint_pos_target[JOINT_IDX_MAPPING]
        joint_vel_target = np.zeros(12)

        command_for_robot.q_des = joint_pos_target
        command_for_robot.qd_des = joint_vel_target
        command_for_robot.kp = self.p_gains
        command_for_robot.kd = self.d_gains
        command_for_robot.tau_ff = np.zeros(12)
        command_for_robot.se_contactState = np.zeros(4)
        command_for_robot.timestamp_us = int(time.perf_counter() * 10 ** 6)
        command_for_robot.id = 0

        if hard_reset:
            command_for_robot.id = -1
        if not debug:
            lc.publish("pd_plustau_targets", command_for_robot.encode())
        else:
            pass

        return joint_pos_target

    def reset(self):
        self.actions = torch.zeros(12, device=self.device)
        self.just_started = True

        self.compute_observations()
        return self.obs_buf
    
    def step(self, actions, hard_reset=False, debug=False):
        """
        actions: from policy output, in unitree indexing. Converted to isaacgym here to be compatiable
        with default dof indexing
        """

        self.previous_actions = actions.clone()
        clip_actions = self.clip_actions / self.action_scale
        self.actions = torch.clip(actions, -clip_actions, clip_actions).to(self.device)

        self.start_profile("lcm_agent/publish_action")
        self.publish_action(self.actions, hard_reset=hard_reset, debug=debug)
        self.stop_profile("lcm_agent/publish_action")

        time_elapsed = self.stop_profile("lcm_agent", save=False)
        if time_elapsed + self.time_eps < self.dt:
            time.sleep(self.dt - time_elapsed - self.time_eps)
        elif time_elapsed > self.dt + self.time_eps:
            print(f"Warning: step time {time_elapsed}s is greater than dt {self.dt}s!")
        self.start_profile("lcm_agent")
        # while True:
        #     if (time.perf_counter() * 1000 - self.offset_ms) % self.dt_ms < 4:
        #         t = int((time.perf_counter() * 1000) / self.dt_ms)
        #         if self.t > 0 and t > self.t + 1:
        #             print(f"Warning: LCM agent is running behind by {t - self.t} steps!")
        #         self.t = t
        #         break
        #     else:
        #         time.sleep(self.sleep_ms / 1000)

        self.start_profile("lcm_agent/compute_observations")
        self.compute_observations()
        self.stop_profile("lcm_agent/compute_observations")

        clip_obs = self.clip_observations
        self.obs_buf = torch.clip(self.obs_buf, -clip_obs, clip_obs)

        if self.t % 100 == 0 and self.debug:
            self.print_profile()
            self.clear_profile()
            print()

        self.t += 1
        return self.obs_buf, self.extras

    def compute_observations(self, skip_depth=False):
        """
        Compute observations from state estimator.
        """
        self.start_profile("lcm_agent/prepare_buffers")
        self.prepare_buffers()
        self.stop_profile("lcm_agent/prepare_buffers")

        joysticks = self.read_buffer("state_estimator-joysticks")
        left_stick, right_stick = joysticks[:2], joysticks[2:]

        # Commands go from -1 to 1
        target_lin_vel_x, target_lin_vel_y, target_yaw = left_stick[1], left_stick[0], -1.0 * right_stick[0]
        # Assume policy can only move forward
        target_lin_vel_x = target_lin_vel_x / 2 + 0.5
        target_lin_vel_y = target_lin_vel_y / 2 + 0.5
        target_yaw = target_yaw / 2 + 0.5

        lin_vel_x_lo, lin_vel_x_hi = self.env_cfg.commands.ranges.lin_vel_x
        lin_vel_y_lo, lin_vel_y_hi = self.env_cfg.commands.ranges.lin_vel_y
        ang_vel_yaw_lo, ang_vel_yaw_hi = self.env_cfg.commands.ranges.ang_vel_yaw

        if target_lin_vel_x < 1e-3:
            target_lin_vel_x = 0
        else:
            target_lin_vel_x = lin_vel_x_lo + (lin_vel_x_hi - lin_vel_x_lo) * target_lin_vel_x
        target_lin_vel_y = lin_vel_y_lo + (lin_vel_y_hi - lin_vel_y_lo) * target_lin_vel_y
        target_yaw = ang_vel_yaw_lo + (ang_vel_yaw_hi - ang_vel_yaw_lo) * target_yaw

        target_lin_vel_x *= np.abs(target_lin_vel_x) > self.env_cfg.commands.lin_vel_clip
        target_lin_vel_y *= np.abs(target_lin_vel_y) > self.env_cfg.commands.lin_vel_clip

        self.delta_yaw = torch.zeros_like(self.imu[:, 2], device=self.device) + target_yaw
        self.delta_next_yaw = self.delta_yaw

        proprio = torch.cat((
            self.base_ang_vel * self.obs_scales.ang_vel,
            self.imu[:, :2],
            self.delta_yaw[None, ...],
            self.delta_next_yaw[None, ...],
            torch.tensor([[target_lin_vel_x]], device=self.device),
            (self.dof_pos - self.default_dof_pos) * self.obs_scales.dof_pos,
            self.dof_vel * self.obs_scales.dof_vel,
            self.previous_actions,
            self.contact_filt.float() - 0.5,
        ), dim=-1,)
        self.write_buffer("lcm_agent-obs_proprio", proprio.cpu())

        # These are placeholders and will be inferred by estimators
        scan = torch.zeros(1, self.n_scan, device=self.device, dtype=torch.float32)
        priv_explicit = torch.zeros(1, self.n_priv, device=self.device, dtype=torch.float32)
        priv_latent = torch.zeros(1, self.n_priv_latent, device=self.device, dtype=torch.float32)

        self.obs_buf = torch.cat([proprio, scan, priv_explicit, priv_latent, self.obs_history_buf.view(1, -1)], dim=-1)
        proprio[:, 5:7] = 0

        # prepare for the next timestep
        if self.just_started:
            self.obs_history_buf = torch.stack([proprio] * self.history_len, dim=1)
            self.just_started = False
        else:
            self.obs_history_buf = torch.cat([self.obs_history_buf[:, 1:], proprio.unsqueeze(1)], dim=1)

    def prepare_buffers(self):
        """
        Prepare buffers before computing observations.
        """

        self.base_ang_vel = self.read_buffer("state_estimator-deuler", as_torch=True)
        self.previous_body_ang_vel = self.base_ang_vel
        self.imu = self.read_buffer("state_estimator-euler", as_torch=True)
        self.dof_pos = self.read_buffer("state_estimator-joint_pos", as_torch=True)
        self.dof_vel = self.read_buffer("state_estimator-joint_vel", as_torch=True)
        self.contact_state = self.read_buffer("state_estimator-contact_state", as_torch=True)
        self.contact_filt = torch.logical_or(self.contact_state, self.previous_contacts)
        self.previous_contacts = self.contact_state
