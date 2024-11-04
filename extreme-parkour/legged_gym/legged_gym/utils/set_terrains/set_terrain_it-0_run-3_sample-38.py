import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Series of ascending and descending ramps for the robot to navigate across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up ramp dimensions
    ramp_length = 2.0 - 1.0 * difficulty
    ramp_length = m_to_idx(ramp_length)
    ramp_height_max = 0.4 * difficulty
    ramp_height_min = 0.2 * difficulty
    ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)

    def add_ramp(start_x, end_x, height, ascending=True):
        if ascending:
            slope = np.linspace(0, height, end_x - start_x)
        else:
            slope = np.linspace(height, 0, end_x - start_x)
        height_field[start_x:end_x] = slope[:, np.newaxis]

    dx_min, dx_max = 0.2, 0.5
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.8, 0.8
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), m_to_idx(width / 2)]

    cur_x = spawn_length
    ascending = True
    for i in range(6):  # Set up 6 ramps
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        ramp_start_y = m_to_idx(width) // 2 + dy
        ramp_end_y = ramp_start_y + m_to_idx(0.8)

        ramp_end_x = cur_x + ramp_length + dx
        add_ramp(cur_x, ramp_end_x, ramp_height, ascending)

        # Put goal in the middle of the ramp
        goals[i+1] = [cur_x + (ramp_length + dx) // 2, ramp_start_y + m_to_idx(0.4)]

        # Flip the direction of the slope for the next ramp
        ascending = not ascending
        
        cur_x += ramp_length + dx

    # Add final goal towards the end of the course
    goals[-1] = [cur_x + m_to_idx(0.5), m_to_idx(width / 2)]
    height_field[cur_x:, :] = 0

    return height_field, goals