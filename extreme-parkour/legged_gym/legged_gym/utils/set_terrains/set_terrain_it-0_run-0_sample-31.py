import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Narrow beams and wide gaps for the robot to balance and jump across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up beam and gap dimensions
    beam_width = 0.4 + 0.4 * difficulty  # 0.4 to 0.8 meters wide beams
    beam_width = m_to_idx(beam_width)
    beam_height = 0.1 + 0.3 * difficulty  # 0.1 to 0.4 meters tall beams
    gap_length_min = 0.5
    gap_length_max = 2 + 2 * difficulty  # 0.5 to 4 meters wide gaps
    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, mid_y):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = beam_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    for i in range(6):  # Set up 6 beams and gaps
        gap_length = np.random.uniform(gap_length_min, gap_length_max)
        gap_length = m_to_idx(gap_length)
        
        add_beam(cur_x, cur_x + m_to_idx(1), mid_y)  # Beam with 1 meter length

        # Put goal at the center of the beam
        goals[i+1] = [cur_x + m_to_idx(0.5), mid_y]

        # Add gap
        cur_x += m_to_idx(1) + gap_length
    
    # Add final goal behind the last beam, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals