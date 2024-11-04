import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Series of narrow beams and wide planks to test the quadruped's balance and precise foot placement.”

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    def add_beam(start_x, length, start_y, width, height):
        """Adds a narrow beam to the height field."""
        x1, x2 = start_x, start_x + m_to_idx(length)
        y1, y2 = start_y - m_to_idx(width // 2), start_y + m_to_idx(width // 2) 
        height_field[x1:x2, y1:y2] = height

    def add_plank(start_x, length, start_y, width, height):
        """Adds a wider plank to the height field."""
        x1, x2 = start_x, start_x + m_to_idx(length)
        y1, y2 = start_y - m_to_idx(width // 2), start_y + m_to_idx(width // 2) 
        height_field[x1:x2, y1:y2] = height

    beam_length = 1.0 - 0.2 * difficulty
    beam_width = 0.2  # Always fixed
    plank_length = 1.5 
    plank_width = 1.5 - 0.5 * difficulty
    obstacle_height = 0.1 + 0.2 * difficulty

    spawn_length = m_to_idx(2)
    mid_y = m_to_idx(width) // 2
    
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    height_field[0:spawn_length, :] = 0  # spawn area

    cur_x = spawn_length
    num_obstacles = 6

    for i in range(3):
        # Add beams
        add_beam(cur_x, beam_length, mid_y, beam_width, obstacle_height)
        goals[i*2+1] = [cur_x + m_to_idx(beam_length / 2), mid_y]
        cur_x += m_to_idx(beam_length) + m_to_idx(0.3 + 0.1 * difficulty)

        # Add planks
        add_plank(cur_x, plank_length, mid_y, plank_width, obstacle_height)
        goals[(i+1)*2] = [cur_x + m_to_idx(plank_length / 2), mid_y]
        cur_x += m_to_idx(plank_length) + m_to_idx(0.3 + 0.1 * difficulty)

    goals[7] = [cur_x, mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals