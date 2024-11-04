import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Narrow curbs and raised beams to test balance and navigation."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up dimensions of the curbs and beams
    curb_length = 1.0 - 0.4 * difficulty
    curb_length = m_to_idx(curb_length)
    curb_width = np.random.uniform(0.5, 1.2)
    curb_width = m_to_idx(curb_width)
    curb_height = 0.1 + 0.3 * difficulty
    curb_height = m_to_idx(curb_height)
    
    beam_length = 1.2 - 0.5 * difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = np.random.uniform(0.3, 0.5)
    beam_width = m_to_idx(beam_width)
    beam_height_min, beam_height_max = 0.2 + 0.2 * difficulty, 0.4 + 0.2 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_curb(start_x, end_x, mid_y):
        half_width = curb_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = curb_height

    def add_beam(start_x, mid_y, height):
        half_width = beam_width // 2
        end_x = start_x + beam_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[start_x:end_x, y1:y2] = height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Concrete curbs and beams alternating pattern
    cur_x = spawn_length
    for i in range(4):  # Set up 4 curbs
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_curb(cur_x, cur_x + curb_length + dx, mid_y + dy)

        # Put goal on the curb
        goals[2*i+1] = [cur_x + (curb_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += curb_length + dx + m_to_idx(0.2)

        beam_height = np.random.uniform(beam_height_min, beam_height_max)
        add_beam(cur_x, mid_y, beam_height)

        # Put goal in the center of the beam
        goals[2*i+2] = [cur_x + beam_length / 2, mid_y]

        # Add gap
        cur_x += beam_length + m_to_idx(0.3)
    
    # Add final goal behind the last beam, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals