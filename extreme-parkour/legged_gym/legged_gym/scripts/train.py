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

import numpy as np
import os
from datetime import datetime

import isaacgym
import argparse
from legged_gym.envs import *
from legged_gym.utils import task_registry, add_shared_args, process_args
import shutil
import torch
import wandb
import subprocess
from pathlib import Path
import pickle

os.environ["WANDB_SILENT"] = "False"
file_dir = os.path.dirname(os.path.abspath(__file__))  # Location of this file

def save_file(file, log_dir):
    wandb.save(file, policy="now")
    filename = os.path.basename(file)
    if filename in os.listdir(log_dir):
        os.rename(log_dir / filename, log_dir / f"{filename}.old")
    shutil.copy(file, log_dir)

def train(args):
    wandb.init(
        project=args.proj_name,
        name=args.exptid,
        group=args.wandb_group,
        mode=("online" if args.use_wandb else "disabled"),
        dir=f"{file_dir}/../../logs",
        id=args.wandb_id,
        resume="allow"
    )

    if args.render_images:
        # To avoid affecting training, we run rendering in a separate process
        # NOTE: If rendering if done with too many environments (like that used for training), there may be unexpected errors
        #       Thus, we cannot render and train with the same simulation setup
        print("Running render.py subprocess and waiting...")
        render_log_dir = Path(LEGGED_GYM_ROOT_DIR) / "logs" / args.proj_name / args.exptid / "renders"
        if render_log_dir is not None:
            render_log_dir.mkdir(parents=True, exist_ok=True)
        render_command = f"python {file_dir}/render.py --task {args.task} --save_dir {render_log_dir} --terrain_type {args.terrain_type} --terrain_rows 1 --device {args.device}"
        process = subprocess.Popen(
            render_command.split(" "),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, env={**os.environ.copy(), "TQDM_DISABLE": "1"}
        )
        _, stderr = process.communicate()
        if stderr:
            print("Error in render.py subprocess:")
            print(stderr.decode('utf-8'))
        wandb.log({"terrain_render": wandb.Image(str(render_log_dir / "summary.png"))}, commit=False)

    env, env_cfg = task_registry.make_env(name=args.task, args=args)
    ppo_runner, train_cfg, log_dir, _, _ = task_registry.make_alg_runner(env=env, args=args, name=args.task)
    if args.render_images:
        assert log_dir == render_log_dir.parent, "Log directory mismatch between train.py and render.py"

    # Save config and important source files
    legged_robot_file = LEGGED_GYM_ROOT_DIR + "/legged_gym/envs/base/legged_robot.py"
    save_file(legged_robot_file, log_dir)
    terrain_filename = "set_terrain.py" if env_cfg.terrain.type == "default" else f"set_terrain_{env_cfg.terrain.type}.py"
    try:
        terrain_file = LEGGED_GYM_ROOT_DIR + "/legged_gym/utils/" + terrain_filename
        save_file(terrain_file, log_dir)
    except FileNotFoundError:
        terrain_file = LEGGED_GYM_ROOT_DIR + "/legged_gym/utils/set_terrains/" + terrain_filename
        save_file(terrain_file, log_dir)

    # Save config as pickle
    with open(log_dir / "legged_robot_config.pkl", "wb") as f:
        cfg = (env_cfg, train_cfg)
        pickle.dump(cfg, f)
    
    print(f"Starting training, using log directory {log_dir}...")
    ppo_runner.learn(num_learning_iterations=train_cfg.runner.max_iterations, init_at_random_ep_len=True)
    wandb.finish(quiet=True)
    print("Done training!")

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    add_shared_args(parser)

    parser.add_argument("--resume", action="store_true", default=False, help="Resume training from a checkpoint")
    parser.add_argument("--load_run", type=str, help="Name of the run to load when resuming. If unspecified, will load exptid. Overrides config file if provided.")
    parser.add_argument("--checkpoint", type=int, default=-1, help="Which model checkpoint to load. If -1, will load the last checkpoint. Overrides config file if provided.")
    parser.add_argument("--max_iterations", type=int, help="Maximum number of training iterations. Overrides config file if provided.")
    parser.add_argument("--render_images", action="store_true", default=False, help="Render the environment and save images")

    args = parser.parse_args()
    args = process_args(args)
    if not args.headless:
        print("Setting headless to True, overriding")
        args.headless = True

    args.script = "train"
    train(args)
