import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Series of narrow beams aligned with gaps in between for the robot to balance and traverse."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up beam and gap sizes based on difficulty
    beam_width_min, beam_width_max = 0.4 - 0.2 * difficulty, 0.8 - 0.3 * difficulty
    beam_width = np.random.uniform(beam_width_min, beam_width_max)
    beam_width = m_to_idx(beam_width)
    beam_height = 0.3 + 0.5 * difficulty
    gap_width = 0.2 + 0.6 * difficulty
    gap_width = m_to_idx(gap_width)

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, beam_width, mid_y):
        half_width = beam_width // 2
        x1 = start_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x1 + beam_width, y1:y2] = beam_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    for i in range(6):  # Set up 6 beams
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_beam(cur_x, beam_width + dx, mid_y + dy)

        # Put goal at the endpoint of each beam
        goals[i+1] = [cur_x + (beam_width + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += beam_width + dx + gap_width
    
    # Add final goal behind the last beam, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals