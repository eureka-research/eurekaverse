import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Mixed obstacles including wide platforms, uneven stepping stones, and gentle slopes for agility and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform parameters
    platform_width = np.random.uniform(1.2, 1.8)
    platform_width = m_to_idx(platform_width)
    platform_length = 1.5 - 0.5 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_height_min, platform_height_max = 0.1 * difficulty, 0.3 * difficulty

    # Stepping stone parameters
    stepping_stone_size = 0.5
    stepping_stone_size = m_to_idx(stepping_stone_size)
    stepping_stone_height_min, stepping_stone_height_max = 0.05 * difficulty, 0.2 * difficulty

    # Slope parameters
    slope_width = platform_width
    slope_length = 1.5 - 0.5 * difficulty
    slope_length = m_to_idx(slope_length)
    slope_height_min, slope_height_max = 0.1 * difficulty, 0.25 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_stepping_stone(mid_x, mid_y, height):
        half_size = stepping_stone_size // 2
        x1, x2 = mid_x - half_size, mid_x + half_size
        y1, y2 = mid_y - half_size, mid_y + half_size
        height_field[x1:x2, y1:y2] = height

    def add_slope(start_x, end_x, mid_y, height):
        half_width = slope_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slope = np.linspace(0, height, num=x2-x1)[:, None]  # Creating gradual slope
        height_field[x1:x2, y1:y2] = slope

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # First goal at the end of the flat area
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    dx_min, dx_max = m_to_idx(-0.1), m_to_idx(0.1)
    dy_min, dy_max = m_to_idx(-0.4), m_to_idx(0.4)

    # Add first wide platform
    add_platform(cur_x, cur_x + platform_length, mid_y, np.random.uniform(platform_height_min, platform_height_max))
    goals[1] = [cur_x + platform_length // 2, mid_y]
    cur_x += platform_length + m_to_idx(0.5)

    # Add series of stepping stones
    for i in range(2, 6):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_stepping_stone(cur_x + dx, mid_y + dy, np.random.uniform(stepping_stone_height_min, stepping_stone_height_max))
        goals[i] = [cur_x + dx, mid_y + dy]
        cur_x += stepping_stone_size + m_to_idx(0.5)

    # Add final slope
    slope_height = np.random.uniform(slope_height_min, slope_height_max)
    add_slope(cur_x, cur_x + slope_length, mid_y, slope_height)
    goals[-2] = [cur_x + slope_length // 2, mid_y]
    cur_x += slope_length + m_to_idx(0.5)

    # Last goal at the end
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0  # Ensure no further obstacles

    return height_field, goals