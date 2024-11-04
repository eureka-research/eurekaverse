import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Narrow paths and pits for the robot to carefully navigate through."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    path_width_min = 0.4
    path_width_max = 1.6 - 1.2 * difficulty
    path_width = np.random.uniform(path_width_min, path_width_max)
    
    pit_width_min = 0.8
    pit_width_max = 2.0
    pit_width = np.random.uniform(pit_width_min, pit_width_max)

    mid_y = m_to_idx(width) // 2

    def add_narrow_path(start_x, end_x, mid_y, path_width):
        half_width = m_to_idx(path_width) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = 0.0

    def add_pit(start_x, end_x, mid_y, pit_width):
        half_width = m_to_idx(pit_width) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = -1.0

    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(4):  # Set up 4 narrow paths and 4 pits alternately
        path_length = np.random.uniform(1.0, 2.0)
        path_length = m_to_idx(path_length)
        add_narrow_path(cur_x, cur_x + path_length, mid_y, path_width)
        goals[i*2 + 1] = [cur_x + path_length // 2, mid_y]

        cur_x += path_length

        pit_length = np.random.uniform(0.5, 1.5)
        pit_length = m_to_idx(pit_length)
        add_pit(cur_x, cur_x + pit_length, mid_y, pit_width)
        goals[i*2 + 2] = [cur_x + pit_length // 2, mid_y]

        cur_x += pit_length

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals