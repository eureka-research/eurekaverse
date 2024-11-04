import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Staircase challenge with varying step heights for the robot to climb."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define the staircase parameters
    step_height_min, step_height_max = 0.05 * difficulty, 0.2 * difficulty
    step_length = 0.5
    step_length_idx = m_to_idx(step_length)
    step_width = width
    step_width_idx = m_to_idx(step_width)

    mid_y = m_to_idx(width) // 2
    
    def add_step(start_x, height):
        x1 = start_x
        x2 = start_x + step_length_idx
        height_field[x1:x2, :] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Place the first goal at the edge of spawn area
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(7):  # We will create 7 steps
        # Determine step height
        step_height = np.random.uniform(step_height_min, step_height_max)
        
        # Add the step to the height field
        add_step(cur_x, step_height)
        
        # Set a goal at the middle of the step
        goals[i+1] = [cur_x + step_length_idx // 2, mid_y]
        
        # Move to the start of the next step
        cur_x += step_length_idx

    # Ensure the terrain fits within the specified length
    final_length = height_field.shape[0]
    cur_x = min(cur_x, final_length - step_length_idx)

    return height_field, goals