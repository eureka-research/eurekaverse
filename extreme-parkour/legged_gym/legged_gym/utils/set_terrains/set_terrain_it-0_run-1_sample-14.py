import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Traversing a series of staggered steps and ramps for the robot to climb and balance on."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up step dimensions based on difficulty
    step_height_min, step_height_max = 0.1 * difficulty, 0.3 * difficulty
    step_depth = 1.0 - 0.3 * difficulty
    step_depth = m_to_idx(step_depth)
    step_side_offset = np.random.uniform(0.2, 0.5)
    step_side_offset = m_to_idx(step_side_offset)

    ramp_length = 1.0 + 0.5 * difficulty
    ramp_length = m_to_idx(ramp_length)
    ramp_height = 0.15 + 0.3 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_step(start_x, end_x, start_y, end_y, height):
        height_field[start_x:end_x, start_y:end_y] = height

    def add_ramp(start_x, end_x, start_y, end_y, start_height, end_height):
        for x in range(start_x, end_x):
            height = start_height + (end_height - start_height) * (x - start_x) / (end_x - start_x)
            height_field[x, start_y:end_y] = height

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
    for i in range(4):  # Set up 4 steps
        step_height = np.random.uniform(step_height_min, step_height_max)
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_step(cur_x, cur_x + step_depth + dx, mid_y + dy - step_side_offset, mid_y + dy + step_side_offset, step_height)

        # Put goal on top of each step
        goals[i + 1] = [cur_x + (step_depth + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += step_depth + dx

    for i in range(2):  # Add 2 ramps
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_ramp(cur_x, cur_x + ramp_length + dx, mid_y + dy - step_side_offset, mid_y + dy + step_side_offset, step_height, step_height + ramp_height)

        # Update step height to the end height of the ramp
        step_height += ramp_height

        # Put goal at the end of each ramp
        goals[5 + i] = [cur_x + (ramp_length + dx) / 2, mid_y + dy]

        # Move to next section
        cur_x += ramp_length + dx

    # Add final goal on flat ground
    goals[7] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = step_height

    return height_field, goals