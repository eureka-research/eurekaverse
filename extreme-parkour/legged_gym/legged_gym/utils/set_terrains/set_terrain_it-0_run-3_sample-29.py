import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Tightropes and platforms to test balance and precise movement."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Tightrope and platform dimensions
    platform_length = 1.0
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.5, 1.0)
    platform_width = m_to_idx(platform_width)
    tightrope_width = np.random.uniform(0.05, 0.1)

    platform_height_min, platform_height_max = 0.1, 0.3
    tightrope_height_min, tightrope_height_max = 0.2, 0.4
    
    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, platform_height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = platform_height

    def add_tightrope(start_x, end_x, mid_y, tightrope_height):
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - tightrope_width // 2, mid_y + tightrope_width // 2
        height_field[x1:x2, y1:y2] = tightrope_height

    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(4):
        platform_height = np.random.uniform(platform_height_min, platform_height_max) * difficulty
        tightrope_height = np.random.uniform(tightrope_height_min, tightrope_height_max) * difficulty

        dx = m_to_idx(1.0 + random.uniform(0.0, 0.5) * difficulty)
        
        add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)

        goals[2*i + 1] = [cur_x + platform_length // 2, mid_y]
        
        cur_x += platform_length + dx
        
        add_tightrope(cur_x, cur_x + platform_length, mid_y, -tightrope_height)

        goals[2*i + 2] = [cur_x + platform_length // 2, mid_y]
        
        cur_x += platform_length + dx

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals