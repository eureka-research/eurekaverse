import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Series of narrow beams for the robot to carefully navigate across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up beam dimensions
    beam_length = 2.0 - difficulty  # Beams get shorter with higher difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = 0.4 + 0.2 * difficulty  # The width of the beams, keeping it between 0.4m and 0.6m
    beam_width = m_to_idx(beam_width)
    beam_height = 0.2 + 0.3 * difficulty  # The height of the beams, increasing with difficulty
    gap_length = 0.4 + 0.6 * difficulty  # Gaps between beams

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, mid_y):
        y_half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - y_half_width, mid_y + y_half_width
        height_field[x1:x2, y1:y2] = beam_height

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
        add_beam(cur_x, cur_x + beam_length + dx, mid_y + dy)

        # Put goal in the center of the beam
        goals[i+1] = [cur_x + (beam_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += beam_length + dx + m_to_idx(gap_length)

    # Add final goal behind the last beam, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals