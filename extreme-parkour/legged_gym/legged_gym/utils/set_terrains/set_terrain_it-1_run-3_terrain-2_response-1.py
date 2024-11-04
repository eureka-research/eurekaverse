import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Mixed complex terrain with varied heights, gaps, and inclines for advanced navigation."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    def add_platform(start_x, end_x, mid_y, width, height):
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_ramp(start_x, end_x, mid_y, width, height, incline):
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slope = np.linspace(0, height * incline, num=x2 - x1)[None, :]
        height_field[x1:x2, y1:y2] = slope.T

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    mid_y = m_to_idx(width) // 2
    spawn_length = m_to_idx(2)
    platform_width_base = 1.0 - 0.6 * difficulty
    platform_width = m_to_idx(platform_width_base)
    gap_length_base = 0.2 + 0.8 * difficulty
    gap_length = m_to_idx(gap_length_base)

    height_incr_base = 0.05 + 0.25 * difficulty
    height_incr = m_to_idx(height_incr_base)
    
    ramp_inclination = 1.0 + 0.5 * difficulty

    # Spawn flat ground setup
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    num_steps = 2 + int(3 * difficulty)  # Number of steps based on difficulty

    for i in range(num_steps):
        platform_height = height_incr * (i + 1)
        platform_length = m_to_idx(0.6)
        
        if random.random() > 0.5:
            add_platform(cur_x, cur_x + platform_length, mid_y, platform_width, platform_height)
        else:
            add_ramp(cur_x, cur_x + platform_length, mid_y, platform_width, platform_height, ramp_inclination)

        goals[i+1] = [cur_x + platform_length // 2, mid_y]
        cur_x += platform_length + gap_length

    # Add a sloped section
    incline_length = m_to_idx(1.2)
    add_ramp(cur_x, cur_x + incline_length, mid_y, platform_width, height_incr * (num_steps + 1), ramp_inclination)
    goals[num_steps+1] = [cur_x + incline_length // 2, mid_y]
    cur_x += incline_length + gap_length

    # Add descending platforms
    for i in range(num_steps):
        platform_height = height_incr * (num_steps - i)
        platform_length = m_to_idx(0.6)

        if random.random() > 0.5:
            add_platform(cur_x, cur_x + platform_length, mid_y, platform_width, platform_height)
        else:
            add_ramp(cur_x, cur_x + platform_length, mid_y, platform_width, platform_height, -ramp_inclination)

        goals[num_steps+2+i] = [cur_x + platform_length // 2, mid_y]
        cur_x += platform_length + gap_length

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    return height_field, goals