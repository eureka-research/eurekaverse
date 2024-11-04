
import os
import hydra
from pathlib import Path
import subprocess
import re
import logging
import shutil
import wandb
import random
import ast
from concurrent.futures import ThreadPoolExecutor, as_completed
import isaacgym  # IsaacGym must be imported before torch
import torch
import numpy as np
import threading
import ast
import pickle
from omegaconf import OmegaConf
import argparse

# Hide wandb output
os.environ["WANDB_SILENT"] = "True"
# Disable openai logging
httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.WARNING)

from eurekaverse.utils.terrain_utils import set_terrain, copy_terrain, setup_generated_terrains_from_file, get_eval_stats_from_file, stat_to_str, get_terrain_descriptions, extract_fixed_terrains, get_num_total_goals
from eurekaverse.utils.gpt_utils import prepare_prompts, query_gpt_initial, query_gpt_evolution, log_gpt_query
from eurekaverse.utils.misc_utils import get_freest_gpu, run_subprocess, wait_subprocess

file_dir = os.path.dirname(os.path.abspath(__file__))  # Location of this file

# Parkour files for training, evaluation, and terrain setting
train_script = Path(f"{file_dir}/../extreme-parkour/legged_gym/legged_gym/scripts/train.py")
eval_script = Path(f"{file_dir}/../extreme-parkour/legged_gym/legged_gym/scripts/evaluate.py")

# Logging (will be set by hydra)
run_id = None
wandb_id = None
output_dir = None
renders_dir = None
distill_suffix = None

def run_training(cfg, it, parallel_run_id, load_exptid):
    log_file = output_dir / f"train_iter-{it}_run-{parallel_run_id}.log"
    if log_file.exists():
        log_file.rename(f"{log_file}.old")
    
    gpu = get_freest_gpu()
    command = f"python -u {train_script} --task {cfg.quadruped_model} --exptid {run_id}_{it}_{parallel_run_id}_{distill_suffix} --device {gpu} --max_iterations {cfg.train_iterations} --terrain_type it-{it}_run-{parallel_run_id}"
    command = command + f" --resume --load_run {load_exptid}"
    command = command + " --use_camera --action_delay"
    command = command + f" --use_wandb --wandb_id {wandb_id}_{it}_{parallel_run_id}_{distill_suffix} --wandb_group {run_id}" if cfg.wandb else command
    command = command + f" --render_images" if cfg.render_images else command

    process = run_subprocess(command=command, log_file=log_file)
    success, timeout = wait_subprocess(process, log_file, success_log="Starting training", failure_log="Traceback", timeout=20*60)
    if timeout:
        logging.warning(f"Timeout while training for run {parallel_run_id}!")
        process.terminate()
    if not success or timeout:
        return None, None
    return process, log_file

def main(args):
    # Make logging just like Hydra
    logging.basicConfig(level=logging.INFO)
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    # Define the custom formatter that matches the Hydra style
    formatter = logging.Formatter(
        fmt='[%(asctime)s][%(name)s][%(levelname)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    # Create a stream handler
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    # Get the root logger and set the level and handler
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    global run_id, wandb_id, output_dir, renders_dir, distill_suffix

    distill_suffix = "depth-u5d1_noise-bg_action-d1.5"  # Based on setup in LeggedRobotConfig
    print(f"Distill parameters: {distill_suffix}")

    run_id = args.distill_from
    output_dir = Path(f"{file_dir}/outputs/run_eurekaverse/{args.distill_from}_{distill_suffix}")
    os.makedirs(output_dir, exist_ok=True)
    renders_dir = Path(f"{output_dir}/train_renders")

    logging.info(f"Output directory: {output_dir}")

    # Load hydra config
    load_dir = f"{file_dir}/outputs/run_eurekaverse/{args.distill_from}"
    cfg = OmegaConf.load(f"{load_dir}/.hydra/config.yaml")
    cfg.wandb = args.wandb
    cfg.train_iterations = int(cfg.train_iterations)

    # Load lineage
    last_it = cfg.iterations - 1
    with open(f"{load_dir}/parallel_run_lineage_it-{last_it}.pkl", "rb") as f:
        parallel_run_lineage = pickle.load(f)
    # Assuming the best run is the most common last run across the lineages
    last_parallel_run_ids = [lineage[-1] for lineage in parallel_run_lineage.values()]
    best_run_id = max(set(last_parallel_run_ids), key=last_parallel_run_ids.count)
    best_run_lineage = None
    for lineage in parallel_run_lineage.values():
        if lineage[-1] == best_run_id:
            best_run_lineage = lineage
            break
    assert best_run_lineage is not None, "Best run lineage not found!"

    # Main wandb run for the entire experiment, merges best run from each iteration
    if cfg.wandb:
        wandb_id = wandb.util.generate_id()
        wandb.init(  
            project="parkour",
            name=f"{run_id}_{distill_suffix}",
            group=run_id,
            dir=f"{file_dir}/../extreme-parkour/legged_gym/logs",
            id=wandb_id,
        )
        wandb.finish(quiet=True)  # Will resume at the end
    else:
        logging.info("Wandb is disabled!")

    logging.info("Starting iterations...")
    for it, parallel_run_id in enumerate(best_run_lineage):
        logging.info("="*10 + f" ITERATION {it:02} " + "="*10)

        # Set up generated terrains
        load_terrain_filename = f"{load_dir}/terrain_iter-{it}_run-{parallel_run_id}.py"
        terrain_filename = f"set_terrain_it-{it}_run-{parallel_run_id}"
        setup_generated_terrains_from_file(load_terrain_filename, terrain_filename)

        # Load the teacher in the first iteration, then continue from the previous iteration
        load_exptid = f"{run_id}_{it-1}_{best_run_lineage[it-1]}_{distill_suffix}" if it > 0 else f"{args.distill_from}_{last_it}_{best_run_id}"
        logging.info(f"> Starting {train_script.name} subprocess for parallel run {parallel_run_id}...")
        train_process, train_log_file = run_training(cfg, it, parallel_run_id, load_exptid)
        if train_process is None:
            logging.warning(f"Error in training for run {parallel_run_id}!")
            return
        logging.info(f"Training started for run {parallel_run_id}...")
        with open(train_log_file) as f:
            train_log = f.read()

        # Copy training renderings to hydra output directory, if they exist
        log_dir = re.search(r"Starting training, using log directory (.*?)\.\.\.", train_log).group(1)
        render_log_dir = Path(log_dir) / "renders"
        if render_log_dir.exists():
            shutil.copytree(render_log_dir, renders_dir / f"iter-{it}" / f"run-{parallel_run_id}")
        
        # Wait for training to complete
        train_process.communicate()

        if cfg.wandb:
            # Merge wandb logs into main run
            wandb.init(  
                project="parkour",
                name=f"{run_id}_{distill_suffix}",
                group=run_id,
                dir=f"{file_dir}/../extreme-parkour/legged_gym/logs",
                id=wandb_id,
                resume="allow",
            )
            api = wandb.Api()
            cur_run = api.run(f"upenn-pal/parkour/{wandb_id}_{it}_{parallel_run_id}_{distill_suffix}")
            for log in cur_run.history(samples=cfg.train_iterations, pandas=False):
                step = int(log["_step"])
                log = {key: val for key, val in log.items() if val is not None}
                wandb.log(log, step=step)
            wandb.finish(quiet=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("distill_from", type=str)
    parser.add_argument("--wandb", action="store_true")
    args = parser.parse_args()

    main(args)