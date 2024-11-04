import re
import os
from pathlib import Path
import logging
import pickle
import importlib.util
import numpy as np
import inspect
import shutil
import random  # This is used by set_terrain in compute_terrain_stats()

from eurekaverse.utils.misc_utils import suppress_output

with suppress_output():
    from isaacgym import terrain_utils
    from legged_gym.envs.base.legged_robot_config import LeggedRobotCfg
    from legged_gym.utils import set_seed
    from legged_gym.utils.terrain_gpt import fix_terrain, calc_direct_path_heights

file_dir = os.path.dirname(os.path.abspath(__file__))  # Location of this file
with open(Path(f"{file_dir}/../gpt/terrain_template.py")) as f:
    terrain_template = f.read()
terrain_file_dir = Path(f"{file_dir}/../../extreme-parkour/legged_gym/legged_gym/utils/set_terrains")
if not terrain_file_dir.exists():
    os.makedirs(terrain_file_dir)
# NOTE: This regex pattern assumes that everything between two "def" statements is part of a function
#       This does not always hold true if there is un-indented code between functions, but we filter these out in query_gpt()
function_pattern = r"(^def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\((.*?)\):([\S\s]+?))(?=^def|\Z)"

def get_terrain(terrain_filename):
    with open(terrain_file_dir / (terrain_filename + ".py"), "r") as f:
        return f.read()

def set_terrain(terrain_filename, terrain_code):
    with open(terrain_file_dir / (terrain_filename + ".py"), "w") as f:
        f.write(terrain_code)

def reset_terrain(terrain_filename):
    with open(terrain_file_dir / (terrain_filename + ".py"), "w") as f:
        f.write(terrain_template)

def add_terrain(terrain_filename, terrain_code, terrain_num):
    # Remove everything before function definition and replace function name
    terrain_code = terrain_code.split("\n")
    for i in range(len(terrain_code)):
        if "def set_terrain" in terrain_code[i]:
            terrain_code[i] = terrain_code[i].replace("set_terrain", f"set_terrain_{terrain_num}")
            terrain_code = "\n".join(terrain_code[i:]) + "\n"
            break
    if isinstance(terrain_code, list):
        return False

    data = get_terrain(terrain_filename)
    indent_1 = re.search(r"([ \t]*)# INSERT TERRAIN FUNCTIONS HERE", data).group(1)
    indent_2 = re.search(r"([ \t]*)# INSERT TERRAIN FUNCTION DEFINITIONS HERE", data).group(1)
    data = data.replace("# INSERT TERRAIN FUNCTIONS HERE", f"set_terrain_{terrain_num},\n{indent_1}# INSERT TERRAIN FUNCTIONS HERE")
    data = data.replace("# INSERT TERRAIN FUNCTION DEFINITIONS HERE", f"{terrain_code}\n{indent_2}# INSERT TERRAIN FUNCTION DEFINITIONS HERE")
    set_terrain(terrain_filename, data)

    return True

def setup_generated_terrains(terrain_filename, terrain_codes, use_chunking=False):
    if use_chunking:
        chunk_size = LeggedRobotCfg.terrain.num_cols
        terrain_codes = [terrain_codes[i:i+chunk_size] for i in range(0, len(terrain_codes), chunk_size)]
    else:
        terrain_codes = [terrain_codes]
    for i, terrain_chunk in enumerate(terrain_codes):
        cur_terrain_filename = f"{terrain_filename}_{i}" if use_chunking else terrain_filename
        reset_terrain(cur_terrain_filename)
        for j, terrain in enumerate(terrain_chunk):
            success = add_terrain(cur_terrain_filename, terrain, j)
            if not success:
                logging.error("Error in adding terrain to terrain file, failed to find function signature!")
    return len(terrain_codes)

def setup_generated_terrains_from_file(load_terrain_filepath, terrain_filename):
    shutil.copyfile(load_terrain_filepath, terrain_file_dir / (terrain_filename + ".py"))

def copy_terrain(terrain_filename, copy_path):
    shutil.copyfile(terrain_file_dir / (terrain_filename + ".py"), copy_path)

def extract_evaluation_strings(eval_data):
    summary_pattern = r"STATISTICS SUMMARY\n(.*?)\n\n"
    summary_string = re.search(summary_pattern, eval_data, re.DOTALL).group(1).strip()
    strings_per_terrain = {}
    terrain_type = 0
    while True:
        # Keep extracting terrain stats until no more are found
        pattern = r"STATISTICS FOR TERRAIN TYPE " + re.escape(f"{terrain_type:02}") +r"\n(.*?)\n\n"
        string = re.search(pattern, eval_data, re.DOTALL)
        if not string:
            break
        string = string.group(1).strip()
        strings_per_terrain[terrain_type] = string
        terrain_type += 1
    return summary_string, strings_per_terrain

def extract_evaluation_stats(eval_string):
    stats = {}
    for line in eval_string.split("\n"):
        key, val = line.split(":")
        key, val = key.strip(), val.strip()
        stats[key] = None if val == "None" else float(val)
    return stats

def stat_to_str(stats):
    return "\n".join([f"{key}: {val}" for key, val in stats.items()])

def get_eval_stats_from_file(eval_log_file):
    with open(eval_log_file) as f:
        eval_data = f.read()
        eval_summary_string, eval_strings_per_terrain = extract_evaluation_strings(eval_data)
        eval_summary_stats = extract_evaluation_stats(eval_summary_string)
        eval_stats_per_terrain = {terrain_type: extract_evaluation_stats(string) for terrain_type, string in eval_strings_per_terrain.items()}
    return eval_summary_stats, eval_stats_per_terrain

def load_terrain_function_from_string(string):
    local_scope = {}
    exec(string, globals(), local_scope)
    return local_scope["set_terrain"]

def load_terrain_function_from_file(filepath):
    # Copied from terrain_gpt.py
    spec = importlib.util.spec_from_file_location("module_name", filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    function = module.set_terrain
    return function

def compute_terrain_stats(terrain_fn_string):
    cfg = LeggedRobotCfg.terrain

    set_terrain = load_terrain_function_from_string(terrain_fn_string)

    env_length = cfg.terrain_length
    env_width = cfg.terrain_width
    width_per_env_pixels = int(env_width / cfg.horizontal_scale)
    length_per_env_pixels = int(env_length / cfg.horizontal_scale)

    stat_fns = {
        "Maximum": lambda arr: np.max(arr),
        "Maximum difference between consecutive indices": lambda arr: np.max(np.abs(np.diff(arr))),
        "Standard deviation": lambda arr: np.std(arr),
    }

    stats = {}
    signature = inspect.signature(set_terrain)
    args = [p.name for p in signature.parameters.values()]

    # Variation is not used for this signature, so we don't need to loop over columns
    one_terrain_type = set(args) == set(["length", "width", "field_resolution", "difficulty"])
    for j in range(cfg.num_cols if not one_terrain_type else 1):
        for i in range(cfg.num_rows):
            difficulty = i / (cfg.num_rows-1) if cfg.num_rows > 1 else 0.5
            variation = j / cfg.num_cols
            set_seed(int(variation * 1e3 + difficulty * 1e6))
            terrain = terrain_utils.SubTerrain(
                "terrain",
                width=length_per_env_pixels,
                length=width_per_env_pixels,
                vertical_scale=cfg.vertical_scale,
                horizontal_scale=cfg.horizontal_scale
            )
            terrain.goals = np.zeros((cfg.num_goals, 2))

            if set(args) == set(["terrain", "variation", "difficulty"]):
                set_idx = set_terrain(terrain, variation, difficulty)
            elif set(args) == set(["terrain", "difficulty"]):
                set_idx = set_terrain(terrain, difficulty)
            elif set(args) == set(["length", "width", "field_resolution", "difficulty"]):
                height_field, goals = set_terrain(terrain.width * terrain.horizontal_scale, terrain.length * terrain.horizontal_scale, terrain.horizontal_scale, difficulty)
                terrain.height_field_raw = (height_field / terrain.vertical_scale).astype(np.int16)
                terrain.goals = goals
                set_idx = None
            else:
                raise ValueError(f"set_terrain function signature not recognized: {args}")
            fix_terrain(terrain)
            start_location = np.array([2, (terrain.length / 2 * terrain.horizontal_scale)])
            goals = np.concatenate([start_location[None, :], terrain.goals], axis=0) / terrain.horizontal_scale
            _, heights = calc_direct_path_heights(terrain.height_field_raw, goals, skip_size=round(1 / terrain.horizontal_scale))
            heights = np.array([i for sublist in heights for i in sublist], dtype=np.float64) * terrain.vertical_scale  # Squash list, convert to meters

            # Compute statistics on heights
            if set_idx not in stats:
                stats[set_idx] = {stat_name: {} for stat_name in stat_fns.keys()}
            for stat_name, stat_fn in stat_fns.items():
                stats[set_idx][stat_name][difficulty] = stat_fn(heights)
    
    return stats

def get_terrain_stats_string(terrain_fn_string, queue=None):
    stats = compute_terrain_stats(terrain_fn_string)
    stats_string = ""
    for set_idx, stat_dict in stats.items():
        if set_idx is not None:
            stats_string += f"STATISTICS FOR TERRAIN TYPE {set_idx}\n"
        # Check that difficulties are the same for all stats
        difficulties = sorted(list(stat_dict.values())[0].keys())
        assert all([sorted(list(stat_values.keys())) == difficulties for stat_values in stat_dict.values()])
        stats_string += "(Computed on difficulties " + ", ".join([f"{difficulty:.2f}" for difficulty in difficulties]) + " respectively)\n"
        for stat_name, stat_values in stat_dict.items():
            stats_string += f"{stat_name}: " + ", ".join([f"{val:.2f}" for val in stat_values.values()]) + "\n"
    stats_string = stats_string[:-1]  # Remove last newline
    if queue:
        queue.put(stats_string)
    else:
        return stats_string

def get_terrain_descriptions(terrain_fn_string):
    docstring = re.search(r'^\s*"""([^"]*)"""\s*$', terrain_fn_string, re.MULTILINE)
    if docstring:
        return docstring.group(1)
    return None

def extract_fixed_terrains(cfg, train_log_file):
    with open(train_log_file) as f:
        train_log = f.read()
    fixed_terrains = []
    for terrain_id in range(cfg.num_terrain_types):
        if f"Automatically fixed terrain {terrain_id}" in train_log:
            fixed_terrains.append(terrain_id)
    return fixed_terrains

def get_num_total_goals():
    return LeggedRobotCfg.terrain.num_goals
