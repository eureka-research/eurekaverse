import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Narrow elevated platforms with connecting ramps testing balance, agility and precise positioning."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up dimensions and parameters based on difficulty level
    platform_length = 0.8  # meters
    platform_length = m_to_idx(platform_length)
    platform_width = 0.28 + 0.1 * (1 - difficulty)  # Narrowing with difficulty
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 * difficulty, 0.2 * difficulty
    gap_length_min, gap_length_max = 0.4 + 0.2 * difficulty, 1.0  
    gap_length_min, gap_length_max = m_to_idx(gap_length_min), m_to_idx(gap_length_max)
    ramp_slope = np.random.uniform(0.1, 0.2 * difficulty)  # Difficulty increases ramp steepness

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, center_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = center_y - half_width, center_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_ramp(start_x, end_x, center_y, direction, slope):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = center_y - half_width, center_y + half_width
        ramp_height = slope * (x2 - x1)
        slant = np.linspace(0, ramp_height, num=x2 - x1)[::direction]
        slant = slant[:, None]  # Add a dimension for broadcasting to y
        height_field[x1:x2, y1:y2] = slant

    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    for i in range(7):  # 7 obstacles to match 8 goals
        dx = np.random.randint(gap_length_min, gap_length_max)
        height = np.random.uniform(platform_height_min, platform_height_max)
        
        # Alternate between platform and ramp
        if i % 2 == 0:
            add_platform(cur_x, cur_x + platform_length, mid_y, height)
            goals[i + 1] = [cur_x + platform_length / 2, mid_y]
        else:
            direction = 1 if np.random.random() < 0.5 else -1
            add_ramp(cur_x, cur_x + platform_length, mid_y, direction, ramp_slope)
            goals[i + 1] = [cur_x + platform_length / 2, mid_y]

        cur_x += platform_length + dx
    
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals