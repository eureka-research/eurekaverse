import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Narrow balance beams at varying heights for the robot to traverse."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set balance beam dimensions
    beam_length = 0.4 + 0.6 * difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = 0.4  # This is within the allowed narrow width for precision traversal
    beam_width = m_to_idx(beam_width)
    beam_height_min, beam_height_max = 0.1, 0.4 + 0.6 * difficulty

    def add_beam(start_x, mid_y, height):
        half_width = beam_width // 2
        x1, x2 = start_x, start_x + beam_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    mid_y = m_to_idx(width) // 2
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(7):  # There will be 7 beams to traverse
        height = np.random.uniform(beam_height_min, beam_height_max)
        add_beam(cur_x, mid_y, height)
        goals[i+1] = [cur_x + beam_length / 2, mid_y]

        cur_x += beam_length + m_to_idx(0.1)  # Adding a small gap between beams

    return height_field, goals