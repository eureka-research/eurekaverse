import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Series of inclined slopes and uneven terrain to test the quadruped's ability to handle inclined surfaces and maintain balance."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Parameters controlling slope and height
    slope_length = 1.0 + difficulty * 2.0  # Length of the inclined slopes increases with difficulty
    slope_length_idx = m_to_idx(slope_length)
    max_slope_height = 0.2 + difficulty * 0.8  # Max height of the slopes
    min_slope_height = 0.05 + difficulty * 0.45  # Min height of the slopes

    def add_slope(start_x, end_x, mid_y, height):
        """Adds an inclined slope to the height field."""
        half_width = m_to_idx(1.0) // 2  # Ensure the slope is at least 1 meter wide
        for x in range(start_x, end_x):
            slope_height = height * (x - start_x) / (end_x - start_x)
            height_field[x, mid_y - half_width:mid_y + half_width] = slope_height

    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0  # Flat ground at start
    mid_y = m_to_idx(width) // 2

    # Set the initial goal at the spawn location
    goals[0] = [spawn_length // 2, mid_y]

    cur_x = spawn_length

    for i in range(6):  # Create 6 slopes
        slope_height = np.random.uniform(min_slope_height, max_slope_height)
        add_slope(cur_x, cur_x + slope_length_idx, mid_y, slope_height)
        
        # Place a goal at the middle of the slope's flat top
        goals[i+1] = [cur_x + (slope_length_idx // 2), mid_y]
        
        cur_x += slope_length_idx

        # Create flat area between slopes
        gap_length = m_to_idx(0.5)  # 0.5 meters flat gap between
        height_field[cur_x:cur_x + gap_length, mid_y - m_to_idx(0.5):mid_y + m_to_idx(0.5)] = slope_height
        cur_x += gap_length

    # Add final flat area and final goal
    height_field[cur_x:, :] = 0
    goals[-1] = [cur_x + m_to_idx(1.0), mid_y]  # Place final goal behind the last slope

    return height_field, goals