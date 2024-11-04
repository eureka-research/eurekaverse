import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Narrow paths and wide chasms for balance and jumping precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]
    
    # Initialize the height_field with zeros
    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    
    # Dimensions
    path_width_min, path_width_max = 0.4, 0.6
    path_height_min, path_height_max = 0.1, 0.3
    chasm_width_min, chasm_width_max = 0.5, 1.5
    chasm_length_min, chasm_length_max = 0.2, 0.7
    
    path_width_min, path_width_max = np.clip([path_width_min * (1 - difficulty), path_width_max * (1 - difficulty)], 0.4, 0.6)
    path_height_min, path_height_max = path_height_min * difficulty, path_height_max * difficulty
    chasm_width_min, chasm_width_max = chasm_width_min * difficulty, chasm_width_max * difficulty
    chasm_length_min, chasm_length_max = chasm_length_min * difficulty, chasm_length_max * difficulty
    
    mid_y = m_to_idx(width) // 2
    
    def add_narrow_path(start_x, end_x, mid_y, width):
        half_width = m_to_idx(width) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        path_height = np.random.uniform(path_height_min, path_height_max)
        height_field[x1:x2, y1:y2] = path_height
    
    def add_chasm(start_x, end_x):
        x1, x2 = start_x, end_x
        height_field[x1:x2, :] = -1.0  # Chasm level
    
    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  
    
    cur_x = spawn_length
    for i in range(4):  # Set up narrow paths and chasms
        path_length = m_to_idx(np.random.uniform(1.0, 1.5))
        path_width = np.random.uniform(path_width_min, path_width_max)
        
        # Add narrow path
        add_narrow_path(cur_x, cur_x + path_length, mid_y, path_width)
        goals[i * 2 + 1] = [cur_x + path_length / 2, mid_y]
        
        # Add chasm
        cur_x += path_length
        chasm_length = m_to_idx(np.random.uniform(chasm_length_min, chasm_length_max))
        add_chasm(cur_x, cur_x + chasm_length)
        
        goals[i * 2 + 2] = [cur_x + chasm_length / 2, mid_y]
        cur_x += chasm_length
    
    # Ensure final stretch and place last goal
    last_path_length = m_to_idx(2.0)
    add_narrow_path(cur_x, cur_x + last_path_length, mid_y, path_width_min)
    goals[6] = [cur_x + last_path_length / 2, mid_y]
    goals[7] = [cur_x + last_path_length + m_to_idx(0.5), mid_y]

    return height_field, goals