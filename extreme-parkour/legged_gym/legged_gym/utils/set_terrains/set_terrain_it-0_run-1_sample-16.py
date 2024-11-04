import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Ridges and valleys pattern to test the robot's ability to navigate varying heights and maintain balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Parameters for ridges and valleys
    ridge_width_min = 1.0
    ridge_width_max = 1.5
    ridge_height_min = 0.1 + difficulty * 0.2
    ridge_height_max = 0.2 + difficulty * 0.4
    valley_depth_min = -0.1 - difficulty * 0.2
    valley_depth_max = -0.2 - difficulty * 0.4
    ridge_width_offset = np.random.uniform(ridge_width_min, ridge_width_max)
    valley_width_offset = np.random.uniform(ridge_width_min, ridge_width_max)
    
    # Helper function to add a ridge or valley
    def add_ridge_or_valley(start_x, width, height):
        end_x = start_x + m_to_idx(width)
        midpoint_x = start_x + (end_x - start_x) // 2
        mid_y = m_to_idx(width) // 2
        height_field[start_x:end_x, :] = height
        return midpoint_x

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), m_to_idx(width / 2)]

    cur_x = spawn_length
    for i in range(1, 8):
        if i % 2 == 1:
            # Add a ridge
            ridge_height = np.random.uniform(ridge_height_min, ridge_height_max)
            ridge_width = np.random.uniform(ridge_width_min, ridge_width_max)
            midpoint_x = add_ridge_or_valley(cur_x, ridge_width, ridge_height)
            goals[i] = [midpoint_x, m_to_idx(width / 2)]
            cur_x += m_to_idx(ridge_width)
        else:
            # Add a valley
            valley_depth = np.random.uniform(valley_depth_min, valley_depth_max)
            valley_width = np.random.uniform(ridge_width_min, ridge_width_max)
            midpoint_x = add_ridge_or_valley(cur_x, valley_width, valley_depth)
            goals[i] = [midpoint_x, m_to_idx(width / 2)]
            cur_x += m_to_idx(valley_width)

    # Ensure the final portion is flat ground
    height_field[cur_x:, :] = 0

    return height_field, goals