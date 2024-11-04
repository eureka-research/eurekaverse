import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Stepping stones and narrow beam traversal testing the quadruped's precision and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up stepping stone dimensions
    stone_length = 0.6
    stone_width = 0.4
    beam_length = 2.0
    beam_width = 0.4
    height_diff = 0.2 + 0.3 * difficulty
    stone_step_x = 1.5
    stone_step_y_variab = 0.6
    gap_length = 0.1 + 0.7 * difficulty

    stone_length = m_to_idx(stone_length)
    stone_width = m_to_idx(stone_width)
    beam_length = m_to_idx(beam_length)
    beam_width = m_to_idx(beam_width)
    height_diff = float(m_to_idx(height_diff))
    stone_step_x = m_to_idx(stone_step_x)
    stone_step_y_variab = m_to_idx(stone_step_y_variab)
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    # Helper function for adding a stone
    def add_stone(x, y, height):
        half_length = stone_length // 2
        half_width = stone_width // 2
        height_field[x - half_length:x + half_length, y - half_width:y + half_width] = height

    # Helper function for adding a beam
    def add_beam(x, start_y, end_y, height):
        y1, y2 = start_y, end_y
        height_field[x:x + beam_length, y1:y2] = height

    # Set flats and first goal at spawn point
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(4):  # Place 4 stepping stones first
        cur_y = mid_y + random.choice([-stone_step_y_variab, stone_step_y_variab])
        add_stone(cur_x, cur_y, height_diff * (i % 2))
        goals[i + 1] = [cur_x, cur_y]

        # Add gap between stones
        cur_x += stone_step_x + gap_length
    
    for i in range(2):  # Place 2 beams, one horizontal and one vertical
        if i == 0:
            add_beam(cur_x, mid_y - beam_width // 2, mid_y + beam_width // 2, height_diff * 2)
            goals[5 + i] = [cur_x + beam_length // 2, mid_y]
        else:
            add_beam(cur_x, mid_y - beam_width // 2 - beam_length // 2, mid_y - beam_width // 2 + beam_length // 2, height_diff * 3)
            goals[5 + i] = [cur_x, mid_y - beam_width]

        cur_x += beam_length + gap_length
    
    # Add final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals