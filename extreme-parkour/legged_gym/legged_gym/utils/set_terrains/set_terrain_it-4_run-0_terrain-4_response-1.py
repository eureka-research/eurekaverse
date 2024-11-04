import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Staggered platforms with varied sizes and heights to improve navigating uneven terrain and jumps."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.9, 1.2)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 * difficulty, 0.3 * difficulty
    gap_length = 0.2 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    dx_min, dx_max = -0.2, 0.3
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Set remaining area to be a pit with varying base height
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    for i in range(6):  # Set up staggered platforms
        platform_mid_y = mid_y + np.random.randint(dy_min, dy_max)
        dx = np.random.randint(dx_min, dx_max)
        add_platform(cur_x, cur_x + platform_length + dx, platform_mid_y)

        # Put goal in the center of the platform
        goals[i+1] = [cur_x + (platform_length + dx) / 2, platform_mid_y]

        # Add gap
        cur_x += platform_length + dx + gap_length
    
    # Add final goal behind the last platform, fill in remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals