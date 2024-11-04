import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Narrow beams with varying heights and orientations for balance and precise navigation."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up beam dimensions
    beam_width = 0.4  # The narrow dimension of the beam
    beam_length = 3.0  # The longer dimension of the beam
    beam_height_min, beam_height_max = 0.1, 0.4 * difficulty 

    beam_width = m_to_idx(beam_width)
    beam_length = m_to_idx(beam_length)
    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, y_pos, height):
        """Places a beam on the height_field at given position and with given dimensions."""
        half_width = beam_width // 2
        start_y = y_pos - half_width
        end_y = y_pos + half_width
        height_field[start_x:end_x, start_y:end_y] = height

    # Initial flat terrain/spawn area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at the end of the spawn area

    # Parameters for beam placement
    x_step = m_to_idx(1.5)
    beam_gap = m_to_idx(0.5)

    cur_x = spawn_length

    for i in range(6):  # Set up 6 beams
        beam_height = np.random.uniform(beam_height_min, beam_height_max)
        cur_y = mid_y + m_to_idx(np.random.uniform(-0.8, 0.8))  # Introduce slight variability in y-position

        add_beam(cur_x, cur_x + beam_length, cur_y, beam_height)
        goals[i+1] = [cur_x + beam_length // 2, cur_y]  # Goal in the center of the beam
        
        cur_x += beam_length + beam_gap

    # Final goal at the far end of the course
    goals[-1] = [cur_x + m_to_idx(1.0), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals