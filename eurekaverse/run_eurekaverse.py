
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
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np
import threading
import ast
import pickle
import copy

# Hide wandb output
os.environ["WANDB_SILENT"] = "True"
# Disable openai logging
httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.WARNING)

from eurekaverse.utils.terrain_utils import set_terrain, copy_terrain, setup_generated_terrains, get_eval_stats_from_file, stat_to_str, get_terrain_descriptions, extract_fixed_terrains, get_num_total_goals, get_terrain_stats_string
from eurekaverse.utils.gpt_utils import prepare_prompts, query_gpt_initial, query_gpt_evolution, log_gpt_query
from eurekaverse.utils.misc_utils import get_num_gpus, get_freest_gpu, run_subprocess, wait_subprocess, seeded

file_dir = os.path.dirname(os.path.abspath(__file__))  # Location of this file

# Parkour files for training, evaluation, and terrain setting
train_script = Path(f"{file_dir}/../extreme-parkour/legged_gym/legged_gym/scripts/train.py")
eval_script = Path(f"{file_dir}/../extreme-parkour/legged_gym/legged_gym/scripts/evaluate.py")

# Logging (will be set by hydra)
run_id = None
wandb_id = None
output_dir = None
gpt_queries_dir = None
check_execution_dir = None
renders_dir = None

# Global variables, records everything for each iteration and parallel run
parallel_run_lineage = {}                        # For each current parallel run, records the list of previous runs it resumed from

all_executable_terrains = {}                     # Saves all generated terrains, by iteration and parallel run id
flattened_all_executable_terrains = {}           # Flattened version of all_executable_terrains, used to match all-training stats to terrains
all_executable_terrains_lock = threading.Lock()  # Lock for all_executable_terrains since it's updated by multiple threads
num_chunks = 0                                   # Number of chunks all_executable_terrains was split into

eval_pre_training_stats = {}                     # (Unused)
eval_pre_training_stats_per_terrain = {}         # Used as feedback for GPT and to compute learning progress
eval_post_training_stats = {}                    # Logged
eval_post_training_stats_per_terrain = {}        # Used as feedback for GPT and to compute learning progress
eval_all_training_stats = {}                     # Used to select best run
eval_all_training_stats_per_terrain = {}         # (Unused)
eval_testing_stats = {}                          # Logged
eval_testing_stats_per_terrain = {}              # (Unused)

num_gpus = get_num_gpus()

def run_training(cfg, it, parallel_run_id, load_exptid):
    log_file = output_dir / f"train_iter-{it}_run-{parallel_run_id}.log"
    if log_file.exists():
        log_file.rename(f"{log_file}.old")
    
    gpu = get_freest_gpu() if not cfg.deterministic_gpu else f"cuda:{parallel_run_id % num_gpus}"
    command = f"python -u {train_script} --task {cfg.quadruped_model} --exptid {run_id}_{it}_{parallel_run_id} --device {gpu} --max_iterations {cfg.train_iterations} --terrain_type it-{it}_run-{parallel_run_id}"
    command = command + f" --resume --load_run {load_exptid}"
    command = command + f" --use_wandb --wandb_id {wandb_id}_{it}_{parallel_run_id} --wandb_group {run_id}" if cfg.wandb else command
    command = command + f" --render_images" if cfg.render_images else command

    process = run_subprocess(command=command, log_file=log_file)
    success, timeout = wait_subprocess(process, log_file, success_log="Starting training", failure_log="Traceback", timeout=20*60)
    if timeout:
        logging.warning(f"Timeout while training for run {parallel_run_id}!")
        process.terminate()
    if not success or timeout:
        return None, None
    return process, log_file

def run_evaluation(cfg, it, parallel_run_id, exptid, terrain):
    log_file = output_dir / f"eval_iter-{it}_run-{parallel_run_id}_{terrain}.log"
    if log_file.exists():
        log_file.rename(f"{log_file}.old")

    gpu = get_freest_gpu() if not cfg.deterministic_gpu else f"cuda:{parallel_run_id % num_gpus}"
    command = f"python -u {eval_script} --task {cfg.quadruped_model} --exptid {exptid} --device {gpu} --headless --max_steps {cfg.eval_steps} --metric_granularity type"
    if terrain == "pre_training" or terrain == "post_training":
        command = command + f" --terrain_type it-{it}_run-{parallel_run_id}"
    elif terrain == "testing":
        command = command + f" --terrain_type benchmark"
    elif terrain.startswith("all_training"):
        chunk_id = int(terrain.split("_")[-1])
        command = command + f" --terrain_type it-{it}_run-all_{chunk_id}"
    else:
        raise ValueError(f"Invalid terrain type: {terrain}")

    process = run_subprocess(command=command, log_file=log_file)
    success, timeout = wait_subprocess(process, log_file, success_log="Loading model", failure_log="Traceback", timeout=20*60)
    if timeout:
        logging.warning(f"Timeout while evaluating for run {parallel_run_id}!")
        process.terminate()
    if not success or timeout:
        return None, None
    return process, log_file

def setup_training_all_terrains(it):
    global num_chunks, flattened_all_executable_terrains
    with all_executable_terrains_lock:
        for i in range(num_chunks):
            if os.path.exists(f"{output_dir}/terrain_iter-{it}_run-all_{i}.py"):
                os.remove(f"{output_dir}/terrain_iter-{it}_run-all_{i}.py")
        terrain_filename = f"set_terrain_it-{it}_run-all"
        flattened_all_executable_terrains[it] = list(set([item for sub_dict in all_executable_terrains.values() for sub_list in sub_dict.values() for item in sub_list]))
        num_chunks = setup_generated_terrains(
            terrain_filename,
            flattened_all_executable_terrains[it],
            use_chunking=True
        )
        for i in range(num_chunks):
            copy_terrain(f"{terrain_filename}_{i}", f"{output_dir}/terrain_iter-{it}_run-all_{i}.py")

def parallel_run(cfg, it, parallel_run_id):
    """Runs training and evaluation for a parallel run."""
    global all_executable_terrains, all_executable_terrains_lock

    resume_run_id = parallel_run_lineage[parallel_run_id][-1] if it > 0 else -1

    # Set up generated terrains
    terrain_filename = f"set_terrain_it-{it}_run-{parallel_run_id}"
    setup_generated_terrains(terrain_filename, all_executable_terrains[it][parallel_run_id])
    copy_terrain(terrain_filename, f"{output_dir}/terrain_iter-{it}_run-{parallel_run_id}.py")

    # Get the exptid of the run to resume from
    load_exptid = f"{run_id}_{it-1}_{resume_run_id}" if it > 0 else "walk_pretrain"
    exptid = f"{run_id}_{it}_{parallel_run_id}"

    # Start evaluation (training terrain before training) process
    logging.info(f"> Starting {eval_script.name} subprocess (pre-training) for parallel run {parallel_run_id}...")
    eval_process, eval_pre_training_log_file = run_evaluation(cfg, it, parallel_run_id, load_exptid, terrain="pre_training")
    if eval_process is None:
        logging.warning(f"Error in evaluation (pre-training) for run {parallel_run_id}!")
        del all_executable_terrains[it][parallel_run_id]
        setup_training_all_terrains(it)
        return
    logging.info(f"Evaluation (pre-training) started for run {parallel_run_id}...")
    eval_process.communicate()

    # Start training process, wait for it to print execution success or failure (or timeout)
    logging.info(f"> Starting {train_script.name} subprocess for parallel run {parallel_run_id}...")
    train_process, train_log_file = run_training(cfg, it, parallel_run_id, load_exptid)
    if train_process is None:
        logging.warning(f"Error in training for run {parallel_run_id}!")
        del all_executable_terrains[it][parallel_run_id]
        setup_training_all_terrains(it)
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

    # Start evaluation (training terrain after training) process
    logging.info(f"> Starting {eval_script.name} subprocess (post-training) for parallel run {parallel_run_id}...")
    eval_process, eval_post_training_log_file = run_evaluation(cfg, it, parallel_run_id, exptid, terrain="post_training")
    if eval_process is None:
        logging.warning(f"Error in evaluation (post-training) for run {parallel_run_id}!")
        return
    logging.info(f"Evaluation (post-training) started for run {parallel_run_id}...")
    eval_process.communicate()

    # Start evaluation (all training terrains) process
    eval_all_training_log_files = []
    for i in range(num_chunks):
        logging.info(f"> Starting {eval_script.name} subprocess (all-training_{i}) for parallel run {parallel_run_id}...")
        eval_process, eval_all_training_log_file = run_evaluation(cfg, it, parallel_run_id, exptid, terrain=f"all_training_{i}")
        if eval_process is None:
            logging.warning(f"Error in evaluation (all-training_{i}) for run {parallel_run_id}!")
            return
        logging.info(f"Evaluation (all-training_{i}) started for run {parallel_run_id}...")
        eval_process.communicate()
        eval_all_training_log_files.append(eval_all_training_log_file)

    # Start evaluation (testing terrain) process
    logging.info(f"> Starting {eval_script.name} subprocess (testing) for parallel run {parallel_run_id}...")
    eval_process, eval_testing_log_file = run_evaluation(cfg, it, parallel_run_id, exptid, terrain="testing")
    if eval_process is None:
        logging.warning(f"Error in evaluation (testing) for run {parallel_run_id}!")
        return parallel_run_id, train_log_file, eval_pre_training_log_file, eval_post_training_log_file, eval_all_training_log_files, None
    logging.info(f"Evaluation (testing) started for run {parallel_run_id}...")
    eval_process.communicate()

    return parallel_run_id, train_log_file, eval_pre_training_log_file, eval_post_training_log_file, eval_all_training_log_files, eval_testing_log_file

def check_response(cfg, gpt_response, it, parallel_run_id, sample_id, terrain_id):
    """Checks whether gpt_response is executable."""
    save_dir = check_execution_dir / f"iter_{it}" / f"run-{parallel_run_id}"
    if not save_dir.exists():
        os.makedirs(save_dir, exist_ok=True)
    filename = f"sample-{sample_id}" if it == 0 else f"terrain-{terrain_id}_sample-{sample_id}"
    terrain_type = f"it-{it}_run-{parallel_run_id}_sample-{sample_id}" if it == 0 else f"it-{it}_run-{parallel_run_id}_terrain-{terrain_id}_response-{sample_id}"

    if "import numpy as np" not in gpt_response:
        gpt_response = "import numpy as np\n" + gpt_response
    if "import random" not in gpt_response:
        gpt_response = "import random\n" + gpt_response
    with open(f"{save_dir}/{filename}.py", "w") as f:
        f.write(gpt_response)

    # Set generated terrain, test execution
    logging.debug(f"Checking execution of generated terrain {sample_id}...")
    terrain_filename = f"set_terrain_{terrain_type}"
    set_terrain(terrain_filename, gpt_response)

    log_file = save_dir / f"{filename}.log"
    if log_file.exists():
        log_file.rename(f"{log_file}.old")
    
    gpu = get_freest_gpu(gpustat_delay=0) if not cfg.deterministic_gpu else (f"cuda:{sample_id % num_gpus}" if terrain_id == -1 else f"cuda:{terrain_id % num_gpus}")
    command = f"python -u {train_script} --task {cfg.quadruped_model} --exptid {run_id}_{it}_{parallel_run_id} --device {gpu} --max_iterations 0 --terrain_type {terrain_type} --check_terrain_feasibility"
    process = run_subprocess(command=command, log_file=log_file)
    success, timeout = wait_subprocess(process, log_file, success_log="Converting heightmap to trimesh", failure_log="Traceback", timeout=10*60)
    if timeout:
        logging.warning(f"Timeout while checking response for run {parallel_run_id}, sample {sample_id}!")
    process.terminate()
    return success, sample_id

def initial_generation(cfg, parallel_run_id):
    executable_terrains = []
    total_prompt_cost, total_response_cost = 0, 0
    for query_id in range(cfg.max_gpt_queries):
        query_messages, gpt_responses, gpt_parsed_responses, prompt_cost, response_cost = query_gpt_initial(cfg, num_samples=cfg.initial_query_sample_multiplier*cfg.num_terrain_types)
        log_gpt_query(query_messages, gpt_responses, save_dir=gpt_queries_dir / f"iter-0" / f"run-{parallel_run_id}" / f"query-{query_id}")
        total_response_cost += response_cost
        total_prompt_cost += prompt_cost

        # Parallelize over GPT responses
        sample_id_start = query_id * len(gpt_responses)
        executor = ThreadPoolExecutor(max_workers=cfg.num_parallel_checks)
        try:
            futures = []
            for i, response in enumerate(gpt_parsed_responses):
                sample_id = sample_id_start + i
                futures.append(executor.submit(check_response, cfg, response, 0, parallel_run_id, sample_id, -1))
            
            for future in as_completed(futures):
                success, sample_id = future.result()
                if success:
                    executable_terrains.append((gpt_parsed_responses[sample_id - sample_id_start], sample_id))
                    logging.info(f"Generated terrain ({len(executable_terrains)}/{cfg.num_terrain_types}) using sample {sample_id}")
                if len(executable_terrains) == cfg.num_terrain_types:
                    # Sort terrains by sample_id, then return only the terrain code
                    executable_terrains = [x[0] for x in sorted(executable_terrains, key=lambda x: x[1])]
                    return executable_terrains, total_prompt_cost, total_response_cost
        finally:
            # Stop all running checks and return immediately
            # This is also why we use ThreadPoolExecutor instead of ProcessPoolExecutor in this case
            for future in futures:
                future.cancel()
            executor.shutdown(wait=False)

def query_and_check_response(cfg, it, parallel_run_id, terrain_id, prev_executable_terrains, prev_eval_strings, all_prev_terrain_descriptions):
    for query_id in range(cfg.max_gpt_queries):
        terrain_stats = get_terrain_stats_string(prev_executable_terrains[terrain_id])
        query_messages, gpt_responses, gpt_parsed_responses, prompt_cost, response_cost = query_gpt_evolution(cfg, prev_executable_terrains[terrain_id], prev_eval_strings[terrain_id], terrain_stats, all_prev_terrain_descriptions, num_samples=cfg.evolution_query_sample_multiplier)
        log_gpt_query(query_messages, gpt_responses, save_dir=gpt_queries_dir / f"iter-{it}" / f"run-{parallel_run_id}" / f"terrain-{terrain_id}_query-{query_id}")

        sample_id_start = query_id * len(gpt_responses)
        for sample_id, response in enumerate(gpt_parsed_responses, start=sample_id_start):
            success, sample_id = check_response(cfg, response, it, parallel_run_id, sample_id, terrain_id)
            if success:
                return terrain_id, response, sample_id, prompt_cost, response_cost

def evolution_generation(cfg, it, parallel_run_id):
    # Load executable terrains, evaluation strings, and learning progress
    all_prev_executable_terrains = []
    for i, resume_run_id in enumerate(parallel_run_lineage[parallel_run_id]):
        all_prev_executable_terrains.extend(all_executable_terrains[i][resume_run_id])

    resume_run_id = parallel_run_lineage[parallel_run_id][-1]
    prev_executable_terrains = all_executable_terrains[it-1][resume_run_id]
    prev_eval_strings = []
    for terrain_id in range(cfg.num_terrain_types):
        prev_eval_strings.append("\n".join([
            "Before training:",
            stat_to_str(eval_pre_training_stats_per_terrain[it-1][resume_run_id][terrain_id]),
            "After training:",
            stat_to_str(eval_post_training_stats_per_terrain[it-1][resume_run_id][terrain_id])
        ]))

    # Parallelize over terrain types
    executable_terrains = {}
    total_prompt_cost, total_response_cost = 0, 0
    terrains_generated = 0
    with ThreadPoolExecutor(max_workers=cfg.num_parallel_checks) as executor, seeded():
        futures = []
        for terrain_id in range(cfg.num_terrain_types):
            all_prev_terrain_descriptions = [get_terrain_descriptions(terrain_fn) for terrain_fn in all_prev_executable_terrains]
            all_prev_terrain_descriptions = [desc for desc in all_prev_terrain_descriptions if desc is not None]
            futures.append(executor.submit(query_and_check_response, cfg, it, parallel_run_id, terrain_id, prev_executable_terrains, prev_eval_strings, all_prev_terrain_descriptions))

        for future in as_completed(futures):
            res = future.result()
            if res is None:
                logging.warning(f"Failed to generate executable terrain for terrain {terrain_id}!")
                return
            terrain_id, response, sample_id, prompt_cost, response_cost = res
            executable_terrains[terrain_id] = response
            total_prompt_cost += prompt_cost
            total_response_cost += response_cost
            terrains_generated += 1
            logging.info(f"Generated terrain {terrain_id} ({terrains_generated}/{cfg.num_terrain_types}) using sample {sample_id}")
    
    executable_terrains = [executable_terrains[terrain_id] for terrain_id in range(cfg.num_terrain_types)]
    return executable_terrains, total_prompt_cost, total_response_cost

