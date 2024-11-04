import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Combination of varied ramps, narrow bridges, and staggered platforms for increased challenge in climbing, balancing, and jumping."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Constants for obstacle dimensions
    platform_length = m_to_idx(1.0 - 0.2 * difficulty)
    platform_height = 0.2 * difficulty
    bridge_width = m_to_idx(0.4 * difficulty + 0.6)
    ramp_height = 0.25 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        y1, y2 = mid_y - m_to_idx(0.5), mid_y + m_to_idx(0.5)
        height_field[start_x:end_x, y1:y2] = height
    
    def add_ramp(start_x, end_x, mid_y, slope, direction):
        y1, y2 = mid_y - (slope * (end_x - start_x) // 2), mid_y + (slope * (end_x - start_x) // 2)
        if direction == 'up':
            height = np.linspace(0, ramp_height, end_x - start_x)
        else:
            height = np.linspace(ramp_height, 0, end_x - start_x)
        height_field[start_x:end_x, y1:y2] = height[:, None]

    def add_bridge(start_x, end_x, mid_y, width_idx):
        y1, y2 = mid_y - width_idx // 2, mid_y + width_idx // 2
        height_field[start_x:end_x, y1:y2] = platform_height

    def add_staggered_steps(start_x, end_x, mid_y):
        for i in range(start_x, end_x, m_to_idx(0.5)):
            step_height = np.random.uniform(0, platform_height)
            height_field[i:i + m_to_idx(0.5), mid_y - m_to_idx(0.25):mid_y + m_to_idx(0.25)] = step_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    obstacles = [
        {'type': 'platform', 'length': platform_length, 'height': platform_height},
        {'type': 'ramp', 'slope': 1, 'direction': 'up', 'length': platform_length},
        {'type': 'bridge', 'width': bridge_width, 'length': platform_length},
        {'type': 'steps', 'length': platform_length},
        {'type': 'ramp', 'slope': 1, 'direction': 'down', 'length': platform_length},
        {'type': 'platform', 'length': platform_length, 'height': platform_height}
    ]

    for i, obs in enumerate(obstacles, 1):
        if obs['type'] == 'platform':
            add_platform(cur_x, cur_x + obs['length'], mid_y, obs['height'])
        elif obs['type'] == 'ramp':
            add_ramp(cur_x, cur_x + obs['length'], mid_y, obs['slope'], obs['direction'])
        elif obs['type'] == 'bridge':
            add_bridge(cur_x, cur_x + obs['length'], mid_y, obs['width'])
        elif obs['type'] == 'steps':
            add_staggered_steps(cur_x, cur_x + obs['length'], mid_y)
        
        goals[i] = [cur_x + obs['length'] // 2, mid_y]
        cur_x += obs['length'] + m_to_idx(0.4 * difficulty)

    # Fill remaining area beyond the last obstacle and place final goal
    if cur_x < m_to_idx(length) - m_to_idx(1):
        add_platform(cur_x, m_to_idx(length), mid_y, 0)
    goals[-1] = [m_to_idx(11.5), mid_y]

    return height_field, goals