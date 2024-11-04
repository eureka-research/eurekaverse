import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Curved narrow beams with varying gaps to test balance, agility, and precise navigation."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define dimensions
    beam_width = 0.2 + 0.2 * difficulty  # Wider beams at lower difficulty
    beam_height = 0.2 + 0.4 * difficulty  # Taller beams at higher difficulty
    gap_width = 0.2 + 0.5 * difficulty  # Wider gaps at higher difficulty
    curve_offset = 0.5 + 0.4 * difficulty  # Larger curves at higher difficulty
    beam_length = 1.0  # Constant length for beams

    beam_width = m_to_idx(beam_width)
    beam_height = m_to_idx(beam_height)
    gap_width = m_to_idx(gap_width)
    curve_offset = m_to_idx(curve_offset)
    beam_length = m_to_idx(beam_length)

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, y_position, height):
        y1, y2 = y_position - beam_width // 2, y_position + beam_width // 2
        height_field[start_x:end_x, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    cur_y = mid_y

    for i in range(7):
        start_x = cur_x
        end_x = cur_x + beam_length
        beam_height_val = np.random.uniform(beam_height - beam_height // 2, beam_height + beam_height // 2)
        
        add_beam(start_x, end_x, cur_y, beam_height_val)
        # Set goal in middle of the current beam
        goals[i + 1] = [(start_x + end_x) / 2, cur_y]
        
        # Update current position
        cur_x = end_x + gap_width
        if i % 2 == 0:
            cur_y = cur_y + curve_offset
        else:
            cur_y = cur_y - curve_offset

        # Ensure within bounds
        if cur_y - beam_width < 0:
            cur_y = beam_width
        elif cur_y + beam_width > m_to_idx(width):
            cur_y = m_to_idx(width) - beam_width

    # Final area to flat ground
    final_area_length = m_to_idx(1)
    height_field[cur_x:cur_x + final_area_length, :] = 0
    goals[-1] = [cur_x + final_area_length // 2, cur_y]

    return height_field, goals