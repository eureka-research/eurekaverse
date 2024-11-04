import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Courses that combine narrow steps, long gaps, and complex slopes to test climbing, jumping, and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 1.0
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.2 + 0.25 * difficulty, 0.3 + 0.35 * difficulty
    gap_length = 0.4 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)
    slope_length = 1.0 + 0.5 * difficulty
    slope_length = m_to_idx(slope_length)

    mid_y = m_to_idx(width) // 2    

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_slope(start_x, mid_y, length, height, direction=1):
        half_width = platform_width // 2
        x1, x2 = start_x, start_x + length
        y1, y2 = mid_y - half_width, mid_y + half_width
        slope = np.linspace(0, height, x2 - x1)[::direction]
        slope = slope[:, None]
        height_field[x1:x2, y1:y2] += slope

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    # Sequence of Platforms
    for i in range(3):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        height = np.random.uniform(platform_height_min, platform_height_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, height)
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length
    
    # Slopes
    for i in range(3, 7):
        height = np.random.uniform(platform_height_min, platform_height_max)
        direction = np.random.choice([-1, 1])
        add_slope(cur_x, mid_y, slope_length, height, direction)
        goals[i+1] = [cur_x + slope_length // 2, mid_y]
        cur_x += slope_length + gap_length

    # Ending platform
    add_platform(cur_x, cur_x + platform_length, mid_y, 0)
    goals[-1] = [cur_x + platform_length / 2, mid_y]

    return height_field, goals