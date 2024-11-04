import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Staggered steps of varying heights for the robot to climb and traverse."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set the dimensions of the staggered steps
    step_length_base = 1.0  # Base length of each step in meters
    step_width_base = 1.2   # Base width of each step in meters
    
    step_length_variation = 0.3 * difficulty  # The more difficult, the more variation in length
    step_height_min, step_height_max = 0.15 * difficulty, 0.3 * difficulty

    step_length = m_to_idx(step_length_base - step_length_variation)
    step_width = m_to_idx(step_width_base)
    mid_y = m_to_idx(width) // 2

    def add_step(start_x, end_x, height, mid_y):
        half_width = step_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = -0.5, 0.5
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    for i in range(6):  # Set up 6 steps
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        step_height = np.random.uniform(step_height_min, step_height_max)
        add_step(cur_x, cur_x + step_length + dx, step_height, mid_y + dy)

        # Put goal in the center of the step
        goals[i+1] = [cur_x + (step_length + dx) / 2, mid_y + dy]

        # Prepare for the next step
        cur_x += step_length + dx
    
    # Add final goal behind the last step, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals