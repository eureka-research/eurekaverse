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

import time
import os
from collections import deque
import statistics

import torch
import wandb

from rsl_rl.algorithms import PPO
from rsl_rl.modules import *
from rsl_rl.env import VecEnv
from copy import copy, deepcopy
import warnings

class OnPolicyRunner: 

    def __init__(self,
                 env: VecEnv,
                 train_cfg,
                 log_dir=None,
                 init_wandb=True,
                 device='cpu', **kwargs):

        self.cfg=train_cfg["runner"]
        self.alg_cfg = train_cfg["algorithm"]
        self.policy_cfg = train_cfg["policy"]
        self.estimator_cfg = train_cfg["estimator"]
        self.depth_encoder_cfg = train_cfg["depth_encoder"]
        self.device = device
        self.env = env

        print("Using MLP and Priviliged Env encoder ActorCritic structure")
        actor_critic: ActorCriticRMA = ActorCriticRMA(self.env.cfg.env.n_proprio,
                                                      self.env.cfg.env.n_scan,
                                                      self.env.num_obs,
                                                      self.env.cfg.env.n_priv_latent,
                                                      self.env.cfg.env.n_priv,
                                                      self.env.cfg.env.history_len,
                                                      self.env.num_actions,
                                                      **self.policy_cfg).to(self.device)
        estimator = Estimator(input_dim=env.cfg.env.n_proprio, output_dim=env.cfg.env.n_priv, hidden_dims=self.estimator_cfg["hidden_dims"]).to(self.device)
        # Depth encoder
        self.if_depth = self.depth_encoder_cfg["if_depth"]
        if self.if_depth:
            depth_backbone = DepthOnlyFCBackbone58x87(env.cfg.env.n_proprio, 
                                                    self.policy_cfg["scan_encoder_dims"][-1], 
                                                    self.depth_encoder_cfg["hidden_dims"],
                                                    )
            depth_encoder = RecurrentDepthBackbone(depth_backbone, env.cfg, output_yaw=self.depth_encoder_cfg["train_direction_distillation"])
            depth_encoder = depth_encoder.to(self.device)
            depth_actor = deepcopy(actor_critic.actor)
        else:
            depth_encoder = None
            depth_actor = None
        # self.depth_encoder = depth_encoder
        # self.depth_encoder_optimizer = optim.Adam(self.depth_encoder.parameters(), lr=self.depth_encoder_cfg["learning_rate"])
        # self.depth_encoder_paras = self.depth_encoder_cfg
        # self.depth_encoder_criterion = nn.MSELoss()
        # Create algorithm
        alg_class = eval(self.cfg["algorithm_class_name"]) # PPO
        self.alg: PPO = alg_class(actor_critic, 
                                  estimator, self.estimator_cfg, 
                                  depth_encoder, self.depth_encoder_cfg, depth_actor,
                                  device=self.device, **self.alg_cfg)
        self.num_steps_per_env = self.cfg["num_steps_per_env"]
        self.save_interval = self.cfg["save_interval"]
        self.dagger_update_freq = self.alg_cfg["dagger_update_freq"]

        self.alg.init_storage(
            self.env.num_envs, 
            self.num_steps_per_env, 
            [self.env.num_obs], 
            [self.env.num_privileged_obs], 
            [self.env.num_actions],
        )

        self.learn = self.learn_RL if not self.if_depth else self.learn_vision
            
        # Log
        self.log_dir = log_dir
        self.writer = None
        self.tot_timesteps = 0
        self.tot_time = 0
        self.current_learning_iteration = 0
        

    def learn_RL(self, num_learning_iterations, init_at_random_ep_len=False):
        if init_at_random_ep_len:
            self.env.episode_length_buf = torch.randint_like(self.env.episode_length_buf, high=int(self.env.max_episode_length))
        obs = self.env.get_observations()
        privileged_obs = self.env.get_privileged_observations()
        critic_obs = privileged_obs if privileged_obs is not None else obs
        obs, critic_obs = obs.to(self.device), critic_obs.to(self.device)
        self.alg.actor_critic.train() # switch to train mode (for dropout for example)

        ep_infos = []
        reward_sum_buffer = deque(maxlen=100)
        episode_len_buffer = deque(maxlen=100)
        goals_reached_buffer = deque(maxlen=100)
        cur_reward_sum = torch.zeros(self.env.num_envs, dtype=torch.float, device=self.device)
        cur_episode_length = torch.zeros(self.env.num_envs, dtype=torch.float, device=self.device)
        cur_num_goals_reached = torch.zeros(self.env.num_envs, dtype=torch.float, device=self.device)

        self.start_learning_iteration = copy(self.current_learning_iteration)
        self.end_learning_iteration = self.current_learning_iteration + num_learning_iterations

        mean_value_loss, mean_surrogate_loss, mean_estimator_loss, mean_priv_reg_loss, priv_reg_coef, mean_hist_latent_loss = 0, 0, 0, 0, 0, 0
        for it in range(self.start_learning_iteration, self.end_learning_iteration):
            self.current_learning_iteration = it
            start = time.time()
            hist_encoding = it % self.dagger_update_freq == 0

            # Rollout
            with torch.inference_mode():
                for i in range(self.num_steps_per_env):
                    actions = self.alg.act(obs, critic_obs, hist_encoding)
                    obs, privileged_obs, rewards, dones, infos = self.env.step(actions)
                    critic_obs = privileged_obs if privileged_obs is not None else obs
                    obs, critic_obs, rewards, dones = obs.to(self.device), critic_obs.to(self.device), rewards.to(self.device), dones.to(self.device)
                    self.alg.process_env_step(rewards, dones, infos)
                    
                    if self.log_dir is not None:
                        # Book keeping
                        if 'episode' in infos:
                            ep_infos.append(infos['episode'])
                        cur_reward_sum += rewards
                        cur_episode_length += 1
                        cur_num_goals_reached += infos["inc_goal"]
                        
                        # Record and reset stats for finished episodes
                        new_ids = (dones > 0).nonzero(as_tuple=False)
                        reward_sum_buffer.extend(cur_reward_sum[new_ids][:, 0].cpu().numpy().tolist())
                        episode_len_buffer.extend(cur_episode_length[new_ids][:, 0].cpu().numpy().tolist())
                        goals_reached_buffer.extend(cur_num_goals_reached[new_ids][:, 0].cpu().numpy().tolist())

                        cur_reward_sum[new_ids] = 0
                        cur_episode_length[new_ids] = 0
                        cur_num_goals_reached[new_ids] = 0

                stop = time.time()
                collection_time = stop - start

                # Learning step
                start = stop
                self.alg.compute_returns(critic_obs)
            
            mean_value_loss, mean_surrogate_loss, mean_estimator_loss, mean_priv_reg_loss, priv_reg_coef = self.alg.update()
            if hist_encoding:
                print("Updating dagger...")
                mean_hist_latent_loss = self.alg.update_dagger()
            
            stop = time.time()
            learn_time = stop - start
            if self.log_dir is not None:
                self.log(locals(), vision=False)
            if it % self.save_interval == 0:
                self.save(os.path.join(self.log_dir, 'model_{}.pt'.format(it)))
            ep_infos.clear()
        
        self.current_learning_iteration = self.end_learning_iteration
        self.save(os.path.join(self.log_dir, 'model_{}.pt'.format(self.current_learning_iteration)))

    def learn_vision(self, num_learning_iterations, init_at_random_ep_len=False):
        if init_at_random_ep_len:
            self.env.episode_length_buf = torch.randint_like(self.env.episode_length_buf, high=int(self.env.max_episode_length))

        self.start_learning_iteration = copy(self.current_learning_iteration)
        self.end_learning_iteration = self.current_learning_iteration + num_learning_iterations

        ep_infos = []
        reward_sum_buffer = deque(maxlen=100)
        episode_len_buffer = deque(maxlen=100)
        goals_reached_buffer = deque(maxlen=100)
        cur_reward_sum = torch.zeros(self.env.num_envs, dtype=torch.float, device=self.device)
        cur_episode_length = torch.zeros(self.env.num_envs, dtype=torch.float, device=self.device)
        cur_num_goals_reached = torch.zeros(self.env.num_envs, dtype=torch.float, device=self.device)

        obs = self.env.get_observations()
        infos = {
            "depth": self.env.depth_buffer.clone().to(self.device)[:, 0] if self.if_depth else None,
            "delta_yaw_ok": torch.zeros(self.env.num_envs, dtype=torch.bool, device=self.device)
        }
        self.alg.depth_encoder.train()
        self.alg.depth_actor.train()

        num_pretrain_iter = 0
        for it in range(self.start_learning_iteration, self.end_learning_iteration):
            self.current_learning_iteration = it
            start = time.time()
            depth_latent_buffer = []
            scandots_latent_buffer = []
            actions_teacher_buffer = []
            actions_student_buffer = []
            yaw_buffer_student = []
            yaw_buffer_teacher = []
            delta_yaw_ok_buffer = []
            for i in range(self.depth_encoder_cfg["num_steps_per_env"]):
                if infos["depth"] != None:
                    with torch.no_grad():
                        scandots_latent = self.alg.actor_critic.actor.infer_scandots_latent(obs)
                    scandots_latent_buffer.append(scandots_latent)
                    obs_prop_depth = obs[:, :self.env.cfg.env.n_proprio].clone()
                    obs_prop_depth[:, 5:7] = 0
                    depth_encoder_output = self.alg.depth_encoder(infos["depth"].clone(), obs_prop_depth)  # clone is crucial to avoid in-place operation
                    
                    if self.depth_encoder_cfg["train_direction_distillation"]:
                        # Last two elements are yaw
                        depth_latent = depth_encoder_output[:, :-2]
                        yaw = 1.5 * depth_encoder_output[:, -2:]
                        yaw_buffer_student.append(yaw)
                        yaw_buffer_teacher.append(obs[:, 5:7])
                    else:
                        depth_latent = depth_encoder_output
                    # depth_latent_buffer.append(depth_latent)
                
                with torch.no_grad():
                    actions_teacher = self.alg.actor_critic.act_inference(obs, hist_encoding=True, scandots_latent=None)
                    actions_teacher_buffer.append(actions_teacher)

                obs_student = obs.clone()
                delta_yaw_ok_buffer.append(torch.nonzero(infos["delta_yaw_ok"]).size(0) / infos["delta_yaw_ok"].numel())
                if self.depth_encoder_cfg["train_direction_distillation"]:
                    # delta_yaw_ok will be completely 0 if depth.use_direction_distillation is False (see LeggedRobot)
                    obs_student[infos["delta_yaw_ok"], 5:7] = yaw.detach()[infos["delta_yaw_ok"]]
                actions_student = self.alg.depth_actor(obs_student, hist_encoding=True, scandots_latent=depth_latent)
                actions_student_buffer.append(actions_student)

                # detach actions before feeding the env
                if it < num_pretrain_iter:
                    obs, privileged_obs, rewards, dones, infos = self.env.step(actions_teacher.detach())
                else:
                    obs, privileged_obs, rewards, dones, infos = self.env.step(actions_student.detach())
                critic_obs = privileged_obs if privileged_obs is not None else obs
                obs, critic_obs, rewards, dones = obs.to(self.device), critic_obs.to(self.device), rewards.to(self.device), dones.to(self.device)

                if self.log_dir is not None:
                        # Book keeping
                        if 'episode' in infos:
                            ep_infos.append(infos['episode'])
                        cur_reward_sum += rewards
                        cur_episode_length += 1
                        cur_num_goals_reached += infos["inc_goal"]
                        new_ids = (dones > 0).nonzero(as_tuple=False)
                        reward_sum_buffer.extend(cur_reward_sum[new_ids][:, 0].cpu().numpy().tolist())
                        episode_len_buffer.extend(cur_episode_length[new_ids][:, 0].cpu().numpy().tolist())
                        goals_reached_buffer.extend(cur_num_goals_reached[new_ids][:, 0].cpu().numpy().tolist())

                        cur_reward_sum[new_ids] = 0
                        cur_episode_length[new_ids] = 0
                        cur_num_goals_reached[new_ids] = 0
                
            stop = time.time()
            collection_time = stop - start
            start = stop

            delta_yaw_ok_percentage = sum(delta_yaw_ok_buffer) / len(delta_yaw_ok_buffer)
            depth_encoder_loss = 0
            # scandots_latent_buffer = torch.cat(scandots_latent_buffer, dim=0)
            # depth_latent_buffer = torch.cat(depth_latent_buffer, dim=0)

            actions_teacher_buffer = torch.cat(actions_teacher_buffer, dim=0)
            actions_student_buffer = torch.cat(actions_student_buffer, dim=0)
            if self.depth_encoder_cfg["train_direction_distillation"]:
                yaw_buffer_student = torch.cat(yaw_buffer_student, dim=0)
                yaw_buffer_teacher = torch.cat(yaw_buffer_teacher, dim=0)
                depth_actor_loss, yaw_loss = self.alg.update_depth_actor(actions_student_buffer, actions_teacher_buffer, yaw_buffer_student, yaw_buffer_teacher)
            else:
                depth_actor_loss, yaw_loss = self.alg.update_depth_actor(actions_student_buffer, actions_teacher_buffer)
            self.alg.depth_encoder.detach_hidden_states()
            stop = time.time()
            learn_time = stop - start

            if self.log_dir is not None:
                self.log(locals(), vision=True)
            if it % self.save_interval == 0:
                self.save(os.path.join(self.log_dir, 'model_{}.pt'.format(it)))
            ep_infos.clear()

        self.current_learning_iteration = self.end_learning_iteration
        self.save(os.path.join(self.log_dir, 'model_{}.pt'.format(self.current_learning_iteration)))

    def log(self, locs, vision, width=80, pad=35):
        self.tot_timesteps += self.num_steps_per_env * self.env.num_envs
        self.tot_time += locs['collection_time'] + locs['learn_time']
        iteration_time = locs['collection_time'] + locs['learn_time']

        ep_string = f''
        wandb_dict = {}
        if locs['ep_infos']:
            for key in locs['ep_infos'][0]:
                infotensor = torch.tensor([], device=self.device)
                for ep_info in locs['ep_infos']:
                    # handle scalar and zero dimensional tensor infos
                    if not isinstance(ep_info[key], torch.Tensor):
                        ep_info[key] = torch.Tensor([ep_info[key]])
                    if len(ep_info[key].shape) == 0:
                        ep_info[key] = ep_info[key].unsqueeze(0)
                    infotensor = torch.cat((infotensor, ep_info[key].to(self.device)))
                value = torch.mean(infotensor)
                wandb_dict['Episode_rew/' + key] = value
                ep_string += f"""{f'Mean episode {key}:':>{pad}} {value:.4f}\n"""
        mean_std = self.alg.actor_critic.std.mean()
        fps = int(self.num_steps_per_env * self.env.num_envs / (locs['collection_time'] + locs['learn_time']))

        if not vision:
            wandb_dict['Loss/value_function'] = locs['mean_value_loss']
            wandb_dict['Loss/surrogate'] = locs['mean_surrogate_loss']
            wandb_dict['Loss/estimator'] = locs['mean_estimator_loss']
            wandb_dict['Loss/hist_latent_loss'] = locs['mean_hist_latent_loss']
            wandb_dict['Loss/priv_reg_loss'] = locs['mean_priv_reg_loss']
            wandb_dict['Loss/priv_ref_lambda'] = locs['priv_reg_coef']
            wandb_dict['Loss/learning_rate'] = self.alg.learning_rate
        else:
            if self.depth_encoder_cfg["train_direction_distillation"]:
                wandb_dict['Loss_depth/delta_yaw_ok_percent'] = locs['delta_yaw_ok_percentage']
            wandb_dict['Loss_depth/depth_encoder'] = locs['depth_encoder_loss']
            wandb_dict['Loss_depth/depth_actor'] = locs['depth_actor_loss']
            wandb_dict['Loss_depth/yaw'] = locs['yaw_loss']

        wandb_dict['Policy/mean_noise_std'] = mean_std.item()
        wandb_dict['Perf/total_fps'] = fps
        wandb_dict['Perf/collection time'] = locs['collection_time']
        wandb_dict['Perf/learning_time'] = locs['learn_time']

        if len(locs['reward_sum_buffer']) > 0:
            wandb_dict['Train/mean_reward'] = statistics.mean(locs['reward_sum_buffer'])
        if len(locs['episode_len_buffer']) > 0:
            wandb_dict['Train/mean_episode_length'] = statistics.mean(locs['episode_len_buffer'])
        if len(locs['goals_reached_buffer']) > 0:
            wandb_dict['Train/mean_goals_reached'] = statistics.mean(locs['goals_reached_buffer'])
            wandb_dict['Train/std_goals_reached'] = statistics.stdev(locs['goals_reached_buffer'])

        wandb.log(wandb_dict, step=locs['it'])

        str = f" \033[1m Learning iteration {locs['it']}/{self.end_learning_iteration} \033[0m "

        if not vision:
            log_string = (
                f"""{'#' * width}\n"""
                f"""{str.center(width, ' ')}\n\n"""
                f"""{'Computation:':>{pad}} {fps:.0f} steps/s (collection: {locs[
                    'collection_time']:.3f}s, learning {locs['learn_time']:.3f}s)\n"""
                f"""{'Value function loss:':>{pad}} {locs['mean_value_loss']:.4f}\n"""
                f"""{'Surrogate loss:':>{pad}} {locs['mean_surrogate_loss']:.4f}\n"""
                f"""{'Mean action noise std:':>{pad}} {mean_std.item():.2f}\n"""
                f"""{'Estimator loss:':>{pad}} {locs['mean_estimator_loss']:.4f}\n"""
            )
        else:
            log_string = (
                f"""{'#' * width}\n"""
                f"""{str.center(width, ' ')}\n\n"""
                f"""{'Computation:':>{pad}} {fps:.0f} steps/s (collection: {locs[
                    'collection_time']:.3f}s, learning {locs['learn_time']:.3f}s)\n"""
                f"""{'Mean action noise std:':>{pad}} {mean_std.item():.2f}\n"""
                f"""{'Depth encoder loss:':>{pad}} {locs['depth_encoder_loss']:.4f}\n"""
                f"""{'Depth actor loss:':>{pad}} {locs['depth_actor_loss']:.4f}\n"""
                f"""{'Yaw loss:':>{pad}} {locs['yaw_loss']:.4f}\n"""
                f"""{'Delta yaw ok percentage:':>{pad}} {locs['delta_yaw_ok_percentage']:.4f}\n"""
            )
        if len(locs['reward_sum_buffer']) > 0:
            log_string += (
                f"""{'Mean reward (total):':>{pad}} {statistics.mean(locs['reward_sum_buffer']):.2f}\n"""
                f"""{'Mean episode length:':>{pad}} {statistics.mean(locs['episode_len_buffer']):.2f}\n"""
            )

        log_string += f"""{'-' * width}\n"""
        log_string += ep_string
        curr_it = locs['it'] - self.start_learning_iteration
        eta = self.tot_time / (curr_it + 1) * (locs['num_learning_iterations'] - curr_it)
        mins = eta // 60
        secs = eta % 60
        log_string += (f"""{'-' * width}\n"""
                       f"""{'Total timesteps:':>{pad}} {self.tot_timesteps}\n"""
                       f"""{'Iteration time:':>{pad}} {iteration_time:.2f}s\n"""
                       f"""{'Total time:':>{pad}} {self.tot_time:.2f}s\n"""
                       f"""{'ETA:':>{pad}} {mins:.0f} mins {secs:.1f} s\n""")
        print(log_string)

    def save(self, path, infos=None):
        state_dict = {
            'model_state_dict': self.alg.actor_critic.state_dict(),
            'estimator_state_dict': self.alg.estimator.state_dict(),
            'optimizer_state_dict': self.alg.optimizer.state_dict(),
            'iter': self.current_learning_iteration,
            'infos': infos,
            }
        if self.if_depth:
            state_dict['depth_encoder_state_dict'] = self.alg.depth_encoder.state_dict()
            state_dict['depth_actor_state_dict'] = self.alg.depth_actor.state_dict()
        torch.save(state_dict, path)

    def load(self, path, load_optimizer=True):
        print("*" * 80)
        print("Loading model from {}...".format(path))
        loaded_dict = torch.load(path, map_location=self.device)
        self.alg.actor_critic.load_state_dict(loaded_dict['model_state_dict'])
        self.alg.estimator.load_state_dict(loaded_dict['estimator_state_dict'])
        if self.if_depth:
            if 'depth_encoder_state_dict' not in loaded_dict:
                warnings.warn("'depth_encoder_state_dict' key does not exist, not loading depth encoder...")
            else:
                print("Saved depth encoder detected, loading...")
                self.alg.depth_encoder.load_state_dict(loaded_dict['depth_encoder_state_dict'])
            if 'depth_actor_state_dict' in loaded_dict:
                print("Saved depth actor detected, loading...")
                self.alg.depth_actor.load_state_dict(loaded_dict['depth_actor_state_dict'])
            else:
                print("No saved depth actor, Copying actor critic actor to depth actor...")
                self.alg.depth_actor.load_state_dict(self.alg.actor_critic.actor.state_dict())
        if load_optimizer:
            self.alg.optimizer.load_state_dict(loaded_dict['optimizer_state_dict'])
        self.current_learning_iteration = loaded_dict['iter']
        print("*" * 80)

        # Patch to fix incorrect loaded learning iteration
        filename = os.path.basename(path)
        ckpt_number = int(filename.split('_')[-1].split(".")[0])
        if ckpt_number != self.current_learning_iteration:
            print()
            print(f"Warning: Loaded learning iteration ({self.current_learning_iteration}) does not match checkpoint number ({ckpt_number}), using checkpoint number...")
            print()
            self.current_learning_iteration = ckpt_number

        return loaded_dict['infos']

    def get_inference_policy(self, device=None):
        self.alg.actor_critic.eval() # switch to evaluation mode (dropout for example)
        if device is not None:
            self.alg.actor_critic.to(device)
        return self.alg.actor_critic.act_inference
    
    def get_depth_actor_inference_policy(self, device=None):
        self.alg.depth_actor.eval() # switch to evaluation mode (dropout for example)
        if device is not None:
            self.alg.depth_actor.to(device)
        return self.alg.depth_actor
    
    def get_actor_critic(self, device=None):
        self.alg.actor_critic.eval() # switch to evaluation mode (dropout for example)
        if device is not None:
            self.alg.actor_critic.to(device)
        return self.alg.actor_critic
    
    def get_estimator_inference_policy(self, device=None):
        self.alg.estimator.eval() # switch to evaluation mode (dropout for example)
        if device is not None:
            self.alg.estimator.to(device)
        return self.alg.estimator.inference

    def get_depth_encoder_inference_policy(self, device=None):
        self.alg.depth_encoder.eval()
        if device is not None:
            self.alg.depth_encoder.to(device)
        return self.alg.depth_encoder