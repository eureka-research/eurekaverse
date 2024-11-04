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

import os
import sys
from tqdm import tqdm
import argparse
from pathlib import Path
import numpy as np
import isaacgym
import torch
import cv2
from collections import deque
import faulthandler
from copy import deepcopy
import matplotlib.pyplot as plt
from time import time, sleep
import pickle
import copy

from legged_gym import LEGGED_GYM_ROOT_DIR
from legged_gym.envs import *
from legged_gym.utils import task_registry, add_shared_args, process_args, webviewer
from legged_gym.utils.helpers import get_checkpoint

def evaluate(args):
    if args.web:
        web_viewer = webviewer.WebViewer()
    faulthandler.enable()

    load_dir = Path(LEGGED_GYM_ROOT_DIR) / "logs" / args.proj_name / args.exptid
    if not load_dir.exists():
        print(f"Error: {load_dir} does not exist!")
        exit()

    try:
        env_cfg, train_cfg = task_registry.get_saved_cfgs(load_dir=load_dir)
        if env_cfg is None or train_cfg is None:
            print("Warning: failed to load saved config, defaulting to current config")
            env_cfg, train_cfg = task_registry.get_cfgs(name=args.task)
    except:
        # Backwards compatibility
        env_cfg = task_registry.get_saved_cfgs(load_dir=load_dir)
        _, train_cfg = task_registry.get_cfgs(name=args.task)
    
    # If number of environments is too small, increase it to fill up each grid cell (relevant for distillation)
    env_cfg.env.num_envs = max(env_cfg.env.num_envs, env_cfg.terrain.num_rows * env_cfg.terrain.num_cols)
    env_cfg.depth.camera_num_envs = env_cfg.env.num_envs
    
    # Don't resample commands during an episode
    env_cfg.commands.resampling_time = 20
    
    # Disable some domain randomization (keeping friction on)
    env_cfg.domain_rand.randomize_friction = True
    env_cfg.domain_rand.push_robots = False
    env_cfg.domain_rand.randomize_base_mass = False
    env_cfg.domain_rand.randomize_base_com = False

    # Disable the curriculum to assign robots evenly across terrain types and difficulties
    env_cfg.terrain.curriculum = False

    # If showing window, allow user to control command velocity to 0
    # This should not be used for headless evaluation since it will affect the results
    if not args.headless:
        env_cfg.commands.ranges.lin_vel_x[0] = 0
        env_cfg.commands.ranges.lin_vel_y[0] = 0

    # prepare environment
    env: LeggedRobot
    env, _ = task_registry.make_env(name=args.task, args=args, env_cfg=env_cfg)
    obs = env.get_observations()

    total_steps = args.max_steps if (args.max_steps is not None and args.max_steps > 0) else 10 * int(env.max_episode_length)

    # Buffers for metric tracking
    rew_sum_per_env = torch.zeros(env.num_envs, dtype=torch.float, device=env.device)
    rew_terms_sum_per_env = {term: torch.zeros(env.num_envs, dtype=torch.float, device=env.device) for term in env.rew_term_sums.keys()}
    len_sum_per_env = torch.zeros(env.num_envs, dtype=torch.float, device=env.device)
    goals_sum_per_env = torch.zeros(env.num_envs, dtype=torch.float, device=env.device)
    sum_counter_per_env = torch.zeros(env.num_envs, dtype=torch.float, device=env.device)
    edge_violation_sum_per_env = torch.zeros(env.num_envs, dtype=torch.float, device=env.device)

    # cur_rew_sum = torch.zeros(env.num_envs, dtype=torch.float, device=env.device)
    cur_episode_length = torch.zeros(env.num_envs, dtype=torch.float, device=env.device)
    cur_time_from_start = torch.zeros(env.num_envs, dtype=torch.float, device=env.device)

    if args.web:
        web_viewer.setup(env)

    # Set up loading config
    train_cfg.runner.resume = True
    train_cfg.runner.load_run = args.exptid
    train_cfg.runner.checkpoint = args.checkpoint

    if args.use_jit:
        policy = torch.jit.load(load_dir / "traced" / "policy_latest.jit").to(env.device)
        depth_encoder = torch.jit.load(load_dir / "traced" / "depth_latest.jit").to(env.device)
        # parkour_actor = ParkourActor(device="cuda")
        # parkour_actor.load(load_dir)
        checkpoint = "jit"
    else:
        ppo_runner, train_cfg, _, loaded_dir, checkpoint = task_registry.make_alg_runner(env=env, args=args, name=args.task, train_cfg=train_cfg, log_root=load_dir)
        assert load_dir == loaded_dir, f"Config loading directory {load_dir} is different from the runner loading directory {loaded_dir}!"
        if env.cfg.depth.use_camera:
            policy = ppo_runner.get_depth_actor_inference_policy(device=env.device)
            if env.cfg.depth.use_camera:
                depth_encoder = ppo_runner.get_depth_encoder_inference_policy(device=env.device)
        else:
            policy = ppo_runner.get_inference_policy(device=env.device)
    checkpoint_name = checkpoint.replace(".pt", "").replace("_", "-")

    actions = torch.zeros(env.num_envs, 12, device=env.device, requires_grad=False)
    if env_cfg.depth.use_camera:
        infos = {
            "depth": env.depth_buffer.clone().cuda()[:, -1]
        }
        depth_latent = None
    
    obs_replay = []
    depth_replay = []
    action_replay = []
    depth_latent_replay = []
    print(f"Running for {total_steps} steps")

    if args.replay_actions:
        saved_actions = np.load(f"{load_dir}/deployed_actions.npy")
        saved_actions = np.tile(saved_actions, (args.num_envs, 1, 1))
        saved_actions = torch.from_numpy(saved_actions).transpose(0, 1)
    
    if args.replay_depth:
        saved_depth = np.load(f"{load_dir}/deployed_depth.npy")
        saved_depth = np.tile(saved_depth, (args.num_envs, 1, 1, 1))
        saved_depth = torch.from_numpy(saved_depth).transpose(0, 1)
    
    for t in tqdm(range(total_steps)):
        if args.replay_actions:
            actions = saved_actions[t % len(saved_actions)]

        elif args.use_jit:
            # Set scandots to 0, should be estimated by Depth Encoder
            lo = env_cfg.env.n_proprio
            hi = lo + env_cfg.env.n_scan
            obs[:, lo:hi] = 0

            # Set privileged explicit to 0, should be estimated by Estimator
            lo = env_cfg.env.n_proprio + env_cfg.env.n_scan
            hi = lo + env_cfg.env.n_priv
            obs[:, lo:hi] = 0

            # Set privileged latents to 0, should be estimated by Actor's history encoder
            lo = env_cfg.env.n_proprio + env_cfg.env.n_scan + env_cfg.env.n_priv
            hi = lo + env_cfg.env.n_priv_latent
            obs[:, lo:hi] = 0

            assert env_cfg.depth.use_camera, "JIT policy is the deployment policy that uses the depth sensor"
            if infos["depth"] is not None:
                depth_replay.append(copy.deepcopy(infos["depth"][0]))
                with torch.no_grad():
                    obs_proprio = obs[:, :env_cfg.env.n_proprio].clone()
                    obs_proprio[5:7] = 0
                    depth_encoder_output = depth_encoder(infos["depth"], obs_proprio)
                    depth_latent_replay.append(copy.deepcopy(depth_encoder_output[0]))
                    if train_cfg.depth_encoder.train_direction_distillation:
                        yaw = depth_encoder_output[:, -2:]
                        depth_latent = depth_encoder_output[:, :-2]
                        if env_cfg.depth.use_direction_distillation:
                            obs[:, 5:7] = 1.5 * yaw
                    else:
                        depth_latent = depth_encoder_output

            with torch.no_grad():
                actions = policy(obs, depth_latent)

            # Save for replay
            obs_replay.append(obs[0:1])
            action_replay.append(actions[0:1])
        else:
            if env.cfg.depth.use_camera:
                if infos["depth"] is not None:
                    obs_student = obs[:, :env.cfg.env.n_proprio].clone()
                    obs_student[:, 5:7] = 0
                    with torch.no_grad():
                        depth_encoder_output = depth_encoder(infos["depth"], obs_student)
                    # depth_latent = depth_latent_and_yaw[:, :-2]
                    # if env.cfg.depth.use_direction_distillation:
                    #     yaw = depth_latent_and_yaw[:, -2:]
                    #     obs[:, 5:7] = 1.5 * yaw

                    if train_cfg.depth_encoder.train_direction_distillation:
                        yaw = depth_encoder_output[:, -2:]
                        depth_latent = depth_encoder_output[:, :-2]
                        if env_cfg.depth.use_direction_distillation:
                            obs[:, 5:7] = 1.5 * yaw
                    else:
                        depth_latent = depth_encoder_output
            else:
                depth_latent = None
            
            if hasattr(ppo_runner.alg, "depth_actor"):
                with torch.no_grad():
                    actions = ppo_runner.alg.depth_actor(obs.detach(), hist_encoding=True, scandots_latent=depth_latent)
            else:
                actions = policy(obs.detach(), hist_encoding=True, scandots_latent=depth_latent)
            
        obs, _, rews, dones, infos = env.step(actions.detach())

        if args.replay_depth and t % env_cfg.depth.update_interval == 0:
            infos["depth"] = saved_depth[(t // env_cfg.depth.update_interval) % len(saved_depth)].to(env.device)


        if args.web:
            web_viewer.render(fetch_results=True, step_graphics=True, render_all_camera_sensors=True, wait_for_page_load=True)

        lookat_id = env.lookat_id

        # Log stuff
        # cur_rew_sum += rews
        cur_rew_sums = infos["rew_sums"]
        cur_reward_term_sums = infos["rew_term_sums"]
        cur_goal_idx = infos["cur_goal_idx"]
        feet_at_edge = env.feet_at_edge.clone().float()
        cur_episode_length += 1
        cur_time_from_start += 1

        new_ids = (dones > 0).nonzero(as_tuple=False)[:, 0]
        killed_ids = ((dones > 0) & (~infos["time_outs"])).nonzero(as_tuple=False)[:, 0]

        rew_sum_per_env[new_ids] += cur_rew_sums[new_ids]
        for term in rew_terms_sum_per_env.keys():
            rew_terms_sum_per_env[term][new_ids] += cur_reward_term_sums[term][new_ids]
        len_sum_per_env[new_ids] += cur_episode_length[new_ids]
        goals_sum_per_env[new_ids] += cur_goal_idx[new_ids]
        sum_counter_per_env[new_ids] += 1
        edge_violation_sum_per_env[:] += feet_at_edge.sum(dim=1)

        # cur_rew_sum[new_ids] = 0
        cur_episode_length[new_ids] = 0
        cur_time_from_start[killed_ids] = 0

    if args.use_jit and not args.no_save:
        np.save(f'{load_dir}/action_replay.npy', torch.stack(action_replay).cpu().numpy())
        np.save(f'{load_dir}/obs_replay.npy', torch.stack(obs_replay).cpu().numpy())
        np.save(f'{load_dir}/depth_replay.npy', torch.stack(depth_replay).cpu().numpy())
        np.save(f'{load_dir}/depth_latent_replay.npy', torch.stack(depth_latent_replay).cpu().numpy())
    
    rew_sum_per_env = rew_sum_per_env.cpu()
    rew_terms_sum_per_env = {term: rew_terms_sum_per_env[term].cpu() for term in rew_terms_sum_per_env.keys()}
    len_sum_per_env = len_sum_per_env.cpu()
    goals_sum_per_env = goals_sum_per_env.cpu()
    sum_counter_per_env = sum_counter_per_env.cpu()
    edge_violation_sum_per_env = edge_violation_sum_per_env.cpu()

    terrain_cells = set(zip(env.env_class.cpu().numpy().tolist(), env.terrain_levels.cpu().numpy().tolist()))
    mean_rew_per_cell_buffer, mean_rew_terms_per_cell_buffer, mean_len_per_cell_buffer, mean_goals_per_cell_buffer, mean_edge_violation_per_cell_buffer = {}, {}, {}, {}, {}
    mean_rew_terms_per_cell_buffer = {term: {} for term in rew_terms_sum_per_env.keys()}
    sum_counter_per_env[sum_counter_per_env == 0] = 1  # Avoid division by zero
    for cell in terrain_cells:
        terrain_type, terrain_level = cell
        ids = (env.env_class == terrain_type) & (env.terrain_levels == terrain_level)
        mean_rew_per_cell_buffer[cell] = torch.sum(rew_sum_per_env[ids]) / torch.sum(sum_counter_per_env[ids])
        for term in rew_terms_sum_per_env.keys():
            mean_rew_terms_per_cell_buffer[term][cell] = torch.sum(rew_terms_sum_per_env[term][ids]) / torch.sum(sum_counter_per_env[ids])
        mean_len_per_cell_buffer[cell] = torch.sum(len_sum_per_env[ids]) / torch.sum(sum_counter_per_env[ids])
        mean_goals_per_cell_buffer[cell] = torch.sum(goals_sum_per_env[ids]) / torch.sum(sum_counter_per_env[ids])
        mean_edge_violation_per_cell_buffer[cell] = torch.sum(edge_violation_sum_per_env[ids]) / torch.sum(sum_counter_per_env[ids])
    
    if not args.no_save:
        pickle_filename = f"{load_dir}/evaluation-{env_cfg.terrain.type}_{checkpoint_name}.pkl"
        if os.path.exists(pickle_filename):
            os.rename(pickle_filename, pickle_filename + ".old")
        with open(pickle_filename, "wb") as f:
            pickle.dump({
                "mean_rew_per_cell_buffer": mean_rew_per_cell_buffer,
                "mean_rew_terms_per_cell_buffer": mean_rew_terms_per_cell_buffer,
                "mean_len_per_cell_buffer": mean_len_per_cell_buffer,
                "mean_goals_per_cell_buffer": mean_goals_per_cell_buffer,
                "mean_edge_violation_per_cell_buffer": mean_edge_violation_per_cell_buffer
            }, f)

    def aggregate_cells(means_per_cell, granularity):
        if granularity == "cell":
            return means_per_cell
        elif granularity == "type":
            means_per_type = {}
            for terrain_type in set([cell[0] for cell in means_per_cell.keys()]):
                cells_in_type = [means_per_cell[cell] for cell in means_per_cell.keys() if cell[0] == terrain_type]
                means_per_type[terrain_type] = np.mean(cells_in_type)
            return means_per_type
        elif granularity == "level":
            means_per_level = {}
            for terrain_level in set([cell[1] for cell in means_per_cell.keys()]):
                cells_in_level = [means_per_cell[cell] for cell in means_per_cell.keys() if cell[1] == terrain_level]
                means_per_level[terrain_level] = np.mean(cells_in_level)
            return means_per_level
        elif granularity == "overall":
            means_all = np.mean(list(means_per_cell.values()))
            return means_all
        else:
            raise ValueError(f"Invalid granularity {granularity}")
    
    results_str = ""
    results_str += "STATISTICS SUMMARY\n"
    rew_mean = aggregate_cells(mean_rew_per_cell_buffer, granularity="overall")
    rew_terms_mean = {term: aggregate_cells(mean_rew_terms_per_cell_buffer[term], granularity="overall") for term in mean_rew_terms_per_cell_buffer.keys()}
    len_mean = aggregate_cells(mean_len_per_cell_buffer, granularity="overall")
    goals_mean = aggregate_cells(mean_goals_per_cell_buffer, granularity="overall")
    edge_violation_mean = aggregate_cells(mean_edge_violation_per_cell_buffer, granularity="overall")
    results_str += f"Reward: {rew_mean:.2f}\n"
    for term in rew_terms_mean.keys():
        results_str += f"Reward term {term}: {rew_terms_mean[term]:.2f}\n"
    results_str += f"Episode length: {len_mean:.2f}\n"
    results_str += f"Number of goals reached: {goals_mean:.2f}\n"
    results_str += f"Edge violation: {edge_violation_mean:.2f}\n"
    results_str += "\n"
    
    granularities = [args.metric_granularity] if args.metric_granularity != "all" else ["cell", "level", "type"]
    for granularity in granularities:
        # Compute mean statistics, weighing over each terrain type and difficulty equally
        # We do this to avoid biasing the results towards harder terrains that cause more resets, which would put more entries in the buffer
        rew_mean_per = aggregate_cells(mean_rew_per_cell_buffer, granularity)
        rew_terms_mean_per = {term: aggregate_cells(mean_rew_terms_per_cell_buffer[term], granularity) for term in mean_rew_terms_per_cell_buffer.keys()}
        len_mean_per = aggregate_cells(mean_len_per_cell_buffer, granularity)
        goals_mean_per = aggregate_cells(mean_goals_per_cell_buffer, granularity)
        edge_violation_mean_per = aggregate_cells(mean_edge_violation_per_cell_buffer, granularity)
        assert rew_mean_per.keys() == len_mean_per.keys() == goals_mean_per.keys() == edge_violation_mean_per.keys(), "Mismatch in keys for statistics"


        granularity_results_str = ""
        for i in sorted(rew_mean_per.keys()):
            if granularity == "cell":
                terrain_type, terrain_level = i
                granularity_results_str += f"STATISTICS FOR TERRAIN TYPE {terrain_type:02}, LEVEL {terrain_level:02}\n"
            elif granularity == "type":
                granularity_results_str += f"STATISTICS FOR TERRAIN TYPE {i:02}\n"
            elif granularity == "level":
                granularity_results_str += f"STATISTICS FOR TERRAIN LEVEL {i:02}\n"
            granularity_results_str += f"Reward: {rew_mean_per[i]:.2f}\n"
            for term in rew_terms_mean_per.keys():
                granularity_results_str += f"Reward term {term}: {rew_terms_mean_per[term][i]:.2f}\n"
            granularity_results_str += f"Episode length: {len_mean_per[i]:.2f}\n"
            granularity_results_str += f"Number of goals reached: {goals_mean_per[i]:.2f}\n"
            granularity_results_str += f"Edge violation: {edge_violation_mean_per[i]:.2f}\n"
            granularity_results_str += "\n"

        # Print and save results
        if args.metric_granularity != "all":
            print(results_str + granularity_results_str)
        if not args.no_save:
            filepath = os.path.join(load_dir, f"evaluation-{env_cfg.terrain.type}_per-{granularity}_{checkpoint_name}.txt")
            if os.path.exists(filepath):
                os.rename(filepath, filepath + ".old")
            with open(filepath, "w", encoding='utf-8') as f:
                f.write(results_str + granularity_results_str)
    
    if "cell" in granularities:
        goals_mean_per = aggregate_cells(mean_goals_per_cell_buffer, "cell")

        num_terrains = torch.unique(env.env_class).numel()
        num_levels = torch.unique(env.terrain_levels).numel()
        per_row = min(5, num_terrains)
        fig, axs = plt.subplots(num_terrains // per_row, per_row, figsize=(24, 8))
        keys = sorted(list(goals_mean_per.keys()))
        for i in range(num_terrains):
            ax = axs[i // per_row, i % per_row] if num_terrains > per_row else (axs[i] if num_terrains > 1 else axs)
            means = [goals_mean_per[keys[i * num_levels + x]] for x in range(num_levels)]
            ax.plot(range(num_levels), means)
            ax.axhline(y=1, color='r', linestyle='--')
            ax.axhline(y=8, color='r', linestyle='--')
            ax.set_xlim(0, num_levels-1)
            ax.set_ylim(0, 8.5)
            ax.set_title(i)
        plt.tight_layout()

        if not args.no_save:
            save_filename = f"{load_dir}/evaluation-{env_cfg.terrain.type}_{checkpoint_name}.png"
            if os.path.exists(save_filename):
                os.rename(save_filename, save_filename + ".old")
            plt.savefig(save_filename)
        if args.plot_cells:
            plt.show()

if __name__ == '__main__':
    EXPORT_POLICY = False
    RECORD_FRAMES = False
    MOVE_CAMERA = False

    parser = argparse.ArgumentParser()
    add_shared_args(parser)

    parser.add_argument("--checkpoint", type=int, default=-1, help="Which model checkpoint to load. If -1, will load the last checkpoint.")
    parser.add_argument("--max_steps", type=int, help="Maximum number of evaluation steps")
    parser.add_argument("--use_jit", action="store_true", default=False, help="Load jit script when playing")
    parser.add_argument("--web", action="store_true", default=False, help="Visualize evaluation via web viewer")
    parser.add_argument("--metric_granularity", type=str, default="all", choices=["type", "level", "cell", "all"])
    parser.add_argument("--no_save", action="store_true", default=False, help="Do not save any evaluation results")
    parser.add_argument("--plot_cells", action="store_true", default=False, help="Plot evaluation results in new window")

    parser.add_argument("--replay_actions", action="store_true", default=False, help="Replay actions stored from deployment")
    parser.add_argument("--replay_depth", action="store_true", default=False, help="Replay depth stored from deployment")

    args = parser.parse_args()
    args = process_args(args)

    if not args.headless:
        env_cfg, _ = task_registry.get_cfgs(name=args.task)
        # Setting up exactly one env per terrain grid cell
        if args.terrain_rows is None:
            print("Setting terrain_rows to 1 as default")
            args.terrain_rows = 1
        if args.terrain_cols is None:
            args.terrain_cols = env_cfg.terrain.num_cols
        if args.num_envs is None:
            args.num_envs = args.terrain_rows * args.terrain_cols
    
    args.script = "evaluate"
    evaluate(args)
