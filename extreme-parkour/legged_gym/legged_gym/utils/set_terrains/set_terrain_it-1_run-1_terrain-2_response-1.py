import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Alternating high and low platforms with variable gaps to challenge climbing and jumping skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    
    platform_length = 0.8 - 0.2 * difficulty  # Shorter to increase frequency of platforms
    platform_length = m_to_idx(platform_length)
    platform_width_min, platform_width_max = 0.8, 1.2
    gap_length_min, gap_length_max = 0.5 + 0.3 * difficulty, 1.0 + 0.6 * difficulty
    gap_length_min, gap_length_max = m_to_idx(gap_length_min), m_to_idx(gap_length_max)
    platform_height_min, platform_height_max = 0.2, 0.3 + 0.2 * difficulty  # Higher platforms

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        width = np.random.uniform(platform_width_min, platform_width_max)
        width = m_to_idx(width)
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length // 2, mid_y]
    
    cur_x = spawn_length
    platform_heights = [np.random.uniform(platform_height_min, platform_height_max) if i % 2 == 0 else 0 for i in range(8)]

    for i in range(7):  # Set up different types of platforms
        gap_length = np.random.randint(gap_length_min, gap_length_max)
        platform_end = cur_x + platform_length
        add_platform(cur_x, platform_end, mid_y, platform_heights[i])
        goals[i + 1] = [cur_x + platform_length // 2, mid_y]
        cur_x = platform_end + gap_length

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals