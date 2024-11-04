import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Narrow beams extend over gaps for the quadruped to walk across, testing precision and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    
    # Beam and gap dimensions, scaling with difficulty
    beam_length = 1.0 - 0.2 * difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = 0.4 + 0.12 * difficulty  # Making sure beam is narrow but within safe bounds
    beam_width = m_to_idx(beam_width)
    beam_height = 0.1 + 0.3 * difficulty  # Height of beams goes higher with difficulty
    gap_length = 0.2 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)

    # Quadruped spawn in the center on flat ground
    spawn_length = m_to_idx(2)
    mid_y = m_to_idx(width) // 2

    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at the end of the spawn area

    def add_beam(start_x, end_x, mid_y, width, height):
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    cur_x = spawn_length
    for i in range(6):  # 6 beams to be placed
    
        # Randomly decide y-offset for beam placement, making sure they don't overlap significantly
        dy_min, dy_max = -0.4, 0.4
        dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)
        dy = np.random.randint(dy_min, dy_max)
        
        add_beam(cur_x, cur_x + beam_length, mid_y + dy, beam_width, beam_height)

        # Place goals on each beam
        goals[i + 1] = [cur_x + beam_length // 2, mid_y + dy]

        # Add gap
        cur_x += beam_length + gap_length

    # Final section gently slopes down to the finishing platform
    final_length = m_to_idx(1)
    final_slope = np.linspace(beam_height, 0, final_length)
    height_field[cur_x:cur_x + final_length, mid_y - beam_width // 2:mid_y + beam_width // 2] = final_slope
    goals[-2] = [cur_x + final_length // 2, mid_y]

    # Put last goal at the end of the course
    goals[-1] = [cur_x + final_length + m_to_idx(0.5), mid_y]

    return height_field, goals