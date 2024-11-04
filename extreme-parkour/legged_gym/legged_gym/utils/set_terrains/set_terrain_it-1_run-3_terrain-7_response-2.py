import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Series of different height platforms for the robot to jump onto and adapt its approach."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions for varying heights and gaps
    platform_length = 0.8 - 0.2 * difficulty  # Decreased length to make it jumpier
    platform_length = m_to_idx(platform_length)
    platform_width = 0.4 + 0.4 * (1 - difficulty)  # Narrow platforms
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1, 0.8 * difficulty  # Varied heights
    gap_length = 0.3 + 0.5 * difficulty  # Larger gaps
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Start creating platforms and gaps after spawn area
    cur_x = spawn_length

    for i in range(7):  # 7 platforms
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)

        # Put goal at the center of the platform
        goals[i+1] = [cur_x + platform_length // 2, mid_y]

        # Add gap
        cur_x += platform_length + gap_length
    
    # Add final goal beyond the last platform
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals