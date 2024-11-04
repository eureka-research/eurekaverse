import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Hurdle jumps coupled with narrow beams for balance testing."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set hurdle and beam dimensions
    hurdle_height_min = 0.1 + 0.25 * difficulty
    hurdle_height_max = 0.2 + 0.3 * difficulty
    hurdle_width = m_to_idx(1.0)
    
    beam_length = m_to_idx(1.5)
    beam_width = m_to_idx(0.4)
    beam_height = 0.05 + 0.15 * difficulty

    # Ensure narrow but traversable beams
    mid_y = m_to_idx(width) // 2

    def add_hurdle(start_x, end_x, mid_y):
        y1, y2 = mid_y - hurdle_width // 2, mid_y + hurdle_width // 2
        hurdle_height = np.random.uniform(hurdle_height_min, hurdle_height_max)
        height_field[start_x:end_x, y1:y2] = hurdle_height
    
    def add_beam(start_x, end_x, mid_y):
        y1, y2 = mid_y - beam_width // 2, mid_y + beam_width // 2
        height_field[start_x:end_x, y1:y2] = beam_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    # Obstacle course alternates between hurdles and beams
    for i in range(4):  # Two hurdles and two beams
        # Add hurdle
        hurdle_length = m_to_idx(1.0)
        add_hurdle(cur_x, cur_x + hurdle_length, mid_y)
        goals[2*i+1] = [cur_x + hurdle_length / 2, mid_y]
        cur_x += hurdle_length + m_to_idx(0.4)

        # Add beam
        add_beam(cur_x, cur_x + beam_length, mid_y)
        goals[2*i+2] = [cur_x + beam_length / 2, mid_y]
        cur_x += beam_length + m_to_idx(0.4)
    
    # Add final goal after obstacles
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals