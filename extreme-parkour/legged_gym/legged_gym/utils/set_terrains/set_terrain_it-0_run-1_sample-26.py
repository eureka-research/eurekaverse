import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Multiple slopes of varying steepness for the robot to climb and descend."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    
    slope_height_min, slope_height_max = 0.05, 0.4
    mid_y = m_to_idx(width) // 2
    
    def add_slope(start_x, end_x, height_start, height_end, width_pos):
        """Add an incline or decline."""
        for x in range(start_x, end_x):
            slope_height = height_start + (height_end - height_start) * (x - start_x) / (end_x - start_x)
            height_field[x, width_pos:width_pos + m_to_idx(1.0)] = slope_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    
    # Initial goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]
    
    cur_x = spawn_length

    # Set up slopes
    for i in range(6):  # Set up 6 slopes
        slope_length = m_to_idx(1.5 + 1.5 * difficulty)
        slope_start_height = np.random.uniform(slope_height_min, slope_height_max)
        slope_end_height = np.random.uniform(slope_height_min, slope_height_max)
        
        add_slope(cur_x, cur_x + slope_length, slope_start_height, slope_end_height, mid_y - m_to_idx(0.5))
        
        # Put goal at the end of each slope
        goals[i + 1] = [cur_x + slope_length, mid_y]
        
        # Transition to next slope
        transition_length = m_to_idx(1.0 + 1.0 * difficulty)
        height_field[cur_x + slope_length:cur_x + slope_length + transition_length, :] = slope_end_height
        
        cur_x += slope_length + transition_length

    # Add final goal after last terrain feature
    final_length = m_to_idx(2)
    height_field[cur_x:, :] = slope_end_height
    goals[-1] = [cur_x + final_length - m_to_idx(0.5), mid_y]

    return height_field, goals