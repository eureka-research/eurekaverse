import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Staircase-style platforms of increasing heights for the robot to navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up stair steps dimensions
    step_length = 1.0
    step_length = m_to_idx(step_length)
    step_width = 1.0
    step_width = m_to_idx(step_width)
    step_height_min, step_height_max = 0.1, 0.5
    slope_length = 0.3
    slope_length = m_to_idx(slope_length)

    mid_y = m_to_idx(width) // 2

    def add_step(start_x, end_x, mid_y, height):
        half_width = step_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at the end of the spawn area
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    cur_height = 0.1

    for i in range(6):  # Set up 6 steps
        next_height = cur_height + np.random.uniform(step_height_min, step_height_max) * difficulty
        add_step(cur_x, cur_x + step_length, mid_y, next_height)

        # Put goal in the center of the step
        goals[i+1] = [cur_x + step_length / 2, mid_y]

        # Update current position and height for next step
        cur_x += step_length + slope_length
        cur_height = next_height
    
    # Add final goal at the end of the course
    final_goal_x = cur_x + m_to_idx(0.5)
    goals[-1] = [final_goal_x, mid_y]

    return height_field, goals