def order_best_runs(cfg, stats_for_selection):
    metric_key = "Number of goals reached"
    parallel_run_stats = []
    for parallel_run_id in sorted(stats_for_selection.keys()):
        stats = stats_for_selection[parallel_run_id]
        logging.info(f"{metric_key} for parallel run {parallel_run_id} during selection: {stats[metric_key]}")
        parallel_run_stats.append((parallel_run_id, stats[metric_key]))
    parallel_run_stats = sorted(parallel_run_stats, key=lambda x: x[1], reverse=True)
    return [x[0] for x in parallel_run_stats]

def restore_run(cfg):
    global run_id, wandb_id, output_dir
    global parallel_run_lineage, all_executable_terrains, flattened_all_executable_terrains
    global eval_pre_training_stats, eval_pre_training_stats_per_terrain
    global eval_post_training_stats, eval_post_training_stats_per_terrain
    global eval_all_training_stats, eval_all_training_stats_per_terrain
    global eval_testing_stats, eval_testing_stats_per_terrain

    run_id = cfg.resume_run
    output_dir = Path(f"{output_dir}/../{cfg.resume_run}")

    logging.info(f"Resuming experiment {run_id}, make sure you're running with the same config!")

    # Get the correct wandb id to resume
    wandb_api = wandb.Api()
    runs = wandb_api.runs(path="upenn-pal/parkour", filters={"display_name": cfg.resume_run})
    assert len(runs) == 1, f"Expected 1 wandb run, got {len(runs)} called {cfg.resume_run}!"
    wandb_id = runs[0].id

    # Check output directory for saved pickle files
    load_it = -1
    for file in os.listdir(output_dir):
        match = re.search(r"parallel_run_lineage_it-(\d+)\.pkl", file)
        if match:
            load_it = max(int(match.group(1)), load_it)
    if load_it == -1:
        logging.error(f"Could not find any successful iteration in log!")
        return

    # Load previous run globals
    with open(f"{output_dir}/parallel_run_lineage_it-{load_it}.pkl", "rb") as f:
        parallel_run_lineage = pickle.load(f)
    with open(f"{output_dir}/all_executable_terrains_it-{load_it}.pkl", "rb") as f:
        all_executable_terrains = pickle.load(f)
    with open(f"{output_dir}/flattened_all_executable_terrains_it-{load_it}.pkl", "rb") as f:
        flattened_all_executable_terrains = pickle.load(f)
    with open(f"{output_dir}/eval_pre_training_stats_it-{load_it}.pkl", "rb") as f:
        eval_pre_training_stats = pickle.load(f)
    with open(f"{output_dir}/eval_pre_training_stats_per_terrain_it-{load_it}.pkl", "rb") as f:
        eval_pre_training_stats_per_terrain = pickle.load(f)
    with open(f"{output_dir}/eval_post_training_stats_it-{load_it}.pkl", "rb") as f:
        eval_post_training_stats = pickle.load(f)
    with open(f"{output_dir}/eval_post_training_stats_per_terrain_it-{load_it}.pkl", "rb") as f:
        eval_post_training_stats_per_terrain = pickle.load(f)
    with open(f"{output_dir}/eval_all_training_stats_it-{load_it}.pkl", "rb") as f:
        eval_all_training_stats = pickle.load(f)
    with open(f"{output_dir}/eval_all_training_stats_per_terrain_it-{load_it}.pkl", "rb") as f:
        eval_all_training_stats_per_terrain = pickle.load(f)
    with open(f"{output_dir}/eval_testing_stats_it-{load_it}.pkl", "rb") as f:
        eval_testing_stats = pickle.load(f)
    with open(f"{output_dir}/eval_testing_stats_per_terrain_it-{load_it}.pkl", "rb") as f:
        eval_testing_stats_per_terrain = pickle.load(f)
    
    start_it = load_it + 1
    return start_it

def save_run(it):
    with open(f"{output_dir}/parallel_run_lineage_it-{it}.pkl", "wb") as f:
        pickle.dump(parallel_run_lineage, f)
    with open(f"{output_dir}/all_executable_terrains_it-{it}.pkl", "wb") as f:
        pickle.dump(all_executable_terrains, f)
    with open(f"{output_dir}/flattened_all_executable_terrains_it-{it}.pkl", "wb") as f:
        pickle.dump(flattened_all_executable_terrains, f)
    with open(f"{output_dir}/eval_pre_training_stats_it-{it}.pkl", "wb") as f:
        pickle.dump(eval_pre_training_stats, f)
    with open(f"{output_dir}/eval_pre_training_stats_per_terrain_it-{it}.pkl", "wb") as f:
        pickle.dump(eval_pre_training_stats_per_terrain, f)
    with open(f"{output_dir}/eval_post_training_stats_it-{it}.pkl", "wb") as f:
        pickle.dump(eval_post_training_stats, f)
    with open(f"{output_dir}/eval_post_training_stats_per_terrain_it-{it}.pkl", "wb") as f:
        pickle.dump(eval_post_training_stats_per_terrain, f)
    with open(f"{output_dir}/eval_all_training_stats_it-{it}.pkl", "wb") as f:
        pickle.dump(eval_all_training_stats, f)
    with open(f"{output_dir}/eval_all_training_stats_per_terrain_it-{it}.pkl", "wb") as f:
        pickle.dump(eval_all_training_stats_per_terrain, f)
    with open(f"{output_dir}/eval_testing_stats_it-{it}.pkl", "wb") as f:
        pickle.dump(eval_testing_stats, f)
    with open(f"{output_dir}/eval_testing_stats_per_terrain_it-{it}.pkl", "wb") as f:
        pickle.dump(eval_testing_stats_per_terrain, f)

@hydra.main(config_path="config", config_name="config", version_base=None)
def main(cfg):
    global run_id, wandb_id, output_dir, gpt_queries_dir, check_execution_dir, renders_dir

    assert sum(cfg.best_run_proportions) == 1, "Best run proportions must sum to 1!"

    working_dir = Path(hydra.utils.get_original_cwd())
    output_dir = Path(os.getcwd())
    run_id = output_dir.name
    start_it = 0
    if cfg.resume_run != "":
        start_it = restore_run(cfg)
        with open("resumed_run.txt", "w") as f:
            f.write(run_id)

    gpt_queries_dir = Path(f"{output_dir}/gpt_queries")
    check_execution_dir = Path(f"{output_dir}/check_execution")
    renders_dir = Path(f"{output_dir}/train_renders")
    prepare_prompts(cfg)

    logging.info(f"Working directory: {working_dir}")
    logging.info(f"Output directory: {output_dir}")

    # Main wandb run for the entire experiment, merges best run from each generation iteration
    if cfg.wandb:
        wandb_start_step = 1000  # To account for pre-training flat
        if cfg.resume_run == "":
            wandb_id = wandb.util.generate_id()
            wandb.init(  
                project="parkour",
                name=run_id,
                group=run_id,
                dir=f"{file_dir}/../extreme-parkour/legged_gym/logs",
                id=wandb_id,
            )
            wandb.log({
                "best_run_id": 0,
                "Eval/training_mean_episode_length": 0,
                "Eval/training_mean_goals_reached": 0,
                "Eval/training_mean_edge_violation": 0,
                "Eval/training-all_mean_episode_length": 0,
                "Eval/training-all_mean_goals_reached": 0,
                "Eval/training-all_mean_edge_violation": 0,
                "Eval/testing_mean_episode_length": 0,
                "Eval/testing_mean_goals_reached": 0,
                "Eval/testing_mean_edge_violation": 0,
            }, step=wandb_start_step)
            wandb.finish(quiet=True)  # Will resume at the end
    else:
        logging.info("Wandb is disabled!")

    logging.info("Starting iterations...")
    for it in range(start_it, cfg.iterations):
        logging.info("="*10 + f" ITERATION {it:02} " + "="*10)

        all_executable_terrains[it] = {}
        eval_pre_training_stats[it] = {}
        eval_pre_training_stats_per_terrain[it] = {}
        eval_post_training_stats[it] = {}
        eval_post_training_stats_per_terrain[it] = {}
        eval_all_training_stats[it] = {}
        eval_all_training_stats_per_terrain[it] = {}
        eval_testing_stats[it] = {}
        eval_testing_stats_per_terrain[it] = {}
        if it == 0:
            for parallel_run_id in range(cfg.num_parallel_runs):
                parallel_run_lineage[parallel_run_id] = []

        # Generate terrains in parallel
        for parallel_run_id in range(cfg.num_parallel_runs):
            logging.info(f"> Starting generation for parallel run {parallel_run_id}...")
            if it == 0:
                res = initial_generation(cfg, parallel_run_id)
            else:
                res = evolution_generation(cfg, it, parallel_run_id)
            if res is None:
                logging.error(f"Failed to generate {cfg.num_terrain_types} executable terrains in {cfg.max_gpt_queries} queries!")
                continue

            executable_terrains, total_prompt_cost, total_response_cost = res
            all_executable_terrains[it][parallel_run_id] = executable_terrains
            logging.info(f"Generated {len(executable_terrains)} executable terrains for parallel run {parallel_run_id} (costs ${total_prompt_cost:.2f} prompt, ${total_response_cost:.2f} response)")

        # Start parallel runs, each serially running training and evaluation
        setup_training_all_terrains(it)
        with ThreadPoolExecutor(max_workers=cfg.num_parallel_runs) as executor:
            futures = []
            for parallel_run_id in range(cfg.num_parallel_runs):
                futures.append(executor.submit(parallel_run, cfg, it, parallel_run_id))
            for future in as_completed(futures):
                res = future.result()
                if res is None:
                    continue

                parallel_run_id, train_log_file, eval_pre_training_log_file, eval_post_training_log_file, eval_all_training_log_files, eval_testing_log_file = future.result()
                if eval_pre_training_log_file is not None:
                    summary_stats, stats_per_terrain = get_eval_stats_from_file(eval_pre_training_log_file)
                    eval_pre_training_stats[it][parallel_run_id] = summary_stats
                    eval_pre_training_stats_per_terrain[it][parallel_run_id] = stats_per_terrain
                if eval_post_training_log_file is not None:
                    summary_stats, stats_per_terrain = get_eval_stats_from_file(eval_post_training_log_file)
                    eval_post_training_stats[it][parallel_run_id] = summary_stats
                    eval_post_training_stats_per_terrain[it][parallel_run_id] = stats_per_terrain
                if eval_all_training_log_files is not None:
                    summary_stats, stats_per_terrain = {}, {}
                    assert len(eval_all_training_log_files) == num_chunks, f"Expected {num_chunks} all-training chunks, got {len(eval_all_training_log_files)}!"
                    global_terrain_id = 0
                    for i, eval_all_training_log_file in enumerate(eval_all_training_log_files):
                        cur_summary_stats, cur_stats_per_terrain = get_eval_stats_from_file(eval_all_training_log_file)
                        for key in cur_summary_stats.keys():
                            if key not in summary_stats:
                                summary_stats[key] = 0
                            summary_stats[key] += cur_summary_stats[key]
                        for terrain_id in cur_stats_per_terrain.keys():
                            stats_per_terrain[global_terrain_id] = cur_stats_per_terrain[terrain_id]
                            global_terrain_id += 1
                    for key in summary_stats.keys():
                        summary_stats[key] /= num_chunks
                    eval_all_training_stats[it][parallel_run_id] = summary_stats
                    eval_all_training_stats_per_terrain[it][parallel_run_id] = stats_per_terrain
                if eval_testing_log_file is not None:
                    summary_stats, stats_per_terrain = get_eval_stats_from_file(eval_testing_log_file)
                    eval_testing_stats[it][parallel_run_id] = summary_stats
                    eval_testing_stats_per_terrain[it][parallel_run_id] = stats_per_terrain

        # Choose best run
        best_previous_run_ids = order_best_runs(cfg, eval_all_training_stats[it])
        best_previous_run_id = best_previous_run_ids[0]
        best_previous_run_lineage = parallel_run_lineage[best_previous_run_id]
        logging.info(f"Best runs in iteration {it} in order of selection: {best_previous_run_ids}")
        logging.info(f"Best run in iteration {it} is run {best_previous_run_id} with lineage {best_previous_run_lineage}")
        if best_previous_run_id in eval_post_training_stats[it]:
            logging.info(f"Best run's training stats:\n{stat_to_str(eval_post_training_stats[it][best_previous_run_id])}")
        else:
            logging.warning(f"Best run's training stats not found!")
        if best_previous_run_id in eval_all_training_stats[it]:
            logging.info(f"Best run's training-all stats:\n{stat_to_str(eval_all_training_stats[it][best_previous_run_id])}")
        else:
            logging.warning(f"Best run's training-all stats not found!")
        if best_previous_run_id in eval_testing_stats[it]:
            logging.info(f"Best run's testing stats:\n{stat_to_str(eval_testing_stats[it][best_previous_run_id])}")
        else:
            logging.warning(f"Best run's testing stats not found!")

        # Softly select which best runs to continue in the next iteration, and update lineage
        resume_run_ids = []
        for i, proportion in enumerate(cfg.best_run_proportions):
            num_copies = int(proportion * cfg.num_parallel_runs)
            resume_run_ids.extend([best_previous_run_ids[i]] * num_copies)
        if len(resume_run_ids) < cfg.num_parallel_runs:
            num_copies = cfg.num_parallel_runs - len(resume_run_ids)
            resume_run_ids.extend([best_previous_run_ids[0]] * num_copies)
        random.shuffle(resume_run_ids)
        new_parallel_run_lineage = {}
        for parallel_run_id, resume_run_id in enumerate(resume_run_ids):
            new_parallel_run_lineage[parallel_run_id] = parallel_run_lineage[resume_run_id] + [resume_run_id]
        for parallel_run_id in range(cfg.num_parallel_runs):
            parallel_run_lineage[parallel_run_id] = new_parallel_run_lineage[parallel_run_id]
        
        # Save run
        save_run(it)

        if cfg.wandb:
            # Update each parallel run's wandb with evaluation stats
            for parallel_run_id in all_executable_terrains[it].keys():
                wandb.init(  
                    project="parkour",
                    name=f"{run_id}_{it}_{parallel_run_id}",
                    group=run_id,
                    dir=f"{file_dir}/../extreme-parkour/legged_gym/logs",
                    id=f"{wandb_id}_{it}_{parallel_run_id}",
                    resume="allow",
                )
                eval_log = {}
                if parallel_run_id in eval_post_training_stats[it]:
                    eval_log["Eval/training_mean_episode_length"] = eval_post_training_stats[it][parallel_run_id]["Episode length"]
                    eval_log["Eval/training_mean_goals_reached"] = eval_post_training_stats[it][parallel_run_id]["Number of goals reached"]
                    eval_log["Eval/training_mean_edge_violation"] = eval_post_training_stats[it][parallel_run_id]["Edge violation"]
                if parallel_run_id in eval_all_training_stats[it]:
                    eval_log["Eval/training-all_mean_episode_length"] = eval_all_training_stats[it][parallel_run_id]["Episode length"]
                    eval_log["Eval/training-all_mean_goals_reached"] = eval_all_training_stats[it][parallel_run_id]["Number of goals reached"]
                    eval_log["Eval/training-all_mean_edge_violation"] = eval_all_training_stats[it][parallel_run_id]["Edge violation"]
                if parallel_run_id in eval_testing_stats[it]:
                    eval_log["Eval/testing_mean_episode_length"] = eval_testing_stats[it][parallel_run_id]["Episode length"]
                    eval_log["Eval/testing_mean_goals_reached"] = eval_testing_stats[it][parallel_run_id]["Number of goals reached"]
                    eval_log["Eval/testing_mean_edge_violation"] = eval_testing_stats[it][parallel_run_id]["Edge violation"]
                wandb.log(eval_log, step=int(wandb_start_step + (it+1) * cfg.train_iterations))
                wandb.finish(quiet=True)

    if cfg.wandb:
        # Merge wandb logs into main run
        wandb.init(  
            project="parkour",
            name=run_id,
            group=run_id,
            dir=f"{file_dir}/../extreme-parkour/legged_gym/logs",
            id=wandb_id,
            resume="allow",
        )
        api = wandb.Api()

        for it, run_id in enumerate(best_previous_run_lineage + [best_previous_run_id]):
            cur_run = api.run(f"upenn-pal/parkour/{wandb_id}_{it}_{run_id}")
            for log in cur_run.history(samples=cfg.train_iterations, pandas=False):
                step = int(log["_step"])
                log = {key: val for key, val in log.items() if val is not None}
                if step == wandb_start_step + (it+1) * cfg.train_iterations:
                    # This is the evaluation log
                    log["best_run_id"] = run_id
                wandb.log(log, step=step)
        wandb.finish(quiet=True)

    if cfg.resume_run != "":
        cur_output_dir = Path(os.getcwd())
        cur_run_id = cur_output_dir.name
        with open(f"{cur_output_dir}/run_eurekaverse.log", "r") as f:
            data = f.read()
        with open(f"{output_dir}/run_eurekaverse.log", "a") as f:
            f.write("\n\n" + "*"*10 + f" RESUMING RUN (run by {cur_run_id}) " + "*"*10 + "\n")
            f.write(data)

if __name__ == "__main__":
    main()