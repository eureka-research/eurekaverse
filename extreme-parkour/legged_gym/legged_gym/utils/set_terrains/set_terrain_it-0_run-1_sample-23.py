import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Sloped terrain with alternating ascending and descending slopes for the robot to navigate."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up slope dimensions
    slope_length = 1.0  # 1 meter long slopes
    slope_length_idx = m_to_idx(slope_length)
    max_slope_height = 0.3 * difficulty  # maximum height difference is proportional to difficulty, up to 0.3 meters
    mid_y = m_to_idx(width) // 2

    def add_slope(start_x, slope_length_idx, height_start, height_end, mid_y):
        slope = np.linspace(height_start, height_end, slope_length_idx)
        for i in range(slope_length_idx):
            height_field[start_x + i, :] = slope[i]

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length, mid_y]  
    
    cur_x = spawn_length
    current_height = 0

    # Create alternating slopes
    for i in range(4):  # We will make 4 ascending and 4 descending slopes
        next_height = current_height + max_slope_height if i % 2 == 0 else current_height - max_slope_height
        add_slope(cur_x, slope_length_idx, current_height, next_height, mid_y)
        
        # Place goal at end of each slope
        goals[i*2 + 1] = [cur_x + slope_length_idx, mid_y]
        
        current_height = next_height
        cur_x += slope_length_idx
        
        # Add a short flat segment between consecutive slopes
        if i != 3:  # No flat segment after the last slope
            add_slope(cur_x, m_to_idx(0.2), current_height, current_height, mid_y)
            cur_x += m_to_idx(0.2)
    
    # Ensure the last segment is flat ground for the final goal
    if cur_x < height_field.shape[0]:
        height_field[cur_x:, :] = current_height
    goals[-1] = [height_field.shape[0] - m_to_idx(0.5), mid_y]

    return height_field, goals