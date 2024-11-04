import argparse
import glob
from pathlib import Path
import subprocess
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from eurekaverse.utils.misc_utils import get_freest_gpu
from eurekaverse.utils.terrain_utils import extract_evaluation_strings, extract_evaluation_stats

from legged_gym import LEGGED_GYM_ROOT_DIR

eval_script = Path(f"{LEGGED_GYM_ROOT_DIR}/legged_gym/scripts/evaluate.py")

def evaluate_model(exptid, ckpt_iter, terrain_type="benchmark"):
    print(f"Evaluating {exptid} at checkpoint {ckpt_iter}...")
    evaluate_command = f"python3 -u {eval_script} --max_steps 10000 --exptid {exptid} --device {get_freest_gpu()} --headless --checkpoint {ckpt_iter} --terrain_type {terrain_type}"
    process = subprocess.Popen(
        evaluate_command.split(" "),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, env={**os.environ.copy(), "TQDM_DISABLE": "1"}
    )
    stdout, stderr = process.communicate()
    if stderr:
        print(stderr)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--exptid", type=str, required=True)
    parser.add_argument("--ckpt_interval", type=int, default=1000)
    parser.add_argument("--max_workers", type=int, default=1)
    parser.add_argument("--terrain_type", type=str, default="benchmark")
    args = parser.parse_args()

    load_dir = f"{LEGGED_GYM_ROOT_DIR}/logs/parkour/{args.exptid}"
    checkpoint_files = glob.glob(f"{load_dir}/model_*.pt")
    ckpt_iters = []
    for filename in checkpoint_files:
        ckpt_iter = int(filename.split("_")[-1][:-3])
        if ckpt_iter % args.ckpt_interval == 0:
            ckpt_iters.append(ckpt_iter)
    ckpt_iters = sorted(ckpt_iters)
    
    summary_dicts = {}
    with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        futures = []
        for i, ckpt_iter in enumerate(ckpt_iters):
            futures.append(executor.submit(evaluate_model, args.exptid, ckpt_iter, args.terrain_type))
        for future in as_completed(futures):
            res = future.result()