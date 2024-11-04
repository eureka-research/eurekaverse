import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Narrow balance beams, inclined platforms, and hopping gaps to test balance and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Constants sizing and initial setup
    balance_beam_width = m_to_idx(0.4)  # Narrower balance beam
    incline_length = m_to_idx(1.0)
    incline_height_range = [0.2 * difficulty, 0.4 * difficulty]
    gap_length = m_to_idx(0.3 * (1 + difficulty))  # Increased gap lengths with difficulty
    mid_y = m_to_idx(width) // 2

    def add_balance_beam(start_x, end_x, y_center):
        y1 = y_center - balance_beam_width // 2
        y2 = y_center + balance_beam_width // 2
        height_field[start_x:end_x, y1:y2] = 0.2 * difficulty  # Balance beam's height

    def add_incline_platform(start_x, end_x, y_center, incline_height):
        y1 = y_center - balance_beam_width // 2
        y2 = y_center + balance_beam_width // 2
        incline = np.linspace(0, incline_height, end_x-start_x)
        incline = incline[:, None]
        height_field[start_x:end_x, y1:y2] = incline

    cur_x = m_to_idx(2)  # Initial spawn area
    height_field[:cur_x, :] = 0
    goals[0] = [cur_x - m_to_idx(0.5), mid_y]

    obstacles = [
        {'type': 'balance_beam', 'length': m_to_idx(1.5)},
        {'type': 'gap', 'length': gap_length},
        {'type': 'incline', 'length': incline_length, 'height': np.random.uniform(*incline_height_range)},
        {'type': 'gap', 'length': gap_length},
        {'type': 'balance_beam', 'length': m_to_idx(2.0)},
        {'type': 'gap', 'length': gap_length},        
        {'type': 'incline', 'length': incline_length, 'height': np.random.uniform(*incline_height_range)}
    ]

    for i, obs in enumerate(obstacles):
        if obs['type'] == 'balance_beam':
            add_balance_beam(cur_x, cur_x + obs['length'], mid_y)
            goals[i + 1] = [cur_x + obs['length'] // 2, mid_y]

        elif obs['type'] == 'incline':
            add_incline_platform(cur_x, cur_x + obs['length'], mid_y, obs['height'])
            goals[i + 1] = [cur_x + obs['length'] // 2, mid_y]
        
        cur_x += obs['length']

    # Spread goals apart adequately
    cur_x += m_to_idx(0.5)
    goals[-1] = [cur_x, mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals