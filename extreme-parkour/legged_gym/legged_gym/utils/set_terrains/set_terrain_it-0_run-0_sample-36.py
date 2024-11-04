import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Series of ramps and steps for the robot to navigate, designed to test climbing and descending skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Parameters for ramps and steps
    ramp_length = 1.0
    ramp_length = m_to_idx(ramp_length)
    ramp_height_min, ramp_height_max = 0.0 + 0.3 * difficulty, 0.1 + 0.4 * difficulty
    step_height_min, step_height_max = 0.05 + 0.1 * difficulty, 0.2 + 0.3 * difficulty
    step_length = 0.4
    step_length = m_to_idx(step_length)
    step_width = np.random.uniform(1.0, 1.4)
    step_width = m_to_idx(step_width)

    mid_y = m_to_idx(width) // 2

    def add_ramp(start_x, end_x, start_height, end_height):
        height_gradient = np.linspace(start_height, end_height, end_x - start_x)
        height_field[start_x:end_x, :] = height_gradient[:, np.newaxis]

    def add_step(x, y_center, step_height):
        half_width = step_width // 2
        y1, y2 = y_center - half_width, y_center + half_width
        height_field[x:x+m_to_idx(0.4), y1:y2] = step_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(3):  # Set up 3 ramps and 3 steps alternatively
        # Add ramp
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        add_ramp(cur_x, cur_x + ramp_length, 0, ramp_height)

        # Put goal on top of the ramp
        goals[2*i + 1] = [cur_x + ramp_length // 2, mid_y]

        # Update current x
        cur_x += ramp_length

        # Add step
        step_height = np.random.uniform(step_height_min, step_height_max)
        add_step(cur_x, mid_y, ramp_height + step_height)

        # Put goal on top of the step
        goals[2*i + 2] = [cur_x + m_to_idx(0.2), mid_y]

        # Update current x
        cur_x += m_to_idx(0.4)

    # Add final goal some distance after the last step
    goals[-1] = [cur_x + m_to_idx(1.0), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals