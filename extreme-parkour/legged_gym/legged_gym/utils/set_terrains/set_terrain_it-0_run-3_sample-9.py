import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Series of ramps and stairs for the robot to ascend and descend."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up ramp and stairs dimensions based on difficulty
    ramp_length_min, ramp_length_max = 1.0, 2.0
    ramp_length = np.random.uniform(ramp_length_min, ramp_length_max)
    ramp_length = m_to_idx(ramp_length)
    
    stair_height_min, stair_height_max = 0.1 * difficulty, 0.35 * difficulty
    stair_height = np.random.uniform(stair_height_min, stair_height_max)
    
    stair_width_min, stair_width_max = 0.4, 0.8
    stair_width = np.random.uniform(stair_width_min, stair_width_max)
    stair_width = m_to_idx(stair_width)
    
    ramp_height_min, ramp_height_max = 0.2, 0.5
    ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
    
    mid_y = m_to_idx(width) // 2

    def add_ramp(start_x, length, height, mid_y):
        half_width = m_to_idx(1.0) // 2
        for i in range(length):
            height_field[start_x + i, mid_y - half_width:mid_y + half_width] = (i / length) * height

    def add_stairs(start_x, num_stairs, stair_height, stair_width, mid_y):
        for i in range(num_stairs):
            height_field[start_x + i * stair_width: start_x + (i + 1) * stair_width, mid_y - stair_width // 2: mid_y + stair_width // 2] = (i + 1) * stair_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(4):  # Create 4 ramp-stair combinations
        # Add ramp
        add_ramp(cur_x, ramp_length, ramp_height, mid_y)
        cur_x += ramp_length
        
        # Add goal at the top of the ramp
        goals[i * 2 + 1] = [cur_x - ramp_length // 2, mid_y]

        # Add stairs
        num_stairs = int(np.random.uniform(2, 5))
        add_stairs(cur_x, num_stairs, stair_height, stair_width, mid_y)
        cur_x += num_stairs * stair_width

        # Add goal at the base of the stairs
        goals[i * 2 + 2] = [cur_x - stair_width // 2, mid_y]
    
    # Fill in any remaining space with flat ground
    height_field[cur_x:, :] = 0
    # Add final goal
    goals[-1] = [m_to_idx(length) - m_to_idx(0.5), mid_y]

    return height_field, goals