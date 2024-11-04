"""
Take in the observations from the corresponding LCM agent, and output an action for stepping.

Simplified version that does not take in privileged information
"""

import os
import sys
from copy import deepcopy
from logging import warning
from typing import Tuple, Union
from pathlib import Path
import numpy as np

import torch
from torch import nn
import torch.jit

from go1_deploy.modules.base_node import BaseNode


class ParkourActor(BaseNode, nn.Module):
    def __init__(self, env_cfg, load_dir, depth_encoder, device, debug=False, save_obs=False, save_actions=False):
        super().__init__()

        self.env_cfg = env_cfg
        self.load_dir = load_dir
        self.depth_encoder = depth_encoder
        self.device = device
        self.debug = debug

        self.use_camera = env_cfg.depth.use_camera
        self.use_direction_distillation = env_cfg.depth.use_direction_distillation

        self.t = 0
        self.depth_encoder_duration = []
        self.policy_duration = []

        self.save_actions = save_actions
        self.save_obs = save_obs
        if self.save_obs:
            self.save_obs_path = f"{load_dir}/deployed_obs.npy"
            print(f"Saving obs to {self.save_obs_path}")
            self.saved_obs = []
            open(self.save_obs_path, "w")
        if self.save_actions:
            self.save_action_path = f"{load_dir}/deployed_actions.npy"
            print(f"Saving actions to {self.save_action_path}")
            self.saved_actions = []
            open(self.save_action_path, "w")

        self.load(load_dir)

        self.access_buffer_infos = {
            "depth_encoder-depth_latent": ((1, 32), np.float32)
        }
        # We call this directly instead of using a wrapper because it must be available before DeploymentRunner.run()
        self._access_buffers()

    def _parse_ac_params(self, params):
        actor_params = {}
        for k, v in params.items():
            if k.startswith("actor."):
                actor_params[k[6:]] = v
        return actor_params

    def load(self, load_dir):
        """Modified from OnPolicyRunner.load()"""
        load_dir = Path(load_dir)
        self.policy = torch.jit.load(load_dir / "traced" / "policy_latest.jit").to(self.device)

        # Dryrun
        with torch.no_grad():
            self.policy(torch.rand(1, self.env_cfg.env.num_observations, device=self.device), torch.rand(1, 32, device=self.device))
    
    def forward(self, obs):
        """
        Runs policy inference for deployment.

        Args:
            ego: egocentric camera frame
            obs: proprioception and other policy inputs
            vision_latent: latent representation of the camera frame
        
        Returns:
            actions: actions for the robot
            vision_latent: latent representation of the camera frame
        
        Note that ego is only available every Go1ParkourCfg.vision.update_interval timesteps (see ParkourLCMAgent.retrieve_depth()).
        Thus, we save and use the same vision_latent in between updates (see DeploymentRunner.run()).
        """

        obs = obs.float()
        depth_latent = self.read_buffer("depth_encoder-depth_latent", as_torch=True)
        self.start_profile("parkour_actor/policy")
        actions = self.policy(obs, depth_latent)
        self.stop_profile("parkour_actor/policy")

        if self.t % 100 == 0 and self.debug:
            self.print_profile()
            self.clear_profile()
            print()

        self.t += 1
        if self.save_obs:
            self.saved_obs.append(obs.cpu().numpy()[0])
        if self.save_actions:
            self.saved_actions.append(actions.cpu().numpy()[0])
        if (self.save_obs and len(self.saved_obs) > 100) or (self.save_actions and len(self.saved_actions) > 100):
            self.flush_saving()
            
        return actions, depth_latent
    
    def flush_saving(self):
        if self.save_obs:
            if os.path.exists(self.save_obs_path):
                saved_obs = np.load(self.save_obs_path)
                saved_obs = np.concatenate([saved_obs, self.saved_obs])
            else:
                saved_obs = self.saved_obs
            np.save(self.save_obs_path, saved_obs)
            self.saved_obs = []
        if self.save_actions:
            if os.path.exists(self.save_action_path):
                saved_actions = np.load(self.save_action_path)
                saved_actions = np.concatenate([saved_actions, self.saved_actions])
            else:
                saved_actions = self.saved_actions
            np.save(self.save_action_path, saved_actions)
            self.saved_actions = []