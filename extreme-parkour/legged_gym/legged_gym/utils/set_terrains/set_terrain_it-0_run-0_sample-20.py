import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Series of staircases and ramps for the robot to climb and descend."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    stair_height = 0.05 + 0.15 * difficulty  # Height of each step
    num_stairs = int(3 + 5 * difficulty)     # Number of stairs
    stair_length = 1.0                       # Length of each staircase
    ramp_height = 0.2 + 0.3 * difficulty     # Height difference for each ramp
    ramp_length = 1.5                        # Length of each ramp

    stair_height = m_to_idx(stair_height)
    stair_length = m_to_idx(stair_length)
    ramp_height = m_to_idx(ramp_height)
    ramp_length = m_to_idx(ramp_length)

    mid_y = m_to_idx(width / 2)

    def add_stairs(start_x, step_height, num_steps):
        for i in range(num_steps):
            x1 = start_x + i * stair_length
            x2 = x1 + stair_length
            height = (i + 1) * step_height
            height_field[x1:x2, mid_y - stair_length:mid_y + stair_length] = height
        return x2

    def add_ramp(start_x, start_height, length, end_height):
        x1 = start_x
        x2 = x1 + length
        for i in range(length):
            height = start_height + i * (end_height - start_height) / length
            height_field[x1 + i, mid_y - stair_length:mid_y + stair_length] = height
        return x2

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    for i in range(4):  # 4 staircases and 3 ramps to test climbing up and down
        # Add stairs and goal at the topmost step
        cur_x = add_stairs(cur_x, stair_height, num_stairs)
        goals[i * 2 + 1] = [cur_x - stair_length, mid_y]

        # Add ramp and goal at the end of the ramp
        cur_x = add_ramp(cur_x, num_stairs * stair_height, ramp_length, 0)
        goals[i * 2 + 2] = [cur_x - m_to_idx(0.5), mid_y]
    
    # Final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals