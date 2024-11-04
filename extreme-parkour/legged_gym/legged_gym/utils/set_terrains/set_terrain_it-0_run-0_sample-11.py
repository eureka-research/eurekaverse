import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Alternating slopes and stairs to test the robot's capability to handle continuous and discrete elevation changes."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define slope and stair parameters
    slope_length = 1.5 - 0.5 * difficulty
    slope_length = m_to_idx(slope_length)
    slope_height = 0.3 + 0.2 * difficulty

    stair_count = int(4 + 6 * difficulty)
    stair_height = 0.05 + 0.1 * difficulty
    stair_width = 0.2 - 0.05 * difficulty
    stair_width = m_to_idx(stair_width)

    mid_y = m_to_idx(width) // 2

    def add_slope(start_x, length, height, center_y):
        end_x = start_x + length
        gradient = height / length
        for i in range(length):
            height_field[start_x + i, :] = gradient * i

    def add_stairs(start_x, step_count, step_height, step_width, center_y):
        for i in range(step_count):
            height_field[start_x + i * step_width:start_x + (i + 1) * step_width, :] = step_height * (i + 1)
    
    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at spawn

    cur_x = spawn_length

    for i in range(4):  # Alternate between 2 slopes and 2 stairs segments
        if i % 2 == 0:
            # Add slope
            add_slope(cur_x, slope_length, slope_height, mid_y)
            # Place goal at mid-slope
            goals[i+1] = [cur_x + slope_length // 2, mid_y]
            cur_x += slope_length
        else:
            # Add stairs
            add_stairs(cur_x, stair_count, stair_height, stair_width, mid_y)
            # Place goal at end of stairs
            goals[i+1] = [cur_x + stair_count * stair_width - stair_width // 2, mid_y]
            cur_x += stair_count * stair_width

    # Add final goal at the end of the course
    goals[-1] = [m_to_idx(length) - m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0  # Make sure the end of the path is flat

    return height_field, goals