import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Urban-like terrain with steps, slopes, and narrow passages."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Conversion helpers
    len_idx = m_to_idx(length)
    wid_idx = m_to_idx(width)
    quad_length, quad_width = 0.645, 0.28

    mid_y = wid_idx // 2

    # Obstacle settings
    step_height = 0.1 + difficulty * 0.2
    max_slope_height = 0.05 + difficulty * 0.3
    narrow_width = quad_width + (0.4 + 0.2 * difficulty)

    def add_step(start_x, end_x, mid_y, step_h):
        half_width = m_to_idx(1.0) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = step_h

    def add_slope(start_x, end_x, start_h, end_h, mid_y):
        half_width = m_to_idx(1.0) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slope = np.linspace(start_h, end_h, x2 - x1)
        height_field[x1:x2, y1:y2] = slope[:, np.newaxis]

    def add_narrow_passage(start_x, end_x, mid_y, step_h):
        half_width = m_to_idx(narrow_width) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = step_h

    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    # Place the first step
    add_step(cur_x, cur_x + m_to_idx(2), mid_y, step_height)
    goals[1] = [cur_x + m_to_idx(1), mid_y]
    cur_x += m_to_idx(2)

    # Place a slope
    add_slope(cur_x, cur_x + m_to_idx(3), step_height, max_slope_height, mid_y)
    goals[2] = [cur_x + m_to_idx(1.5), mid_y]
    cur_x += m_to_idx(3)

    # Place a narrow passage
    add_narrow_passage(cur_x, cur_x + m_to_idx(2), mid_y, max_slope_height)
    goals[3] = [cur_x + m_to_idx(1), mid_y]
    cur_x += m_to_idx(2)

    # Place a downward slope
    add_slope(cur_x, cur_x + m_to_idx(3), max_slope_height, step_height, mid_y)
    goals[4] = [cur_x + m_to_idx(1.5), mid_y]
    cur_x += m_to_idx(3)

    # Place another step
    add_step(cur_x, cur_x + m_to_idx(2), mid_y, step_height)
    goals[5] = [cur_x + m_to_idx(1), mid_y]
    cur_x += m_to_idx(2)

    # Final slope to ground level
    add_slope(cur_x, cur_x + m_to_idx(3), step_height, 0.0, mid_y)
    goals[6] = [cur_x + m_to_idx(1.5), mid_y]
    cur_x += m_to_idx(3)

    goals[7] = [cur_x + m_to_idx(0.5), mid_y]

    return height_field, goals