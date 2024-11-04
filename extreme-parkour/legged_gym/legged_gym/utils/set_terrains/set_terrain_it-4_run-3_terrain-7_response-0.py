import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Combines staggered platforms, narrow bridges, and alternating ramps for optimized complexity."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Constants sizing and initial variables
    platform_length = m_to_idx(1.0 - 0.3 * difficulty)
    ramp_slope_length = m_to_idx(1.0 - 0.2 * difficulty)
    bridge_width = m_to_idx(0.5 - 0.2 * difficulty)
    gap_length = m_to_idx(0.2 + 0.9 * difficulty)
    mid_y = m_to_idx(width) // 2

    platform_height_min, platform_height_max = 0.15 + 0.2 * difficulty, 0.3 + 0.25 * difficulty

    def add_platform(start_x, end_x, mid_y, height):
        y1, y2 = mid_y - m_to_idx(0.5), mid_y + m_to_idx(0.5)
        height_field[start_x:end_x, y1:y2] = height

    def add_ramp(start_x, end_x, mid_y, direction, height):
        y1, y2 = mid_y - m_to_idx(0.5), mid_y + m_to_idx(0.5)
        ramp_height = np.linspace(0, height, y2 - y1)[::direction]
        ramp_height = ramp_height[None, :]
        height_field[start_x:end_x, y1:y2] = ramp_height

    def add_bridge(start_x, end_x, mid_y, width_idx):
        y1, y2 = mid_y - width_idx // 2, mid_y + width_idx // 2
        height_field[start_x:end_x, y1:y2] = 0.6 * (platform_height_max + platform_height_min) / 2

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    # First platform
    add_platform(cur_x, cur_x + platform_length, mid_y, platform_height_min)
    goals[1] = [cur_x + platform_length // 2, mid_y]
    cur_x += platform_length + gap_length

    # Adding dynamic obstacles
    obstacles = [
        {'type': 'ramp', 'direction': 1, 'length': platform_length, 'width': 1.0},
        {'type': 'bridge', 'direction': 1, 'length': gap_length, 'width': 0.5},
        {'type': 'ramp', 'direction': -1, 'length': platform_length, 'width': 1.0},
        {'type': 'platform', 'height': (platform_height_min + platform_height_max) / 2, 'width': 0.8},
        {'type': 'bridge', 'direction': 1, 'length': gap_length, 'width': 0.4},
        {'type': 'ramp', 'direction': 1, 'length': ramp_slope_length, 'width': 1.0}
    ]

    for i, obs in enumerate(obstacles, 2):
        if obs['type'] == 'ramp':
            add_ramp(cur_x, cur_x + obs['length'], mid_y, obs['direction'], platform_height_max)
        elif obs['type'] == 'bridge':
            add_bridge(cur_x, cur_x + obs['length'], mid_y, bridge_width)
        elif obs['type'] == 'platform':
            add_platform(cur_x, cur_x + platform_length, mid_y, obs['height'])

        goals[i] = [cur_x + obs['length'] // 2, mid_y]
        cur_x += obs['length'] + m_to_idx(0.1)

    # Add final goal behind the last obstacle, fill in the remaining gap
    goals[-1] = [m_to_idx(11.5), mid_y]
    height_field[m_to_idx(11):, :] = 0

    return height_field, goals