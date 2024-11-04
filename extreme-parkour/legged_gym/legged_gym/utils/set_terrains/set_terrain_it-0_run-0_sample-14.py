import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Inclined planes and descending stairs to test the robot's stability and climbing capabilities."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    mid_y = m_to_idx(width) // 2
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Parameters for obstacles
    incline_length = 1.0 + difficulty  # Incline length increases with difficulty
    incline_length = m_to_idx(incline_length)
    stair_depth = 0.3  # Depth of each stair step
    stair_height = 0.1 + difficulty * 0.2  # Height of each stair step increases with difficulty
    stair_count = 4  # Number of stairs
    stair_depth = m_to_idx(stair_depth)
    stair_height = m_to_idx(stair_height)

    # Set up inclined plane
    incline_start_x = spawn_length
    incline_end_x = incline_start_x + incline_length
    incline_height = np.linspace(0, 0.3 + 0.7 * difficulty, incline_length)
    height_field[incline_start_x:incline_end_x, :] = incline_height[:, np.newaxis]
    goals[1] = [(incline_start_x + incline_end_x) / 2, mid_y]

    # Set up a flat area at the top of the incline
    flat_length = m_to_idx(1.0)
    flat_start_x = incline_end_x
    flat_end_x = flat_start_x + flat_length
    height_field[flat_start_x:flat_end_x, :] = incline_height[-1]
    goals[2] = [(flat_start_x + flat_end_x) / 2, mid_y]

    # Set up descending stairs
    stair_start_x = flat_end_x
    for i in range(stair_count):
        stair_end_x = stair_start_x + stair_depth
        height_field[stair_start_x:stair_end_x, :] = incline_height[-1] - stair_height * (i+1)
        stair_start_x = stair_end_x
    goals[3] = [stair_start_x - stair_depth / 2, mid_y]

    # Another flat area
    flat_start_x = stair_start_x
    flat_end_x = flat_start_x + m_to_idx(1.0)
    height_field[flat_start_x:flat_end_x, :] = incline_height[-1] - stair_height * stair_count
    goals[4] = [(flat_start_x + flat_end_x) / 2, mid_y]

    # Add another inclined plane
    incline2_start_x = flat_end_x
    incline2_end_x = incline2_start_x + incline_length
    incline_height2 = np.linspace(0, 0.3 + 0.7 * difficulty, incline_length)
    height_field[incline2_start_x:incline2_end_x, :] = incline_height2[:, np.newaxis] + incline_height[-1]
    goals[5] = [(incline2_start_x + incline2_end_x) / 2, mid_y]

    # Final flat area
    final_length = m_to_idx(3.0)
    final_start_x = incline2_end_x
    final_end_x = final_start_x + final_length
    height_field[final_start_x:final_end_x, :] = incline_height2[-1] + incline_height[-1]
    goals[6] = [(final_start_x + final_end_x) / 2, mid_y]

    # Final goal position
    goals[7] = [final_end_x - m_to_idx(0.5), mid_y] 

    return height_field, goals