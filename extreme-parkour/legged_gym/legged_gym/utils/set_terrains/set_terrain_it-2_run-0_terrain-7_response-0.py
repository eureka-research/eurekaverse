import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Sloped ramps followed by narrow platforms with zigzag patterns, forcing precise navigation."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    ramp_length = 1.5 - 0.5 * difficulty
    ramp_length = m_to_idx(ramp_length)
    ramp_width = np.random.uniform(0.8, 1.2)
    ramp_width = m_to_idx(ramp_width)
    ramp_height_range = (0.0 + 0.3 * difficulty, 0.3 + 0.5 * difficulty)
    gap_length = 0.4 + 0.2 * difficulty
    gap_length = m_to_idx(gap_length)

    def add_ramp(x_start, x_end, y_center, direction):
        height_variation = np.random.uniform(*ramp_height_range)
        half_width = ramp_width // 2
        slope = np.linspace(0, height_variation, num=x_end-x_start)
        slope_matrix = slope[None, :] if direction > 0 else slope[None, ::-1]
        y1, y2 = y_center - half_width, y_center + half_width
        height_field[x_start:x_end, y1:y2] = slope_matrix
    
    def add_platform(x_start, x_end, y_center, height):
        half_width = ramp_width // 2
        y1, y2 = y_center - half_width, y_center + half_width
        height_field[x_start:x_end, y1:y2] = height
    
    dx_range = (-0.1, 0.1)
    dy_range = (-0.4, 0.4)
    dx_range = m_to_idx(dx_range)
    dy_range = m_to_idx(dy_range)

    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), m_to_idx(width)//2]
    
    cur_x = spawn_length
    mid_y = m_to_idx(width) // 2
    
    for i in range(4):
        direction = np.random.choice([-1, 1])
        dx = np.random.randint(*dx_range)
        dy = np.random.randint(*dy_range) * direction
        add_ramp(cur_x, cur_x + ramp_length + dx, mid_y + dy, direction)

        # Add goal to middle of the ramp
        goals[i+1] = [cur_x + (ramp_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += ramp_length + dx + gap_length

    platform_height = np.random.uniform(*ramp_height_range)
    for i in range(4, 7):
        dx = np.random.randint(*dx_range)
        dy = np.random.randint(*dy_range)
        add_platform(cur_x, cur_x + m_to_idx(0.8) + dx, mid_y + dy, platform_height)

        goals[i+1] = [cur_x + (m_to_idx(0.8) + dx) / 2, mid_y + dy]
        cur_x += m_to_idx(0.8) + dx + gap_length

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals