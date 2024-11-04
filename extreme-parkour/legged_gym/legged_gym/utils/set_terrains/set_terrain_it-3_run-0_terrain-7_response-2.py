import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Narrow paths and elevated platforms with small gaps for precise navigation and controlled jumps."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Path and platform dimensions
    path_length = 1.0 - 0.3 * difficulty
    platform_length = 1.0 - 0.2 * difficulty
    path_length, platform_length = m_to_idx(path_length), m_to_idx(platform_length)
    path_width = 0.4 + 0.2 * difficulty
    path_width, platform_width = m_to_idx(path_width), m_to_idx(1.6 - 0.6 * difficulty)
    max_height = 0.3 + 0.3 * difficulty
    gap_max = 0.2 + 0.4 * difficulty
    mid_y = m_to_idx(width) // 2

    def add_path(start_x, end_x, center_y, width, height):
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = center_y - half_width, center_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_platform(start_x, end_x, center_y, width, height):
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = center_y - half_width, center_y + half_width
        height_field[x1:x2, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # Initial goal at spawn point
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    last_height = 0

    for i in range(1, 7):
        if i % 2 == 0:
            gap = np.random.uniform(0.1, gap_max)
            gap = m_to_idx(gap)
            next_height = np.random.uniform(last_height, max_height)
            add_platform(cur_x + gap, cur_x + gap + platform_length, mid_y, platform_width, next_height)
            goals[i] = [cur_x + gap + platform_length // 2, mid_y]
            cur_x += gap + platform_length
        else:
            next_height = np.random.uniform(last_height, max_height)
            add_path(cur_x, cur_x + path_length, mid_y, path_width, next_height)
            goals[i] = [cur_x + path_length // 2, mid_y]
            cur_x += path_length

        last_height = next_height

    # Set final goal behind the last platform
    goals[7] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals