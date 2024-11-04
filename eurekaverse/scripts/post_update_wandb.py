
import wandb
import os
import argparse
import re
import json
import time

from legged_gym import LEGGED_GYM_ROOT_DIR
from eurekaverse.utils.terrain_utils import extract_evaluation_strings, extract_evaluation_stats

def post_update_wandb(exptid):
    # Load eval logs
    run_dir = f"{LEGGED_GYM_ROOT_DIR}/logs/parkour/{exptid}"
    eval_logs = {}
    for file in os.listdir(run_dir):
        match = re.search(r"^evaluation-benchmark_per-type_model-(\d+).txt$", file)
        if match:
            step = int(match.group(1))
            with open(f"{run_dir}/{file}", "r") as f:
                eval_data = f.read()
                eval_testing_summary_string, _ = extract_evaluation_strings(eval_data)
                eval_testing_summary_stats = extract_evaluation_stats(eval_testing_summary_string)
                eval_logs[step] = {
                    "Eval/testing_mean_episode_length": eval_testing_summary_stats["Episode length"],
                    "Eval/testing_mean_goals_reached": eval_testing_summary_stats["Number of goals reached"],
                    "Eval/testing_mean_edge_violation": eval_testing_summary_stats["Edge violation"],
                }

    print("Extracted eval logs:")
    print(json.dumps(eval_logs, indent=4, sort_keys=True))
    input("Press enter to continue...")

    # Load wandb run
    api = wandb.Api()
    runs = api.runs(path="upenn-pal/parkour", filters={"display_name": exptid})
    assert len(runs) == 1, f"Expected 1 wandb run, got {len(runs)} called {exptid}!"
    run = runs[0]

    # Initialize new wandb run
    wandb.init(
        project="parkour",
        name=f"{exptid}_with-eval",
        dir=f"{LEGGED_GYM_ROOT_DIR}/logs",
    )

    # Log all the training logs, merged with eval logs
    cur_step = -1
    for log in run.history(samples=1000000, pandas=False):
        cur_step = log["_step"]
        if cur_step in eval_logs:
            log.update(eval_logs[cur_step])
        wandb.log(log, step=cur_step)
        time.sleep(0.01)

    # Add remaining evals that were not logged
    # This should be only the last eval
    for key in sorted(eval_logs.keys()):
        if key > cur_step:
            wandb.log(eval_logs[key], step=key)
            time.sleep(0.01)

def post_update_wandb_eurekaverse(eurekaverse_run):
    wandb.init(  
        project="parkour",
        name=f"{eurekaverse_run}_with-eval",
        group=eurekaverse_run,
        dir=f"{LEGGED_GYM_ROOT_DIR}/logs",
        resume="never"
    )
    wandb_api = wandb.Api()

    run_lineage = input("Enter run lineage (comma separated): ")
    run_lineage = [int(run_id.strip()) for run_id in run_lineage.split(",")]
    wandb_start_step = int(input("Enter starting step for wandb run: "))
    train_iterations = int(input("Enter number of training iterations per run: "))

    for it, run_id in enumerate(run_lineage):
        runs = wandb_api.runs(path="upenn-pal/parkour", filters={"display_name": f"{eurekaverse_run}_{it}_{run_id}_with-eval"})
        assert len(runs) == 1, f"Expected 1 wandb run, got {len(runs)} called {eurekaverse_run}_{it}_{run_id}_with-eval!"
        cur_run = runs[0]
        for log in cur_run.history(samples=train_iterations, pandas=False):
            step = int(log["_step"])
            if step == 0:
                # These are terrain renders
                continue
            log = {key: val for key, val in log.items() if val is not None}
            if step == wandb_start_step + (it+1) * train_iterations:
                # This is the evaluation log
                log["best_run_id"] = run_id
            wandb.log(log, step=step)
            time.sleep(0.01)
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("exptid", type=str)
    parser.add_argument("--eurekaverse", action="store_true")
    args = parser.parse_args()

    if args.eurekaverse:
        post_update_wandb_eurekaverse(args.exptid)
    else:
        post_update_wandb(args.exptid)