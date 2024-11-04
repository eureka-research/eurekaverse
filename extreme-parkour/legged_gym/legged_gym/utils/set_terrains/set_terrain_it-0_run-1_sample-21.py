import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Zigzag trenches and ridges for the robot to navigate through and climb over."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    trench_width = np.interp(difficulty, [0, 1], [0.9, 0.4])
    ridge_height = np.interp(difficulty, [0, 1], [0.2, 0.8])
    trench_width = m_to_idx(trench_width)
    ridge_height = np.random.uniform(ridge_height - 0.1 * difficulty, ridge_height + 0.1 * difficulty)

    def add_trench_and_ridge(start_x, width, height):
        half_width = width // 2
        mid_y = m_to_idx(width) // 2
        trench_start_y = mid_y - half_width
        trench_end_y = mid_y + half_width

        # Set trench
        height_field[start_x:start_x + half_width, trench_start_y:trench_end_y] = -0.3 - height * difficulty

        # Set ridge
        height_field[start_x + half_width:start_x + m_to_idx(1), trench_start_y:trench_end_y] = height

    # Set the spawning area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # Put the first goal at the initial starting point
    mid_y = m_to_idx(width) // 2
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Start creating trenches and ridges
    cur_x = spawn_length
    for i in range(6):
        add_trench_and_ridge(cur_x, trench_width, ridge_height)

        # Put goal at the end of each ridge
        goals[i + 1] = [cur_x + m_to_idx(0.5), mid_y]

        # Move to the next segment
        cur_x += m_to_idx(1)

    # Add final goal, placed at the end of the last ridge
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    return height_field, goals