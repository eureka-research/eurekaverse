import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Alternating narrow walkways and wider platforms testing the robot's balance and navigation."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    length_idx = m_to_idx(length)
    width_idx = m_to_idx(width)
    height_field = np.zeros((length_idx, width_idx))
    goals = np.zeros((8, 2))

    narrow_walkway_width = 0.4 + 0.1 * difficulty  # Narrower walkways
    narrow_walkway_width = m_to_idx(narrow_walkway_width)
    platform_width = np.random.uniform(1.0, 1.5)  # Wider platforms
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.2 * difficulty, 0.4 * difficulty

    slope_length = 0.9 - 0.3 * difficulty
    slope_length = m_to_idx(slope_length)

    mid_y = width_idx // 2

    def add_narrow_walkway(start_x, end_x, mid_y):
        half_width = narrow_walkway_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = np.random.uniform(platform_height_min, platform_height_max)

    def add_wide_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = np.random.uniform(platform_height_min, platform_height_max)

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(1, 8):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        if i % 2 == 1:
            # Add narrow walkway
            add_narrow_walkway(cur_x, cur_x + slope_length + dx, mid_y + dy)
        else:
            # Add wide platform
            add_wide_platform(cur_x, cur_x + slope_length + dx, mid_y + dy)

        goals[i] = [cur_x + (slope_length + dx) / 2, mid_y + dy]
        cur_x += slope_length + dx  # No large gaps to reduce edge violations

    return height_field, goals