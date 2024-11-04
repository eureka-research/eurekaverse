import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Series of ramps and steps with narrow passages for the robot to navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define obstacle parameters
    ramp_length = 2.0 - 1.0 * difficulty
    ramp_length = m_to_idx(ramp_length)
    height_min, height_max = 0.1 + 0.1 * difficulty, 0.4 + 0.6 * difficulty
    
    step_length = 0.6
    step_length = m_to_idx(step_length)
    step_height = 0.2 * difficulty
    gap_length = 1.0
    gap_length = m_to_idx(gap_length)
    
    narrow_passage_width = 0.4 + 0.4 * (1 - difficulty)
    narrow_passage_width = m_to_idx(narrow_passage_width)

    mid_y = m_to_idx(width) // 2

    def add_ramp(start_x, end_x, mid_y, height):
        half_width = ramp_length // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slope = height / (end_x - start_x)
        for x in range(x1, x2):
            height_field[x, y1:y2] = (x - x1) * slope
    
    def add_steps(start_x, end_x, mid_y, step_count, height):
        half_width = step_length // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        step_height = height / step_count
        for step in range(step_count):
            start_step_x = x1 + step * step_length
            end_step_x = start_step_x + step_length
            height_field[start_step_x:end_step_x, y1:y2] = step * step_height

    def add_narrow_passage(start_x, end_x, mid_y):
        y1, y2 = mid_y - narrow_passage_width // 2, mid_y + narrow_passage_width // 2
        height_field[start_x:end_x, y1:y2] = 0
        
    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    height = np.random.uniform(height_min, height_max)
    
    add_ramp(cur_x, cur_x + ramp_length, mid_y, height)
    goals[1] = [cur_x + ramp_length // 2, mid_y]
    cur_x += ramp_length + gap_length
    
    add_steps(cur_x, cur_x + m_to_idx(3), mid_y, 3, step_height)
    goals[2] = [cur_x + m_to_idx(1.5), mid_y]
    cur_x += m_to_idx(3) + gap_length
    
    height = np.random.uniform(height_min, height_max)
    add_ramp(cur_x, cur_x + ramp_length, mid_y, -height)
    goals[3] = [cur_x + ramp_length // 2, mid_y]
    cur_x += ramp_length + gap_length
   
    add_narrow_passage(cur_x, cur_x + ramp_length, mid_y)
    goals[4] = [cur_x + ramp_length // 2, mid_y]
    cur_x += ramp_length + gap_length
    
    add_steps(cur_x, cur_x + m_to_idx(3), mid_y, 3, -step_height)
    goals[5] = [cur_x + m_to_idx(1.5), mid_y]
    cur_x += m_to_idx(3) + gap_length
    
    height = np.random.uniform(height_min, height_max)
    add_ramp(cur_x, cur_x + ramp_length, mid_y, height)
    goals[6] = [cur_x + ramp_length // 2, mid_y]
    cur_x += ramp_length + gap_length
    
    goals[7] = [cur_x + m_to_idx(1.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals