"""
A collection of simple terrains to experiment with.
"""

import numpy as np
import random

def set_terrain(terrain, variation, difficulty):
    terrain_fns = [
        set_terrain_flat,
        # set_terrain_platforms,
        # set_terrain_hurdles,
    ]
    idx = int(variation * len(terrain_fns))
    height_field, goals = terrain_fns[idx](terrain.width * terrain.horizontal_scale, terrain.length * terrain.horizontal_scale, terrain.horizontal_scale, difficulty)
    terrain.height_field_raw = (height_field / terrain.vertical_scale).astype(np.int16)
    terrain.goals = goals * terrain.horizontal_scale

    if terrain_fns[idx] == set_terrain_flat:
        return -1
    return idx

def set_terrain_flat(length, width, field_resolution, difficulty):
    """Flat terrain with no obstacles."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    goals[:, 0] = np.linspace(m_to_idx(2), m_to_idx(length - 2), 8)
    goals[:, 1] = m_to_idx(width) // 2
    goals[:, 1] += np.random.randint(m_to_idx(-1.0), m_to_idx(1.0), size=(8))
    return height_field, goals

def set_terrain_platforms(length, width, field_resolution, difficulty):
    """Multiple platforms for the robot to climb on."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions
    platform_length = 0.7
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.6)
    platform_width = m_to_idx(platform_width)
    # platform_height_min, platform_height_max = 0.0 + 0.5 * difficulty, 0.1 + 0.5 * difficulty
    # platform_height_min, platform_height_max = 0.1 + 0.4 * difficulty, 0.1 + 0.4 * difficulty + 1e-6
    platform_height_min, platform_height_max = 0.1 + 0.4 * difficulty, 0.2 + 0.4 * difficulty
    # platform_height_min, platform_height_max = 0.2 + 0.3 * difficulty, 0.3 + 0.3 * difficulty
    # platform_height_min, platform_height_max = 0.3 + 0.2 * difficulty, 0.4 + 0.2 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_platform(pos_x, pos_y):
        half_length, half_width = platform_length // 2, platform_width // 2
        x1, x2 = pos_x - half_length, pos_x + half_length
        y1, y2 = pos_y - half_width, pos_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        # Set the region bounded by x1, x2, y1, y2 to the platform height
        height_field[x1:x2, y1:y2] = platform_height

    dx_min, dx_max = 2.0, 2.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length, mid_y]  # Put first goal at spawn

    cur_x = spawn_length + m_to_idx(1)
    cur_y = mid_y
    for i in range(6):  # Set up 6 platforms
        add_platform(cur_x, cur_y)
        goals[i+1] = [cur_x, cur_y]  # Put goal in the center of the platform
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        cur_x += dx
        cur_y = mid_y + dy

    # Add final goal behind the last platform
    goals[-1] = [cur_x, mid_y]

    return height_field, goals

def set_terrain_hurdles(length, width, field_resolution, difficulty):
    """Multiple hurdles for the robot to jump over."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up hurdle dimensions
    hurdle_length = 0.1 + 0.3 * difficulty
    hurdle_length = m_to_idx(hurdle_length)
    hurdle_width = np.random.uniform(1.0, 1.6)
    hurdle_width = m_to_idx(hurdle_width)
    hurdle_height_min, hurdle_height_max = 0.1 + 0.2 * difficulty, 0.2 + 0.2 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_hurdle(pos_x, pos_y):
        half_length, half_width = hurdle_length // 2, hurdle_width // 2
        x1, x2 = pos_x - half_length, pos_x + half_length
        y1, y2 = pos_y - half_width, pos_y + half_width
        hurdle_height = np.random.uniform(hurdle_height_min, hurdle_height_max)
        # Set the region bounded by x1, x2, y1, y2 to the hurdle height
        height_field[x1:x2, y1:y2] = hurdle_height

    dx_min, dx_max = 2.0, 2.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length, mid_y]  # Put first goal at spawn

    cur_x = spawn_length + m_to_idx(1)
    cur_y = mid_y
    for i in range(6):  # Set up 6 hurdles
        add_hurdle(cur_x, cur_y)
        goals[i+1] = [cur_x + m_to_idx(0.2), cur_y]  # Put goal after hurdle
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        cur_x += dx
        cur_y = mid_y + dy

    # Add final goal behind the last hurdle
    goals[-1] = [cur_x, mid_y]

    return height_field, goals