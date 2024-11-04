import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Combination of higher platforms, longer ramps, and wider gaps for increased difficulty."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length = 1.0 + 0.5 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.4)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.2 + 0.3 * difficulty, 0.5 + 0.6 * difficulty
    gap_length_min, gap_length_max = 0.2 + 0.5 * difficulty, 0.4 + 0.7 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_ramp(start_x, end_x, mid_y, start_height, end_height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_slope = (end_height - start_height) / (end_x - start_x)

        for x in range(x1, x2):
            for y in range(y1, y2):
                height_field[x, y] = start_height + ramp_slope * (x - x1)

    dx_min, dx_max = -0.2, 0.3
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.6
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]
    
    cur_x = spawn_length
    add_platform(cur_x, cur_x + platform_length, mid_y, random.uniform(platform_height_min, platform_height_max))
    goals[1] = [cur_x + platform_length / 2, mid_y]
    cur_x += platform_length + m_to_idx(gap_length_min)

    for i in range(2, 8):
        if i % 2 == 0:
            platform_height = random.uniform(platform_height_min, platform_height_max)
            gap_length = random.uniform(gap_length_min, gap_length_max)
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height)
            goals[i] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
            cur_x += platform_length + dx + m_to_idx(gap_length)
        else:
            ramp_start_height = random.uniform(platform_height_min, platform_height_max)
            ramp_end_height = random.uniform(platform_height_min, platform_height_max)
            ramp_length = platform_length * 1.5
            add_ramp(cur_x, cur_x + ramp_length, mid_y, ramp_start_height, ramp_end_height)
            goals[i] = [cur_x + ramp_length / 2, mid_y]
            cur_x += ramp_length + m_to_idx(gap_length_min)

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = -1.0
    
    return height_field, goals