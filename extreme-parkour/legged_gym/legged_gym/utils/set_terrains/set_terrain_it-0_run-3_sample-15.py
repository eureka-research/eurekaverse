import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Multiple hurdles for the robot to jump over, testing its jumping capabilities."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set the dimensions of the hurdles
    hurdle_width = 1.0  # 1 meter wide hurdles
    hurdle_width_idx = m_to_idx(hurdle_width)
    hurdle_height_min = 0.1 + 0.3 * difficulty  # Minimum height of hurdle
    hurdle_height_max = 0.2 + 0.5 * difficulty  # Maximum height of hurdle
    hurdle_distance = 1.0 - 0.5 * difficulty  # Distance between hurdles
    hurdle_distance_idx = m_to_idx(hurdle_distance)

    # Set initial positions and mid-point
    cur_x = m_to_idx(2)  # Start hurdles after 2 meters from the start
    mid_y = m_to_idx(width / 2)
    
    # Set the flat spawn area
    height_field[:cur_x, :] = 0
    goals[0] = [cur_x - m_to_idx(1), mid_y]  # Set the first goal near the spawn
    
    for i in range(1, 8):
        if i < 7:
            # Generate hurdle height within the defined range
            hurdle_height = np.random.uniform(hurdle_height_min, hurdle_height_max)
            
            # Add hurdles to the terrain
            y1, y2 = mid_y - hurdle_width_idx // 2, mid_y + hurdle_width_idx // 2
            height_field[cur_x:cur_x + m_to_idx(0.2), y1:y2] = hurdle_height  # Hurdle depth is 0.2 meters

            # Set goals just behind each hurdle
            goals[i] = [cur_x + m_to_idx(0.3), mid_y]  # Goals are placed slightly behind the hurdles
        
            # Increment the current x position by the distance between hurdles
            cur_x += hurdle_distance_idx

    # Final segment of the terrain after last goal
    height_field[cur_x:, :] = 0
    
    return height_field, goals