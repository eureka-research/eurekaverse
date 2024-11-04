import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Staggered platforms with moderate gaps and varying heights for balance and climbing testing."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and gap dimensions
    platform_length = 1.2 - 0.4 * difficulty  # Adjust length to balance difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 0.5 + 0.2 * difficulty  # Adjust width to balance difficulty
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.1 * difficulty, 0.3 + 0.1 * difficulty
    gap_length = 0.2 + 0.5 * difficulty  # Adjust gap length to balance difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Set remaining area to be a pit
    height_field[spawn_length:, :] = -0.2

    cur_x = spawn_length
    for i in range(6):  # Set up 6 platforms
        dx = np.random.randint(dx_min, dx_max)
        dy_arrangement = [-1, 1] if i % 2 == 0 else [1, -1]  # Alternate dy direction
        dy = np.random.uniform(dy_min, dy_max) * dy_arrangement[i % 2]
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)

        # Put goal in the center of the platform
        goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += platform_length + dx + gap_length
    
    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals