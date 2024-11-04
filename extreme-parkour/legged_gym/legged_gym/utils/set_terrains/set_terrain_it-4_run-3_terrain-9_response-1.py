import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Multiple diverse obstacles including higher platforms, wider gaps, narrow beams, and steep ramps for the robot to climb and jump across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up obstacle dimensions
    platform_length = m_to_idx(1.0 - 0.2 * difficulty)
    platform_width = m_to_idx(0.8 + 0.4 * difficulty)
    platform_height_min, platform_height_max = 0.05 + 0.2 * difficulty, 0.1 + 0.3 * difficulty
    gap_length = m_to_idx(0.5 + 0.5 * difficulty)
    beam_width = m_to_idx(0.2 + 0.2 * difficulty)
    ramp_length = m_to_idx(1.5 - 0.5 * difficulty)
    ramp_height = m_to_idx(0.2 + 0.4 * difficulty)
    
    mid_y = m_to_idx(width) // 2

    dx_min, dx_max = -0.2, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    def add_platform(x, mid_y):
        half_width = platform_width // 2
        x_end = x + platform_length
        y_start, y_end = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x:x_end, y_start:y_end] = platform_height
        return x_end

    def add_gap(x):
        x_end = x + gap_length
        height_field[x:x_end, :] = -1.0  # Marking a pit
        return x_end

    def add_beam(x, mid_y):
        half_width = beam_width // 2
        x_end = x + platform_length
        y_start, y_end = mid_y - half_width, mid_y + half_width
        height_field[x:x_end, y_start:y_end] = 0.1 * difficulty  # Slight elevation
        return x_end

    def add_ramp(x, mid_y, direction):
        half_width = platform_width // 2
        x_end = x + ramp_length
        y_start, y_end = mid_y - half_width, mid_y + half_width
        slant = np.linspace(0, direction * ramp_height, num=x_end-x)[None, :]
        height_field[x:x_end, y_start:y_end] = slant
        return x_end

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - 1, mid_y]  

    cur_x = spawn_length
    for i in range(7):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        if i % 3 == 0:
            cur_x = add_platform(cur_x + dx, mid_y + dy)
        elif i % 3 == 1:
            cur_x = add_gap(cur_x)
        else:
            direction = np.random.choice([-1, 1])
            cur_x = add_ramp(cur_x, mid_y + dy, direction)

        # Set goal
        goals[i+1] = [cur_x - platform_length // 2, mid_y + dy]
        
    # Final goal
    goals[-1] = [cur_x, mid_y]
    height_field[cur_x:, :] = 0
    
    return height_field, goals