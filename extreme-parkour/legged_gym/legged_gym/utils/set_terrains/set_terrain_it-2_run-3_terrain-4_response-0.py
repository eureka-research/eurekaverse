import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """A combination of sideways ramps, narrow bridges, and staggered steps to test balance and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Constants sizing and initial variables
    platform_length = m_to_idx(1.0 - 0.2 * difficulty)
    platform_height_min, platform_height_max = 0.05 * difficulty, 0.25 * difficulty
    bridge_width = m_to_idx(0.5 - 0.2 * difficulty)
    gap_length = m_to_idx(0.2 + 0.8 * difficulty)
    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        y1, y2 = mid_y - m_to_idx(1.0) // 2, mid_y + m_to_idx(1.0) // 2
        height_field[start_x:end_x, y1:y2] = height

    def add_ramp(start_x, end_x, mid_y, direction, height):
        y1, y2 = mid_y - m_to_idx(1.0) // 2, mid_y + m_to_idx(1.0) // 2
        ramp_height = np.linspace(0, height, y2 - y1)[::direction]
        ramp_height = ramp_height[None, :]
        height_field[start_x:end_x, y1:y2] = ramp_height

    def add_bridge(start_x, end_x, mid_y, width_idx):
        y1, y2 = mid_y - width_idx // 2, mid_y + width_idx // 2
        height_field[start_x:end_x, y1:y2] = 0.5 * platform_height_max * difficulty

    def add_staggered_steps(start_x, end_x, mid_y):
        y1, y2 = mid_y - m_to_idx(0.7) // 2, mid_y + m_to_idx(0.7) // 2
        step_heights = np.linspace(platform_height_min, platform_height_max, num=end_x-start_x)
        height_field[start_x:end_x, y1:y2] = step_heights[:, None]

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    # Adding first platform
    add_platform(cur_x, cur_x + platform_length, mid_y, platform_height_min)
    goals[1] = [cur_x + platform_length // 2, mid_y]
    cur_x += platform_length + gap_length

    obstacles = [
        {'type': 'ramp', 'direction': -1, 'length': platform_length, 'width': 1.0},
        {'type': 'bridge', 'direction': 1, 'length': gap_length, 'width': 0.5},
        {'type': 'ramp', 'direction': 1, 'length': platform_length, 'width': 1.0},
        {'type': 'steps', 'direction': 0, 'length': platform_length, 'width': 0.7}
    ]

    for i, obs in enumerate(obstacles, 2):
        if obs['type'] == 'ramp':
            add_ramp(cur_x, cur_x + obs['length'], mid_y, obs['direction'], platform_height_max)
        elif obs['type'] == 'bridge':
            add_bridge(cur_x, cur_x + obs['length'], mid_y, bridge_width)
        elif obs['type'] == 'steps':
            add_staggered_steps(cur_x, cur_x + obs['length'], mid_y)

        goals[i] = [cur_x + obs['length'] // 2, mid_y]
        cur_x += obs['length'] + gap_length

    # Add final goal at the end
    goals[-1] = [m_to_idx(11.5), mid_y]
    height_field[m_to_idx(11):, :] = 0

    return height_field, goals