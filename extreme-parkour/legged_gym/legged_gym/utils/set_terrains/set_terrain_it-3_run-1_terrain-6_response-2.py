import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Combination of staggered steps, variable-height platforms, and safe landing zones for the quadruped."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Adjusted obstacle dimensions
    platform_length = 1.0 - 0.2 * difficulty  # Slightly longer platforms
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.2)  # Increase platform width
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.15 * difficulty, 0.30 * difficulty
    gap_length = 0.1 + 0.4 * difficulty  # Minimized gap length
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, length, width, height, mid_y):
        half_width = width // 2
        height_field[start_x:start_x+length, mid_y-half_width:mid_y+half_width] = height

    def add_ramp(start_x, end_x, mid_y, direction, min_height, max_height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(min_height, max_height)
        slant = np.linspace(0, ramp_height, num=y2-y1)[::direction]
        height_field[x1:x2, y1:y2] = slant
    
    dx = m_to_idx(-0.1)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Flat ground at start
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Remaining area set to low height to allow navigation onto platforms
    height_field[spawn_length:, :] = -1.0

    # First platform
    cur_x = spawn_length
    dy = np.random.randint(dy_min, dy_max)
    add_platform(cur_x, platform_length, platform_width, np.random.uniform(platform_height_min, platform_height_max), mid_y + dy)
    goals[1] = [cur_x + platform_length // 2, mid_y + dy]

    cur_x += platform_length + gap_length
    for i in range(1, 6):
        dy = np.random.randint(dy_min, dy_max)
        if i % 2 == 0:
            add_platform(cur_x, platform_length, platform_width, np.random.uniform(platform_height_min, platform_height_max), mid_y + dy)
        else:
            add_ramp(cur_x, cur_x + platform_length, mid_y + dy, (-1) ** i, platform_height_min, platform_height_max)
        
        goals[i+1] = [cur_x + platform_length // 2, mid_y + dy]
        cur_x += platform_length + gap_length
    
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals