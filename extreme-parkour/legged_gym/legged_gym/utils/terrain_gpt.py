import os
import numpy as np
import random
from isaacgym import terrain_utils
from legged_gym.envs.base.legged_robot_config import LeggedRobotCfg
from pydelatin import Delatin
import pyfqmr
from scipy.ndimage import binary_dilation
import inspect
import importlib.util
from legged_gym.utils.helpers import set_seed

# This is the standard set_terrain
from legged_gym import LEGGED_GYM_ROOT_DIR
from legged_gym.utils.set_terrain import set_terrain as set_terrain
from legged_gym.utils.set_terrain_benchmark import set_terrain as set_terrain_benchmark
from legged_gym.utils.set_terrain_original import set_terrain as set_terrain_original
from legged_gym.utils.set_terrain_original_distill import set_terrain as set_terrain_original_distill
from legged_gym.utils.set_terrain_simple import set_terrain as set_terrain_simple
from legged_gym.utils.set_terrain_random import set_terrain as set_terrain_random

# Override default set_terrain.py with a custom path
set_terrain_override = None

def load_terrain_function_from_file(filepath):
    spec = importlib.util.spec_from_file_location("module_name", filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    function = module.set_terrain
    return function

def run_ambiguous_set_terrain(set_terrain_fn, terrain, variation, difficulty):
    signature = inspect.signature(set_terrain_fn)
    args = [p.name for p in signature.parameters.values()]
    if set(args) == set(["terrain", "variation", "difficulty"]):
        set_idx = set_terrain_fn(terrain, variation, difficulty)
    elif set(args) == set(["terrain", "difficulty"]):
        set_idx = set_terrain_fn(terrain, difficulty)
    elif set(args) == set(["length", "width", "field_resolution", "difficulty"]):
        height_field, goals = set_terrain_fn(terrain.width * terrain.horizontal_scale, terrain.length * terrain.horizontal_scale, terrain.horizontal_scale, difficulty)
        terrain.height_field_raw = (height_field / terrain.vertical_scale).astype(np.int16)
        terrain.goals = goals
        set_idx = None
    else:
        raise ValueError(f"set_terrain function signature not recognized: {args}")
    return set_idx

class Terrain:
    def __init__(self, cfg: LeggedRobotCfg.terrain, num_robots) -> None:
        self.cfg = cfg
        self.num_robots = num_robots
        self.type = cfg.mesh_type
        if self.type in ["none", 'plane']:
            return
        self.env_length = cfg.terrain_length
        self.env_width = cfg.terrain_width

        # cfg.terrain_proportions = np.array(cfg.terrain_proportions) / np.sum(cfg.terrain_proportions)
        # self.proportions = [np.sum(cfg.terrain_proportions[:i+1]) for i in range(len(cfg.terrain_proportions))]
        self.cfg.num_sub_terrains = cfg.num_rows * cfg.num_cols
        self.env_origins = np.zeros((cfg.num_rows, cfg.num_cols, 3))
        self.terrain_type = np.zeros((cfg.num_rows, cfg.num_cols), dtype=np.int64)
        cfg.num_goals = 8
        self.goals = np.zeros((cfg.num_rows, cfg.num_cols, cfg.num_goals, 3))
        # self.num_goals = cfg.num_goals

        self.width_per_env_pixels = int(self.env_width / cfg.horizontal_scale)
        self.length_per_env_pixels = int(self.env_length / cfg.horizontal_scale)

        self.border = int(cfg.border_size/self.cfg.horizontal_scale)
        self.tot_cols = int(cfg.num_cols * self.width_per_env_pixels) + 2 * self.border
        self.tot_rows = int(cfg.num_rows * self.length_per_env_pixels) + 2 * self.border

        self.height_field_raw = np.zeros((self.tot_rows, self.tot_cols), dtype=np.int16)

        if set_terrain_override is not None and self.cfg.type == "default":
            print(f"Warning: Using set_terrain override, getting terrain from {set_terrain_override}")
        for j in range(self.cfg.num_cols):
            for i in range(self.cfg.num_rows):
                difficulty = i / (self.cfg.num_rows-1) if self.cfg.num_rows > 1 else 0.5
                variation = j / self.cfg.num_cols
                terrain = self.make_terrain(variation, difficulty)

                # Pad borders
                pad_width = int(0.1 // terrain.horizontal_scale)
                pad_height = int(0.5 // terrain.vertical_scale)
                terrain.height_field_raw[:, :pad_width] = pad_height
                terrain.height_field_raw[:, -pad_width:] = pad_height
                terrain.height_field_raw[:pad_width, :] = pad_height
                terrain.height_field_raw[-pad_width:, :] = pad_height

                self.add_terrain_to_map(terrain, i, j)
        
        self.heightsamples = self.height_field_raw
        if self.type=="trimesh":
            print("Converting heightmap to trimesh...")
            if cfg.hf2mesh_method == "grid":
                self.vertices, self.triangles, self.x_edge_mask = convert_heightfield_to_trimesh(   self.height_field_raw,
                                                                                                self.cfg.horizontal_scale,
                                                                                                self.cfg.vertical_scale,
                                                                                                self.cfg.slope_treshold)
                half_edge_width = int(self.cfg.edge_width_thresh / self.cfg.horizontal_scale)
                structure = np.ones((half_edge_width*2+1, 1))
                self.x_edge_mask = binary_dilation(self.x_edge_mask, structure=structure)
                if self.cfg.simplify_grid:
                    mesh_simplifier = pyfqmr.Simplify()
                    mesh_simplifier.setMesh(self.vertices, self.triangles)
                    mesh_simplifier.simplify_mesh(target_count = int(0.05*self.triangles.shape[0]), aggressiveness=7, preserve_border=True, verbose=10)

                    self.vertices, self.triangles, normals = mesh_simplifier.getMesh()
                    self.vertices = self.vertices.astype(np.float32)
                    self.triangles = self.triangles.astype(np.uint32)
            else:
                assert cfg.hf2mesh_method == "fast", "Height field to mesh method must be grid or fast"
                self.vertices, self.triangles = convert_heightfield_to_trimesh_delatin(self.height_field_raw, self.cfg.horizontal_scale, self.cfg.vertical_scale, max_error=cfg.max_error)
            print("Created {} vertices".format(self.vertices.shape[0]))
            print("Created {} triangles".format(self.triangles.shape[0]))

    def make_terrain(self, variation, difficulty):
        # Make terrain generation deterministic
        # NOTE: The seed will be reset back to env_cfg.seed after the environment is created, inside TaskRegistry.make_env()
        set_seed(int(variation * 1e3 + difficulty * 1e6))
        # NOTE: Width and length are swapped in the terrain_utils.SubTerrain, careful!
        terrain = terrain_utils.SubTerrain(
            "terrain",
            width=self.length_per_env_pixels,
            length=self.width_per_env_pixels,
            vertical_scale=self.cfg.vertical_scale,
            horizontal_scale=self.cfg.horizontal_scale
        )
        terrain.goals = np.zeros((self.cfg.num_goals, 2))

        fix_desc = ""
        if self.cfg.type == "default":
            if set_terrain_override is not None:
                set_terrain_fn = load_terrain_function_from_file(set_terrain_override)
            else:
                set_terrain_fn = set_terrain
            set_idx = run_ambiguous_set_terrain(set_terrain_fn, terrain, variation, difficulty)
            fix_desc = fix_terrain(terrain)
            if self.cfg.check_feasibility:
                check_terrain_feasibility(terrain, allow_flat_terrain=(difficulty == 0))
        elif self.cfg.type == "benchmark":
            set_idx = set_terrain_benchmark(terrain, variation, difficulty)
        elif self.cfg.type == "original":
            set_idx = set_terrain_original(terrain, variation, difficulty)
        elif self.cfg.type == "original_distill":
            set_idx = set_terrain_original_distill(terrain, variation, difficulty)
        elif self.cfg.type == "simple":
            set_idx = set_terrain_simple(terrain, variation, difficulty)
        elif self.cfg.type == "random":
            set_idx = set_terrain_random(terrain, variation, difficulty)
        else:
            filepath = f"{LEGGED_GYM_ROOT_DIR}/legged_gym/utils/set_terrains/set_terrain_{self.cfg.type}.py"
            if not os.path.exists(filepath):
                raise ValueError(f"Terrain type {self.cfg.type} not recognized!")
            set_terrain_fn = load_terrain_function_from_file(filepath)
            set_idx = run_ambiguous_set_terrain(set_terrain_fn, terrain, variation, difficulty)
            fix_desc = fix_terrain(terrain)
            if self.cfg.check_feasibility:
                check_terrain_feasibility(terrain, allow_flat_terrain=(difficulty == 0))
        terrain.idx = set_idx if set_idx is not None else 0
        if fix_desc != "":
            print(f"Automatically fixed terrain {terrain.idx}: {fix_desc}")

        # Add roughness to terrain
        max_height = (self.cfg.height[1] - self.cfg.height[0]) * 0.5 + self.cfg.height[0]
        height = random.uniform(self.cfg.height[0], max_height)
        terrain_utils.random_uniform_terrain(terrain, min_height=-height, max_height=height, step=0.005, downsampled_scale=self.cfg.downsampled_scale)

        return terrain

    def add_terrain_to_map(self, terrain, row, col):
        i = row
        j = col
        # map coordinate system
        start_x = self.border + i * self.length_per_env_pixels
        end_x = self.border + (i + 1) * self.length_per_env_pixels
        start_y = self.border + j * self.width_per_env_pixels
        end_y = self.border + (j + 1) * self.width_per_env_pixels
        self.height_field_raw[start_x: end_x, start_y:end_y] = terrain.height_field_raw

        env_origin_x = i * self.env_length + 1.0
        env_origin_y = (j + 0.5) * self.env_width
        x1 = int((1.0 - 0.5) / terrain.horizontal_scale) # within 1 meter square range
        x2 = int((1.0 + 0.5) / terrain.horizontal_scale)
        y1 = int((self.env_width/2 - 0.5) / terrain.horizontal_scale)
        y2 = int((self.env_width/2 + 0.5) / terrain.horizontal_scale)
        if self.cfg.origin_zero_z:
            env_origin_z = 0
        else:
            env_origin_z = np.max(terrain.height_field_raw[x1:x2, y1:y2])*terrain.vertical_scale
        self.env_origins[i, j] = [env_origin_x, env_origin_y, env_origin_z]
        self.terrain_type[i, j] = terrain.idx
        self.goals[i, j, :, :2] = terrain.goals + [i * self.env_length, j * self.env_width]
    
def fix_terrain(terrain):
    """Fix common errors with GPT-generated terrains"""
    # If goals are in units (indices), convert to meters
    # This doesn't count as a fix since we prompt GPT to return goals in units (for simplicity)
    env_length, env_width = terrain.width * terrain.horizontal_scale, terrain.length * terrain.horizontal_scale
    if np.max(terrain.goals[:, 0]) > env_length or np.max(terrain.goals[:, 1]) > env_width:
        terrain.goals = terrain.goals.astype(np.float64) * terrain.horizontal_scale
    
    fix_descs = set()

    min_terrain_height = np.min(terrain.height_field_raw)
    if min_terrain_height < round(-1 / terrain.vertical_scale):
        terrain.height_field_raw[terrain.height_field_raw < -1] = round(-1 / terrain.vertical_scale)
        fix_descs.add(f"min terrain height {min_terrain_height} is below -1")

    # Fix goals that are unset or out of bounds
    def valid_goal(goal):
        return 0 < goal[0] < env_length and 0 < goal[1] < env_width  # We check > 0 since (0, 0) is the default
    num_goals_fixed = 0
    for i in range(1, len(terrain.goals)):
        if not valid_goal(terrain.goals[i]) and valid_goal(terrain.goals[i-1]):
            terrain.goals[i] = terrain.goals[i-1]
            num_goals_fixed += 1
    for i in range(len(terrain.goals) - 2, -1, -1):
        if not valid_goal(terrain.goals[i]) and valid_goal(terrain.goals[i+1]):
            terrain.goals[i] = terrain.goals[i+1]
            num_goals_fixed += 1
    if num_goals_fixed > 0:
        fix_descs.add(f"{num_goals_fixed} goal(s) out of bounds")
    assert num_goals_fixed <= round(len(terrain.goals) / 2), f'Fixed too many goals ({num_goals_fixed})!'
    for i in range(len(terrain.goals)):
        assert valid_goal(terrain.goals[i]), f'Goal {i} at ({terrain.goals[i, 0]}, {terrain.goals[i, 1]}) is invalid!'

    # Move goals away from edge
    clipped_goals_x = np.clip(terrain.goals[:, 0], a_min=0.5, a_max=(env_length - 0.5))
    clipped_goals_y = np.clip(terrain.goals[:, 1], a_min=0.5, a_max=(env_width - 0.5))
    if not np.allclose(clipped_goals_x, terrain.goals[:, 0]) or not np.allclose(clipped_goals_y, terrain.goals[:, 1]):
        fix_descs.add("goals too close to edge")
    terrain.goals[:, 0] = clipped_goals_x
    terrain.goals[:, 1] = clipped_goals_y

    # Check and fix quadruped's spawn location
    if np.max(terrain.height_field_raw[:round(2 / terrain.horizontal_scale), :]) > 0:
        terrain.height_field_raw[:round(2 / terrain.horizontal_scale), :] = 0
        fix_descs.add("spawn area not 0")
    clipped_goals_x = np.clip(terrain.goals[:, 0], a_min=1.5, a_max=None)  # Move goals ahead of spawn
    if not np.allclose(clipped_goals_x, terrain.goals[:, 0]):
        fix_descs.add("goals too close to spawn")
    terrain.goals[:, 0] = clipped_goals_x

    # Check and fix small obstacles that have an extreme aspect ratio
    # This only works for axis-aligned obstacles, but the mistake is rare enough to not warrant a more complex fix
    min_terrain_height = np.min(terrain.height_field_raw)
    valid_ratio_threshold = 2
    min_obstacle_length, min_obstacle_width = 0.6 / terrain.horizontal_scale, 0.4 / terrain.horizontal_scale
    floodfill_dz_threshold = 1 / terrain.vertical_scale
    obstacles = {}
    floodfill = np.zeros_like(terrain.height_field_raw)

    def bfs(x, y, id):
        q = [(x, y)]
        while len(q) > 0:
            x, y = q.pop(0)
            if floodfill[x, y] != 0:
                continue
            floodfill[x, y] = id
            obstacles[id] = [
                (min(obstacles[id][0][0], x), min(obstacles[id][0][1], y)),
                (max(obstacles[id][1][0], x+1), max(obstacles[id][1][1], y+1))
            ]
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < terrain.height_field_raw.shape[0] and 0 <= ny < terrain.height_field_raw.shape[1]:
                    if terrain.height_field_raw[nx, ny] != min_terrain_height and floodfill[nx, ny] == 0 and abs(terrain.height_field_raw[nx, ny] - terrain.height_field_raw[x, y]) < floodfill_dz_threshold:
                        q.append((nx, ny))
    obstacle_counter = 0
    for i in range(terrain.height_field_raw.shape[0]):
        for j in range(terrain.height_field_raw.shape[1]):
            if terrain.height_field_raw[i, j] != min_terrain_height and floodfill[i, j] == 0:
                obstacle_counter += 1
                obstacles[obstacle_counter] = [(i, j), (i, j)]
                bfs(i, j, obstacle_counter)
    
    for obstacle in obstacles:
        x1, y1 = obstacles[obstacle][0]
        x2, y2 = obstacles[obstacle][1]
        obstacle_length, obstacle_width = x2 - x1, y2 - y1
        if max(obstacle_length, obstacle_width) / min(obstacle_width, obstacle_length) < valid_ratio_threshold:
            continue
        
        if obstacle_length < min_obstacle_length and obstacle_width < min_obstacle_width:
            # Erase small obstacles
            terrain.height_field_raw[x1:x2, y1:y2] = 0
            fix_descs.add("obstacles length and width too small (erased)")
        if obstacle_length < min_obstacle_length:
            # Extend length on both sides
            extend_length = max(round((min_obstacle_length - obstacle_length) // 2), 1)
            nx1, nx2 = max(0, x1 - extend_length), min(terrain.height_field_raw.shape[0], x2 + extend_length)
            terrain.height_field_raw[nx1:x1, y1:y2] = terrain.height_field_raw[x1, y1:y2][None, :]
            terrain.height_field_raw[x2:nx2, y1:y2] = terrain.height_field_raw[x2-1, y1:y2][None, :]
            fix_descs.add("obstacles length too small")
        if obstacle_width < min_obstacle_width:
            # Extend width on both sides
            extend_width = max(round((min_obstacle_width - obstacle_width) // 2), 1)
            ny1, ny2 = max(0, y1 - extend_width), min(terrain.height_field_raw.shape[1], y2 + extend_width)
            terrain.height_field_raw[x1:x2, ny1:y1] = terrain.height_field_raw[x1:x2, y1][..., None]
            terrain.height_field_raw[x1:x2, y2:ny2] = terrain.height_field_raw[x1:x2, y2-1][..., None]
            fix_descs.add("obstacles width too small")
    
    return ", ".join(fix_descs)

def calc_direct_path_heights(height_field_raw, goals, skip_size):
    """Runs Bresenham's line algorithm to check heights along direct path between goals."""
    # NOTE: goals is in indices, not meters

    all_line_heights = []
    all_skip_line_heights = []
    for i in range(len(goals) - 1):
        (goal_x, goal_y), (next_goal_x, next_goal_y) = goals[i], goals[i + 1]
        goal_x, goal_y, next_goal_x, next_goal_y = round(goal_x), round(goal_y), round(next_goal_x), round(next_goal_y)

        dx, dy = abs(next_goal_x - goal_x), abs(next_goal_y - goal_y)
        sx, sy = 1 if goal_x < next_goal_x else -1, 1 if goal_y < next_goal_y else -1
        err = dx - dy

        # Extract height along the line
        x, y = goal_x, goal_y
        line_heights = [height_field_raw[x, y]]
        while x != next_goal_x or y != next_goal_y:
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
            line_heights.append(height_field_raw[x, y])
        all_line_heights.append(line_heights)
        
        # Check max height difference in line_heights
        # We must also account for gap obstacles: a large height difference is
        # allowed if there is a platform with smaller height difference right after
        j = 0
        skip_line_heights = []
        while j < len(line_heights) - 1:
            skip_line_heights.append(line_heights[j])
            k = min(j + skip_size + 1, len(line_heights))
            diff_along_range = line_heights[j+1:k] - line_heights[j]      # Difference between jump destinations (i+1:j) and jump origin (i)
            diff_along_range = np.maximum.accumulate(diff_along_range)    # Every point is at least as high as the points before
                                                                          # This fills up gap unless it starts at i+1, and it also prevents edge cases with walls
            diff_along_range = np.abs(diff_along_range)
            min_diff_idx = np.argmin(diff_along_range)                    # Find optimal jump destination
            j += min_diff_idx + 1                                         # Move to next jump destination
        skip_line_heights.append(line_heights[-1])
        all_skip_line_heights.append(skip_line_heights)

    return all_line_heights, all_skip_line_heights  # First list is for all line heights, second list is with considering skips

def check_terrain_feasibility(terrain, allow_flat_terrain=False):
    max_terrain_height = np.max(terrain.height_field_raw)
    assert max_terrain_height <= round(3 / terrain.vertical_scale), f'Generated terrain with maximum height {max_terrain_height} exceeds height bound!'
    start_location = np.array([2, (terrain.length / 2 * terrain.horizontal_scale)])
    goals = np.concatenate([start_location[None, :], terrain.goals], axis=0) / terrain.horizontal_scale
    _, heights = calc_direct_path_heights(terrain.height_field_raw, goals, skip_size=round(1 / terrain.horizontal_scale))
    heights = [i for sublist in heights for i in sublist]
    diff_along_path = np.max(np.abs(np.diff(heights)))
    assert diff_along_path <= round(0.8 / terrain.vertical_scale), f'Generated terrain has maximum height difference of {diff_along_path} along direct path, not feasible!'
    if not allow_flat_terrain:
        assert diff_along_path > 0, 'Generated terrain has no height difference along direct path, no challenge!'


def convert_heightfield_to_trimesh_delatin(height_field_raw, horizontal_scale, vertical_scale, max_error=0.01):
    mesh = Delatin(np.flip(height_field_raw, axis=1).T, z_scale=vertical_scale, max_error=max_error)
    vertices = np.zeros_like(mesh.vertices)
    vertices[:, :2] = mesh.vertices[:, :2] * horizontal_scale
    vertices[:, 2] = mesh.vertices[:, 2]
    return vertices, mesh.triangles

def convert_heightfield_to_trimesh(height_field_raw, horizontal_scale, vertical_scale, slope_threshold=None):
    # Modified from isaacgym.terrain_utils.convert_heightfield_to_trimesh to also return x_edge_mask

    hf = height_field_raw
    num_rows = hf.shape[0]
    num_cols = hf.shape[1]

    y = np.linspace(0, (num_cols-1)*horizontal_scale, num_cols)
    x = np.linspace(0, (num_rows-1)*horizontal_scale, num_rows)
    yy, xx = np.meshgrid(y, x)

    if slope_threshold is not None:
        slope_threshold *= horizontal_scale / vertical_scale
        move_x = np.zeros((num_rows, num_cols))
        move_y = np.zeros((num_rows, num_cols))
        move_corners = np.zeros((num_rows, num_cols))
        move_x[:num_rows-1, :] += (hf[1:num_rows, :] - hf[:num_rows-1, :] > slope_threshold)
        move_x[1:num_rows, :] -= (hf[:num_rows-1, :] - hf[1:num_rows, :] > slope_threshold)
        move_y[:, :num_cols-1] += (hf[:, 1:num_cols] - hf[:, :num_cols-1] > slope_threshold)
        move_y[:, 1:num_cols] -= (hf[:, :num_cols-1] - hf[:, 1:num_cols] > slope_threshold)
        move_corners[:num_rows-1, :num_cols-1] += (hf[1:num_rows, 1:num_cols] - hf[:num_rows-1, :num_cols-1] > slope_threshold)
        move_corners[1:num_rows, 1:num_cols] -= (hf[:num_rows-1, :num_cols-1] - hf[1:num_rows, 1:num_cols] > slope_threshold)
        xx += (move_x + move_corners*(move_x == 0)) * horizontal_scale
        yy += (move_y + move_corners*(move_y == 0)) * horizontal_scale

    vertices = np.zeros((num_rows*num_cols, 3), dtype=np.float32)
    vertices[:, 0] = xx.flatten()
    vertices[:, 1] = yy.flatten()
    vertices[:, 2] = hf.flatten() * vertical_scale
    triangles = -np.ones((2*(num_rows-1)*(num_cols-1), 3), dtype=np.uint32)
    for i in range(num_rows - 1):
        ind0 = np.arange(0, num_cols-1) + i*num_cols
        ind1 = ind0 + 1
        ind2 = ind0 + num_cols
        ind3 = ind2 + 1
        start = 2*i*(num_cols-1)
        stop = start + 2*(num_cols-1)
        triangles[start:stop:2, 0] = ind0
        triangles[start:stop:2, 1] = ind3
        triangles[start:stop:2, 2] = ind1
        triangles[start+1:stop:2, 0] = ind0
        triangles[start+1:stop:2, 1] = ind2
        triangles[start+1:stop:2, 2] = ind3

    return vertices, triangles, move_x != 0
