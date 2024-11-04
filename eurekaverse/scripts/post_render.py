import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import glob
import logging
from threading import current_thread
from legged_gym import LEGGED_GYM_ROOT_DIR
import os
from omegaconf import OmegaConf
import argparse
import shutil
from pathlib import Path

from eurekaverse.utils.misc_utils import get_freest_gpu, run_subprocess,  alphanum_key

parkour_log_dir = Path(f"{LEGGED_GYM_ROOT_DIR}/logs/parkour")
eurekaverse_log_dir = Path("/home/exx/Projects/eurekaverse/eurekaverse/outputs/eurekaverse/")

def decompose_terrain_path(terrain_path):
    # Extracts eurekaverse_id, it, run from terrain_path
    path = terrain_path.split("/")
    eurekaverse_id = path[-2]
    file = path[-1]
    it = file.split("_")[-2].split("-")[1]
    parallel_run_id = file.split("_")[-1].split("-")[1][:-3]
    return eurekaverse_id, it, parallel_run_id

def render_terrain(terrain_path, terrain_rows, terrain_cols, save_everything=False):
    eurekaverse_id, it, parallel_run_id = decompose_terrain_path(terrain_path)
    thread_id = current_thread().getName().split("_")[-1]

    eurekaverse_render_dir = eurekaverse_log_dir / eurekaverse_id / "train_renders" / f"iter-{it}" / f"run-{parallel_run_id}"
    if eurekaverse_render_dir.exists():
        print(f"Rendered terrain {terrain_path} already exists in eurekaverse, skipping!")
        return

    print(f"Rendering {terrain_path}...")
    
    new_path = f"{LEGGED_GYM_ROOT_DIR}/legged_gym/utils/set_terrains/set_terrain_render_{thread_id}.py"
    shutil.copy(terrain_path, new_path)
      
    train_render_dir = Path(f"{parkour_log_dir}/{eurekaverse_id}_{it}_{parallel_run_id}/renders")
    render_command = f"python3 {LEGGED_GYM_ROOT_DIR}/legged_gym/scripts/render.py --save_dir {train_render_dir} --terrain_type render_{thread_id} --terrain_rows {terrain_rows} --terrain_cols {terrain_cols} --device {get_freest_gpu()}"
    if save_everything:
        render_command += " --save_everything"
    
    process = run_subprocess(command=render_command, log_file=None)
    _, stderr = process.communicate()
    if stderr:
        print(f"Error in render.py subprocess for {terrain_path}:")
        print(stderr.decode('utf-8'))

    if not train_render_dir.exists():
        print(f"Could not find render directory for {terrain_path}!")
        return False, None
    else:
        if eurekaverse_render_dir.exists():
            if os.path.exists(f"{eurekaverse_render_dir}.old"):
                shutil.rmtree(f"{eurekaverse_render_dir}.old")
            shutil.move(eurekaverse_render_dir, f"{eurekaverse_render_dir}.old")
        os.makedirs(eurekaverse_render_dir.parent, exist_ok=True)
        shutil.copytree(train_render_dir, eurekaverse_render_dir)
        return True, terrain_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--eurekaverse_id", type=str, required=True)
    parser.add_argument("--num_workers", type=int, default=4)
    parser.add_argument("--terrain_rows", type=int, default=10)
    parser.add_argument("--terrain_cols", type=int, default=10)
    parser.add_argument("--save_everything", action="store_true", default=False)
    args = parser.parse_args()

    terrains = sorted(glob.glob(f"../outputs/eurekaverse/{args.eurekaverse_id}/terrain_iter-[0-9]*_run-[0-9]*.py"), key=alphanum_key)

    executor = ThreadPoolExecutor(max_workers=args.num_workers)
    finished = 0
    try:
        futures = []
        for sample_id, terrain_path in enumerate(terrains):
            futures.append(executor.submit(render_terrain, terrain_path, args.terrain_rows, args.terrain_cols, args.save_everything))

        for future in as_completed(futures):
            if future.result():
                success, terrain_path = future.result()
                if success:
                    finished += 1
                    logging.info(f"Rendered {terrain_path} ({finished}/{len(terrains)})")
    finally:
        for future in futures:
            future.cancel()
        executor.shutdown(wait=False)
