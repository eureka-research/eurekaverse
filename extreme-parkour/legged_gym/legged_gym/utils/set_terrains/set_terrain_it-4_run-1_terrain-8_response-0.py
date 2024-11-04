import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Staggered platforms, narrow bridges, and mild sloped pathways for the quadruped to climb, balance, and navigate"""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions
    platform_length = m_to_idx(1.0 - 0.3 * difficulty)
    platform_height_min, platform_height_max = 0.05 * difficulty, 0.25 * difficulty
    bridge_width = m_to_idx(0.5 - 0.2 * difficulty)
    gap_length = m_to_idx(0.2 + 0.8 * difficulty)
    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, length, mid_y, height):
        half_width = m_to_idx(1.0) // 2
        height_field[start_x:start_x + length, mid_y - half_width:mid_y + half_width] = height

    def add_bridge(start_x, length, mid_y):
        half_width = bridge_width // 2
        height_field[start_x:start_x + length, mid_y - half_width:mid_y + half_width] = 0.5 * platform_height_max * difficulty

    def add_slope(start_x, length, mid_y, height):
        half_width = m_to_idx(1.0) // 2
        slope = np.linspace(0, height, length)
        slope = slope[:, None]  # Add a dimension for broadcasting to y
        height_field[start_x:start_x + length, mid_y - half_width:mid_y + half_width] = slope

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    # Let's mix platforms, slopes, and bridges
    for i in range(1, 7):  # We have 6 more goals to place
        if i % 2 == 1:
            # Add platform every other goal
            height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, platform_length, mid_y, height)
            goals[i] = [cur_x + platform_length // 2, mid_y]
            cur_x += platform_length + gap_length
        else:
            # Add alternating between bridge and slope
            if np.random.rand() > 0.5:
                add_bridge(cur_x, platform_length, mid_y)
            else:
                height = np.random.uniform(platform_height_min, platform_height_max)
                add_slope(cur_x, platform_length, mid_y, height)
            goals[i] = [cur_x + platform_length // 2, mid_y]
            cur_x += platform_length + gap_length

    # Add final goal behind the last obstacle, fill in remaining gap
    goals[-1] = [m_to_idx(11.5), mid_y]
    height_field[m_to_idx(11):, :] = 0

    return height_field, goals