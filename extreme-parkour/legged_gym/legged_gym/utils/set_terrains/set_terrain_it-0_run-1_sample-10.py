import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Staggered steps for the robot to climb up and down at varying heights."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set step dimensions
    step_length = 0.9 - 0.2 * difficulty  # Step lengths decrease as difficulty increases
    step_length = m_to_idx(step_length)
    step_width = np.random.uniform(1.0, 1.5)
    step_width = m_to_idx(step_width)
    
    min_height = 0.1 * difficulty
    max_height = 0.2 + 0.3 * difficulty
    
    mid_y = m_to_idx(width) // 2

    def add_step(start_x, end_x, mid_y, height):
        half_width = step_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Add steps
    cur_x = spawn_length
    direction = 1  # 1 means ascending, -1 means descending
    
    for i in range(7):  # Set up 7 steps
        height = np.random.uniform(min_height, max_height) * direction
        add_step(cur_x, cur_x + step_length, mid_y, height)
        
        # Place the goal at the center of the step
        goals[i + 1] = [cur_x + step_length // 2, mid_y]

        cur_x += step_length
        direction *= -1  # Alternate between ascending and descending

    # Add final goal beyond last step
    goals[-1] = [cur_x + m_to_idx(1), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals