import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Series of hurdles for the quadruped robot to jump over, testing its jumping and coordination skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Setup the hurdles
    hurdle_height_min, hurdle_height_max = 0.05, 0.4
    hurdle_height_min = hurdle_height_min * difficulty
    hurdle_height_max = hurdle_height_max * difficulty

    hurdle_length_min, hurdle_length_max = 0.4, 1.2
    hurdle_length_min = m_to_idx(hurdle_length_min)
    hurdle_length_max = m_to_idx(hurdle_length_max)

    mid_y = m_to_idx(width) // 2
    hurdle_width = 0.6
    hurdle_width = m_to_idx(hurdle_width)

    def add_hurdle(start_x, height):
        y1 = mid_y - hurdle_width // 2
        y2 = mid_y + hurdle_width // 2
        height_field[start_x, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(1), mid_y]  

    cur_x = spawn_length
    for i in range(6):  # Set up 6 hurdles
        hurdle_height = np.random.uniform(hurdle_height_min, hurdle_height_max)
        hurdle_length = np.random.randint(hurdle_length_min, hurdle_length_max)
        add_hurdle(cur_x, hurdle_height)

        # Put goal just after the hurdle
        goals[i+1] = [cur_x + m_to_idx(0.5), mid_y]

        # Move current x to the end of the current hurdle length plus some gap
        cur_x = cur_x + hurdle_length + m_to_idx(0.8)

    # Fill in the final goals
    # Assume the difficulty applies a distance gap factor between hurdles
    # Place the remaining goals
    for i in range(6, 8):
        cur_x += m_to_idx(1.0 / difficulty)
        goals[i] = [cur_x, mid_y]

    return height_field, goals