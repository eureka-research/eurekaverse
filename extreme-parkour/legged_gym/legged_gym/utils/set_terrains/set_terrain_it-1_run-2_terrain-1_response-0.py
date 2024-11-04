import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Multiple platforms with narrow beams and slopes across a pit to test climbing and balancing."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length = 0.8 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.4, 0.5)  # Decrease platform width to test balance
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.05 + 0.2 * difficulty, 0.1 + 0.3 * difficulty
    gap_length_min, gap_length_max = 0.2 + 0.4 * difficulty, 0.6 + 0.4 * difficulty
    gap_length_min, gap_length_max = m_to_idx(gap_length_min), m_to_idx(gap_length_max)
    
    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_slope(start_x, end_x, mid_y, slope_height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slant = np.linspace(0, slope_height, num=x2-x1)
        height_field[x1:x2, y1:y2] = slant[:, None]

    dx_min, dx_max = 0.0, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.0, 0.2  # Some horizontal variability
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)
    
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]
    
    cur_x = spawn_length
    for i in range(6):  # Add 6 platforms with narrow beams and slopes between them
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Add randomly between narrow beams and slopes
        if i % 2 == 0:
            gap_length = np.random.randint(gap_length_min, gap_length_max)
        else:
            slope_height = np.random.uniform(platform_height_min, platform_height_max)
            add_slope(cur_x + platform_length + dx, cur_x + platform_length + dx + gap_length_min, mid_y + dy, slope_height)
            gap_length = slope_height
        
        cur_x += platform_length + dx + gap_length
    
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals