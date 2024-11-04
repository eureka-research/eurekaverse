import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Series of stair-like steps for the robot to carefully climb up and down."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set step parameters based on difficulty
    step_height_increment = 0.05 * difficulty  # Increment for each step
    step_height = 0.05 + step_height_increment  # Initial step height
    step_length = 1.0  # Each step is 1 meter in length
    step_length_idx = m_to_idx(step_length)
    
    mid_y = m_to_idx(width) // 2  # Middle of the width for aligning steps

    def add_step(start_x, end_x, center_y, height):
        half_width = m_to_idx(1.0) // 2  # 1 meter wide steps
        x1, x2 = start_x, end_x
        y1, y2 = center_y - half_width, center_y + half_width
        height_field[x1:x2, y1:y2] = height

    # Set up spawning area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # Place first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]
    
    cur_x = spawn_length
    step_count = 0
    
    while cur_x + step_length_idx < m_to_idx(length):
        add_step(cur_x, cur_x + step_length_idx, mid_y, step_height)
        goals[step_count % 8] = [cur_x + step_length_idx // 2, mid_y]
        step_count += 1
        step_height = step_height + step_height_increment if step_count % 2 == 0 else step_height - step_height_increment
        cur_x += step_length_idx
    
    # Ensure the last goal is well within the bounds of the terrain
    goals[-1] = [m_to_idx(length) - m_to_idx(0.5), mid_y]

    return height_field, goals