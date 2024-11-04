import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Series of stepping stones of varying widths combined with ascending and descending platforms traversing pits."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_width_min = 0.4 + 0.1 * difficulty
    platform_width_max = 0.6 + 0.2 * difficulty
    platform_length_min = 0.4 + 0.1 * difficulty
    platform_length_max = 1.0 + 0.3 * difficulty
    step_height_min = 0.05 * difficulty
    step_height_max = 0.3 * difficulty
    gap_length_min = 0.2
    gap_length_max = 0.5 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = m_to_idx(np.random.uniform(platform_width_min, platform_width_max)) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = m_to_idx(-0.1), m_to_idx(0.1)
    dy_min, dy_max = m_to_idx(-0.2), m_to_idx(0.2)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Add platforms
    cur_x = spawn_length
    current_height = 0

    for i in range(7):
        platform_length = m_to_idx(np.random.uniform(platform_length_min, platform_length_max))
        current_gap = m_to_idx(np.random.uniform(gap_length_min, gap_length_max))
        next_height = current_height + np.random.uniform(step_height_min, step_height_max) * (-1 if i % 2 == 0 else 1)
        
        add_platform(cur_x, cur_x + platform_length, mid_y, current_height)
        
        goals[i + 1] = [cur_x + platform_length / 2, mid_y]

        cur_x += platform_length + current_gap
        current_height = next_height

    # Add final goal beyond last step
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals