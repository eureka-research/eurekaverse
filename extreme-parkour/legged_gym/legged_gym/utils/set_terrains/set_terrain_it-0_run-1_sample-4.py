import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Narrow zigzag paths with varying elevation ramps."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define some parameters
    passage_width = 0.4 + difficulty * 0.2  # width will range from 0.4m to 0.6m based on difficulty
    passage_width_idx = m_to_idx(passage_width)
    ramp_height_min, ramp_height_max = 0.1 * difficulty, 0.5 * difficulty  # ramp height increases with difficulty
    
    def add_passage(x_start, y_center, length, ramp_height=0):
        """Add a narrow passage centered at y_center of given length and height."""
        half_width = passage_width_idx // 2
        x1 = x_start
        x2 = x_start + m_to_idx(length)
        y1 = y_center - half_width
        y2 = y_center + half_width
        height_field[x1:x2, y1:y2] = ramp_height
    
    def add_ramp(x_start, y_center, length, height):
        """Add a ramp rising in height across its length."""
        x1 = x_start
        x2 = x_start + m_to_idx(length)
        y1 = y_center - passage_width_idx // 2
        y2 = y_center + passage_width_idx // 2
        for x in range(x1, x2):
            ramp_height = height * ((x - x1) / (x2 - x1))  # linearly increasing height
            height_field[x, y1:y2] = ramp_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), m_to_idx(width) // 2]

    ramp_length = 1.0
    ramp_length_idx = m_to_idx(ramp_length)
    passage_length = 1.5
    
    cur_x = spawn_length
    mid_y = m_to_idx(width) // 2
    
    for i in range(6):
        difficulty_factor = (i + 1) / 6 * difficulty
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max) * difficulty_factor
        
        if i % 2 == 0:
            y_center = mid_y - m_to_idx(0.6)  # upper side path
        else:
            y_center = mid_y + m_to_idx(0.6)  # lower side path
        
        add_passage(cur_x, y_center, passage_length, 0)
        add_ramp(cur_x + passage_length, y_center, ramp_length, ramp_height)
        
        goals[i+1] = [cur_x + passage_length + ramp_length / 2, y_center]
        
        cur_x += passage_length + ramp_length

    # Add final goal behind the last ramp
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals