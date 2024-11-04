import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Varied terrain with inclines and declines, including ramps and flat areas."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define dimensions for ramps and platforms
    ramp_length_min = 1.0
    ramp_length_max = 1.2 + 0.8 * difficulty
    ramp_length_min, ramp_length_max = m_to_idx(ramp_length_min), m_to_idx(ramp_length_max)

    platform_length = 1.0
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.6)
    platform_width = m_to_idx(platform_width)

    incline_min, incline_max = 0.1, 0.3 * difficulty
    incline_height = lambda length: np.random.uniform(incline_min, incline_max) * length

    mid_y = m_to_idx(width) // 2

    def add_ramp(start_x, end_x, height_start, height_end, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_line = np.linspace(height_start, height_end, x2 - x1).reshape(-1, 1)
        height_field[x1:x2, y1:y2] = ramp_line

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    current_height = 0

    for i in range(7):  # Set up 7 ramps or flat platforms
        is_ramp = True if random.random() < 0.7 else False
        
        if is_ramp:
            ramp_length = np.random.randint(ramp_length_min, ramp_length_max)
            ramp_height = incline_height(ramp_length)
            
            # Randomly decide if incline or decline
            if random.random() < 0.5:
                height_end = current_height + ramp_height
            else:
                height_end = current_height - ramp_height

            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)
            add_ramp(cur_x, cur_x + ramp_length + dx, current_height, height_end, mid_y + dy)
            current_height = height_end
            goals[i+1] = [cur_x + (ramp_length + dx) / 2, mid_y + dy]
            cur_x += ramp_length + dx
        else:
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)
            x1, x2 = cur_x, cur_x + platform_length + dx
            y1, y2 = mid_y - platform_width // 2 + dy, mid_y + platform_width // 2 + dy
            height_field[x1:x2, y1:y2] = current_height
            cur_x += platform_length + dx
            goals[i+1] = [x1 + (x2 - x1) / 2, mid_y + dy]
    
    # Add final goal at the end
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = current_height

    return height_field, goals