import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Narrow balance beams at varying heights and gaps for the robot to traverse."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set balance beam dimensions
    beam_width = 0.4  # minimum width of the balance beam
    beam_width_idx = m_to_idx(beam_width)
    beam_length = 2.0 - 0.3 * difficulty   # varying length of the beam based on difficulty
    beam_length_idx = m_to_idx(beam_length)
    max_beam_height = 0.6  # max height of a balance beam can be 0.6 meters
    gap_length_idx = m_to_idx(0.3 + 0.4 * difficulty)  # gaps get larger as difficulty increases

    def add_beam(start_x, end_x, mid_y, height):
        half_width_idx = beam_width_idx // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width_idx, mid_y + half_width_idx
        height_field[x1:x2, y1:y2] = height

    mid_y = m_to_idx(width) // 2
    
    # Set spawn area to flat ground
    spawn_length_idx = m_to_idx(2)
    height_field[0:spawn_length_idx, :] = 0
    
    # Put first goal at spawn
    goals[0] = [spawn_length_idx - m_to_idx(0.5), mid_y]
    
    cur_x = spawn_length_idx

    for i in range(6):
        # Determine the height of the current beam (height gets taller with difficulty)
        beam_height = max_beam_height * (i / 6 * difficulty)
        
        # Add the balance beam to the height_field
        add_beam(cur_x, cur_x + beam_length_idx, mid_y, beam_height)

        # Set goal for robot in the middle of the beam
        goals[i + 1] = [cur_x + beam_length_idx // 2, mid_y]

        # Add gap to the next beam
        cur_x += beam_length_idx + gap_length_idx

    # Add final goal after last beam, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals