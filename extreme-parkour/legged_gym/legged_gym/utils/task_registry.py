# SPDX-FileCopyrightText: Copyright (c) 2021 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Copyright (c) 2021 ETH Zurich, Nikita Rudin

from copy import deepcopy
import os
from datetime import datetime
from typing import Tuple
import torch
import numpy as np
from pathlib import Path
import pickle

from rsl_rl.env import VecEnv
from rsl_rl.runners import OnPolicyRunner

from legged_gym import LEGGED_GYM_ROOT_DIR
from .helpers import update_cfg_from_args, class_to_dict, get_checkpoint, set_seed, parse_sim_params
from legged_gym.envs.base.legged_robot_config import LeggedRobotCfg, LeggedRobotCfgPPO

class TaskRegistry():
    def __init__(self):
        self.task_classes = {}
        self.env_cfgs = {}
        self.train_cfgs = {}
    
    def register(self, name: str, task_class: VecEnv, env_cfg: LeggedRobotCfg, train_cfg: LeggedRobotCfgPPO):
        self.task_classes[name] = task_class
        self.env_cfgs[name] = env_cfg
        self.train_cfgs[name] = train_cfg
    
    def get_task_class(self, name: str) -> VecEnv:
        return self.task_classes[name]
    
    def get_cfgs(self, name) -> Tuple[LeggedRobotCfg, LeggedRobotCfgPPO]:
        train_cfg = self.train_cfgs[name]
        env_cfg = self.env_cfgs[name]
        env_cfg.seed = train_cfg.seed
        return env_cfg, train_cfg
    
    def get_saved_cfgs(self, load_dir) -> Tuple[LeggedRobotCfg, LeggedRobotCfgPPO]:
        config_path = Path(load_dir) / "legged_robot_config.pkl"
        if not config_path.exists():
            return None, None
        with open(config_path, "rb") as f:
            cfgs = pickle.load(f)
        return cfgs
    
    def make_env(self, name, args, env_cfg=None) -> Tuple[VecEnv, LeggedRobotCfg]:
        """ Creates an environment either from a registered namme or from the provided config file.

        Args:
            name (string): Name of a registered env.
            args (Args): Isaac Gym comand line arguments.
            env_cfg (Dict, optional): Environment config file used to override the registered config. Defaults to None.

        Raises:
            ValueError: Error if no registered env corresponds to 'name' 

        Returns:
            isaacgym.VecTaskPython: The created environment
            Dict: the corresponding config file
        """
        # check if there is a registered env with that name
        if name in self.task_classes:
            task_class = self.get_task_class(name)
        else:
            raise ValueError(f"Task with name: {name} was not registered")
        if env_cfg is None:
            # load config files
            env_cfg, _ = self.get_cfgs(name)
        # override cfg from args (if specified)
        env_cfg, _ = update_cfg_from_args(env_cfg, None, args)
        set_seed(env_cfg.seed)
        # parse sim params (convert to dict first)
        sim_params = {"sim": class_to_dict(env_cfg.sim)}
        sim_params = parse_sim_params(args, sim_params)
        env = task_class(
            cfg=env_cfg,
            sim_params=sim_params,
            physics_engine=args.physics_engine,
            sim_device=args.sim_device,
            headless=args.headless
        )
        # set_seed() might be used deterministically during env creation, reset it here to make execution different for different env_cfg.seed
        set_seed(env_cfg.seed)  
        return env, env_cfg

    def make_alg_runner(self, env, args, name=None, train_cfg=None, init_wandb=True, log_root="", **kwargs) -> Tuple[OnPolicyRunner, LeggedRobotCfgPPO]:
        """Creates the training algorithm either from a registered name or from the provided config file.

        Args:
            env (isaacgym.VecTaskPython): The environment to train
            args (Args, optional): Isaac Gym comand line arguments.
            name (string, optional): Name of a registered env. If None, the config file will be used instead. Defaults to None.
            train_cfg (Dict, optional): Training config file. If None 'name' will be used to get the config file. Defaults to None.
            log_root (str, optional): Logging directory for Tensorboard. Set to 'None' to avoid logging (at test time for example). 

        Raises:
            ValueError: Error if neither 'name' or 'train_cfg' are provided
            Warning: If both 'name' or 'train_cfg' are provided 'name' is ignored

        Returns:
            PPO: The created algorithm
            Dict: the corresponding config file
            string: The logging directory
            string: The directory to load the model from, if different from the logging directory
        """
        # if config files are passed use them, otherwise load from the name
        if train_cfg is None:
            if name is None:
                raise ValueError("Either 'name' or 'train_cfg' must be not None")
            # load config files
            _, train_cfg = self.get_cfgs(name)
        else:
            if name is not None:
                print(f"'train_cfg' provided -> Ignoring 'name={name}'")
        # override cfg from args (if specified)
        _, train_cfg = update_cfg_from_args(None, train_cfg, args)

        log_dir = log_root if log_root != "" else Path(LEGGED_GYM_ROOT_DIR) / "logs" / args.proj_name / args.exptid
        if log_dir is not None:
            log_dir.mkdir(parents=True, exist_ok=True)
        
        train_cfg_dict = class_to_dict(train_cfg)
        runner = OnPolicyRunner(env, 
                                train_cfg_dict, 
                                log_dir, 
                                init_wandb=init_wandb,
                                device=args.rl_device, **kwargs)

        # Resume training if specified
        resume = train_cfg.runner.resume
        load_dir = train_cfg.runner.load_run if train_cfg.runner.load_run else log_dir
        if not Path(load_dir).is_absolute():
            load_dir = Path(LEGGED_GYM_ROOT_DIR) / "logs" / args.proj_name / load_dir
        checkpoint = None
        if resume:
            # load previously trained model
            checkpoint = get_checkpoint(load_dir, checkpoint=train_cfg.runner.checkpoint)
            runner.load(os.path.join(load_dir, checkpoint))
            if not train_cfg.policy.continue_from_last_std:
                runner.alg.actor_critic.reset_std(train_cfg.policy.init_noise_std, 12, device=runner.device)

        return runner, train_cfg, log_dir, load_dir, checkpoint

# make global task registry
task_registry = TaskRegistry()
