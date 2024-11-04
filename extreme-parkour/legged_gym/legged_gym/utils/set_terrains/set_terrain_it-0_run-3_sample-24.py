import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Obstacle course focuses on a zigzag path with narrow steps to test lateral agility and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform dimensions - steps are much narrower but long, height increases with difficulty
    step_length = 0.8 - 0.3 * difficulty
    step_length = m_to_idx(step_length)
    step_width = np.random.uniform(0.4, 0.7)
    step_width = m_to_idx(step_width)
    step_height_min, step_height_max = 0.1 + 0.2 * difficulty, 0.1 + 0.3 * difficulty

    mid_y = m_to_idx(width) // 2

    # Helper function to add a step
    def add_step(start_x, end_x, start_y, end_y, height):
        height_field[start_x:end_x, start_y:end_y] = height
        
    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    step_direction = 1  # 1 means moving towards positive y, -1 means negative y

    for i in range(6):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        start_y = mid_y + step_direction * (step_width // 2 + dy)
        end_y = start_y + step_direction * step_width
        
        step_height = np.random.uniform(step_height_min, step_height_max)
        add_step(cur_x, cur_x + step_length, start_y, end_y, step_height)
        
        # Place the goal at the center of the step
        goal_x = cur_x + step_length // 2
        goal_y = (start_y + end_y) // 2
        goals[i + 1] = [goal_x, goal_y]
        
        cur_x += step_length + m_to_idx(0.2)  # Space between consecutive steps
        step_direction *= -1  # Switch direction for zigzag pattern
        
    # Add final goal behind the last step, filling in remaining space
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals