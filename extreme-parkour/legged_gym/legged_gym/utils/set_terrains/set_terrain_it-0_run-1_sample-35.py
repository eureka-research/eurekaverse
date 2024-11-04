import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Series of steps of varying heights for the robot to climb up and navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up step dimensions
    step_height_min = 0.1 + 0.1 * difficulty
    step_height_max = 0.2 + 0.3 * difficulty
    step_length = 1.0
    step_length = m_to_idx(step_length)
    step_width = 2.0
    step_width = m_to_idx(step_width)

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    mid_y = m_to_idx(width) // 2
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    total_steps = 6  # We will create 6 steps
    for i in range(total_steps):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        step_height = np.random.uniform(step_height_min, step_height_max)
        x1, x2 = cur_x, cur_x + step_length + dx
        y1, y2 = mid_y - step_width // 2 + dy, mid_y + step_width // 2 + dy

        height_field[x1:x2, y1:y2] = step_height

        # Put goal in the middle of each step
        goals[i+1] = [cur_x + (step_length + dx) / 2, mid_y + dy]

        cur_x += step_length + dx

    # Add a final flat area behind the last step with the last goal
    final_flat_length = m_to_idx(1.0)
    height_field[cur_x:cur_x + final_flat_length, :] = 0
    goals[-1] = [cur_x + final_flat_length / 2, mid_y]

    return height_field, goals