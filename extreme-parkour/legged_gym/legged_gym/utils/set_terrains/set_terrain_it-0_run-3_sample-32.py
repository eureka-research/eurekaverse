import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Series of hurdles with varying heights and a balance beam-like narrow obstacle."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up hurdle dimensions based on difficulty
    hurdle_height_min, hurdle_height_max = 0.1, 0.3
    hurdle_height = lambda diff: np.random.uniform(
        hurdle_height_min * (1 + diff), hurdle_height_max * (1 + diff)
    )
    hurdle_width = m_to_idx(0.5)
    balance_beam_width = m_to_idx(0.3)
    hurdle_gap = m_to_idx(2.0 - 1.5 * difficulty)  # Larger gap at higher difficulty

    mid_y = m_to_idx(width) // 2

    def add_hurdle(start_x, end_x, mid_y):
        half_width = hurdle_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height = hurdle_height(difficulty)
        height_field[x1:x2, y1:y2] = height

    def add_balance_beam(start_x, end_x, mid_y):
        half_width = balance_beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height = hurdle_height(difficulty) / 2  # Balance beam is lower than hurdles
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = m_to_idx(-0.2), m_to_idx(0.2)
    dy_min, dy_max = m_to_idx(-0.4), m_to_idx(0.4)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [m_to_idx(1), mid_y]  # Put first goal at spawn

    cur_x = spawn_length
    last_hurdle_end = cur_x

    # Set up 7 obstacles (6 hurdles + 1 balance beam)
    for i in range(6):  # First 6 hurdles
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_hurdle(cur_x + dx, cur_x + hurdle_width + dx, mid_y + dy)
        
        # Put goal past each hurdle
        goals[i + 1] = [cur_x + hurdle_width + dx + m_to_idx(0.5), mid_y + dy]
        
        # Update position for the next hurdle
        cur_x += hurdle_width + dx + hurdle_gap
        last_hurdle_end = cur_x

    # Add balance beam - final obstacle
    balance_beam_length = m_to_idx(1.0 + difficulty)
    add_balance_beam(last_hurdle_end + dx, last_hurdle_end + dx + balance_beam_length, mid_y)

    goals[-1] = [last_hurdle_end + dx + balance_beam_length + m_to_idx(0.5), mid_y]

    return height_field, goals