import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Narrow beams, inclines, declines, and small steps combined with narrow pathways for an increased challenge."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    
    beam_length = 1.0 - 0.3 * difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = np.random.uniform(0.4, 0.6)
    beam_width = m_to_idx(beam_width)
    step_height_min, step_height_max = 0.2 * difficulty, 0.3 * difficulty
    
    incline_start_height = 0.05
    incline_end_height = 0.2 + 0.4 * difficulty
    incline_length = 0.8
    incline_length = m_to_idx(incline_length)
    
    mid_y = m_to_idx(width) // 2
    
    def add_beam(start_x, end_x, mid_y):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = beam_height
        
    def add_incline(start_x, end_x, start_height, end_height, mid_y):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        incline = np.linspace(start_height, end_height, x2-x1)[:, None]
        height_field[x1:x2, y1:y2] = incline
        
    def add_steps(start_x, end_x, step_height, mid_y):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = np.arange(step_height, step_height*(x2-x1+1), step_height)[:, None]
        
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
    
    # Add inclined beam
    dx = np.random.randint(dx_min, dx_max)
    dy = np.random.randint(dy_min, dy_max)
    add_incline(cur_x, cur_x + incline_length + dx, incline_start_height, incline_end_height, mid_y + dy)
    goals[1] = [cur_x + incline_length // 2, mid_y + dy]
    cur_x += incline_length + dx + m_to_idx(0.2)
    
    # Add small steps
    steps_length = m_to_idx(1.6)
    add_steps(cur_x, cur_x + steps_length, m_to_idx(beam_height * 0.25), mid_y)
    goals[2] = [cur_x + steps_length // 2, mid_y]
    cur_x += steps_length + m_to_idx(0.2)
    
    # Add flat beams
    for i in range(3, 6):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        beam_height = np.random.uniform(step_height_min, step_height_max)
        add_beam(cur_x, cur_x + beam_length + dx, mid_y + dy)
        goals[i] = [cur_x + beam_length // 2, mid_y + dy]
        cur_x += beam_length + dx + m_to_idx(0.2)
    
    # Add decline beam
    add_incline(cur_x, cur_x + incline_length + dx, incline_end_height, incline_start_height, mid_y + dy)
    goals[6] = [cur_x + incline_length // 2, mid_y + dy]
    cur_x += incline_length + dx + m_to_idx(0.2)
    
    # Add final goal behind the last beam, fill in the remaining gap
    goals[7] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals