import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Series of sloping ramps for the robot to climb and descend."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define ramp characteristics based on difficulty
    ramp_length_min = 1.0
    ramp_length_max = 2.0
    
    ramp_height_min = 0.1 * difficulty
    ramp_height_max = 0.5 * difficulty
    
    flat_area_length = 0.5  # Length of flat areas between ramps
    flat_area_length = m_to_idx(flat_area_length)

    mid_y = m_to_idx(width) // 2
    
    def add_ramp(start_x, end_x, height_start, height_end):
        slope = (height_end - height_start) / (end_x - start_x)
        for x in range(start_x, end_x):
            height = height_start + slope * (x - start_x)
            height_field[x, :] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]
    
    current_x = spawn_length

    for i in range(6):  # Create 6 ramps
        ramp_length = np.random.uniform(ramp_length_min, ramp_length_max)
        ramp_length = m_to_idx(ramp_length)
        
        start_height = height_field[current_x - 1, 0] if current_x != spawn_length else 0 
        end_height = np.random.uniform(ramp_height_min, ramp_height_max)
        
        add_ramp(current_x, current_x + ramp_length, start_height, end_height)
        
        # Place the goal at the top end of each ramp
        goals[i + 1] = [current_x + ramp_length // 2, mid_y]
        
        current_x += ramp_length
        
        # Add a flat area
        height_field[current_x:current_x + flat_area_length, :] = end_height
        current_x += flat_area_length
        
    # Final goal at the end of the course
    goals[-1] = [min(current_x + m_to_idx(1), m_to_idx(length) - 1), mid_y]
    height_field[current_x:, :] = height_field[current_x - 1, 0]

    return height_field, goals