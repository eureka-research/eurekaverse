import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Dynamic terrain with staggered platforms and alternating slopes to test diverse locomotion skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up dimensions for platforms and slopes to balance difficulty
    platform_length = 0.8 - 0.2 * difficulty  # Platforms get shorter as difficulty increases
    platform_length = m_to_idx(platform_length)
    platform_width = 0.9
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 * difficulty, 0.3 * difficulty
    
    slope_length = 1.0 - 0.4 * difficulty
    slope_length = m_to_idx(slope_length)
    slope_height_min, slope_height_max = 0.05 * difficulty, 0.25 * difficulty
    
    gap_length_min, gap_length_max = 0.1 * difficulty, 0.5 * difficulty
    gap_length_min, gap_length_max = m_to_idx(gap_length_min), m_to_idx(gap_length_max)

    mid_y = m_to_idx(width) // 2

    # Functions to add platforms and slopes
    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_slope(start_x, end_x, mid_y, direction):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slope_height = np.random.uniform(slope_height_min, slope_height_max)
        slant = np.linspace(0, slope_height, num=x2-x1)[::direction]
        slant = slant[:, None]  # Add a dimension for broadcasting to y
        height_field[x1:x2, y1:y2] = slant

    # Variables to tune obstacle placement
    dx_min, dx_max = -0.05, 0.05
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set flat spawn area to start
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Place obstacles and goals
    cur_x = spawn_length
    for i in range(4):
        if i % 2 == 0:
            # Add platforms
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
            cur_x += platform_length + dx + np.random.randint(gap_length_min, gap_length_max)
        else:
            # Add slopes
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)
            direction = (-1) ** i  # Alternate slope direction
            add_slope(cur_x, cur_x + slope_length + dx, mid_y + dy, direction)
            goals[i + 1] = [cur_x + (slope_length + dx) / 2, mid_y + dy]
            cur_x += slope_length + dx + np.random.randint(gap_length_min, gap_length_max)

    # Add final platform and goal
    add_platform(cur_x, cur_x + platform_length, mid_y)
    goals[-2] = [cur_x + platform_length / 2, mid_y]
    
    # Final goal
    goals[-1] = [cur_x + platform_length + m_to_idx(0.5), mid_y]
    height_field[cur_x + platform_length:, :] = 0

    return height_field, goals