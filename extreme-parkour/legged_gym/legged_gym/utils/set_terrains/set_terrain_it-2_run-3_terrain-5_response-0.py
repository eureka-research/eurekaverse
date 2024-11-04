import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Staggered narrow beams with changing heights to test balance and precise movement."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Beam dimensions
    beam_length = 0.9 + 0.1 * difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = 0.4 + 0.04 * difficulty
    beam_width = m_to_idx(beam_width)
    min_height = 0.1 * difficulty
    max_height = 0.5 * difficulty
    beam_gap = 0.1 * difficulty
    beam_gap = m_to_idx(beam_gap)
    
    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, y, height):
        x1, x2 = start_x, end_x
        y1, y2 = y - beam_width // 2, y + beam_width // 2
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = -0.1, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(6):  # Place 6 beams
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        height = np.random.uniform(min_height, max_height)
        add_beam(cur_x, cur_x + beam_length + dx, mid_y + dy, height)

        # Place goal in the center of the beam
        goals[i+1] = [cur_x + (beam_length + dx) / 2, mid_y + dy]

        # Add gap after beam
        cur_x += beam_length + dx + beam_gap
    
    # Place the final goal at the end
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals