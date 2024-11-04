import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Elevated steps of increasing height for the robot to navigate around and over."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    mid_y = m_to_idx(width) // 2
    
    # Sets the step dimensions and heights
    step_length = 0.8  # Each step length
    step_height_increment = 0.15 * difficulty  # Height increment per step
    step_width = 1.4  # Fixed width per step

    step_length_idx = m_to_idx(step_length)
    step_width_idx = m_to_idx(step_width)
    
    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x_start = spawn_length
    current_height = 0.1  # Starting height for the first step

    for i in range(6):  # Set up 6 steps
        x_end = cur_x_start + step_length_idx
        y_start = mid_y - step_width_idx // 2
        y_end = mid_y + step_width_idx // 2

        # Add an elevated step
        height_field[cur_x_start:x_end, y_start:y_end] = current_height
        goals[i+1] = [cur_x_start + step_length_idx // 2, mid_y]

        # Increment the height
        current_height += step_height_increment

        # Move to next step position
        cur_x_start = x_end + m_to_idx(0.2)  # Add some horizontal spacing

    # Fill the last goal position (straight path)
    goals[7] = [cur_x_start + m_to_idx(0.5), mid_y]

    return height_field, goals