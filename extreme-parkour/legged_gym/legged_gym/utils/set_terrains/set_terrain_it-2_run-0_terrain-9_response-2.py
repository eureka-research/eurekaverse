import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Multi-complex obstacle course with narrow beams, wide platforms, slopes, and varied gaps."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length = 0.8 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width_min = 0.4
    platform_width_max = 1.5
    platform_height_min, platform_height_max = 0.0 + 0.2 * difficulty, 0.1 + 0.3 * difficulty
    gap_length_min = 0.1 + 0.4 * difficulty
    gap_length_max = 0.5 + 0.7 * difficulty
    gap_length_min = m_to_idx(gap_length_min)
    gap_length_max = m_to_idx(gap_length_max)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, y_center, width):
        half_width = m_to_idx(width) // 2
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[start_x:end_x, y_center - half_width:y_center + half_width] = platform_height

    def add_slope(start_x, end_x, y_center, width, direction):
        half_width = m_to_idx(width) // 2
        ramp_height = np.random.uniform(platform_height_min, platform_height_max)
        slope = np.linspace(0, ramp_height, end_x - start_x)[::direction]
        slope = slope[:, None]  # Add a dimension for broadcasting to y
        height_field[start_x:end_x, y_center - half_width:y_center + half_width] = slope

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    for i in range(6):
        platform_width = np.random.uniform(platform_width_min, platform_width_max)
        gap_length = np.random.randint(gap_length_min, gap_length_max)

        if i % 2 == 0:
            add_platform(cur_x, cur_x + platform_length, mid_y, platform_width)
        else:
            direction = 1 if i % 4 == 1 else -1
            add_slope(cur_x, cur_x + platform_length, mid_y, platform_width, direction)

        goals[i + 1] = [cur_x + platform_length // 2, mid_y]

        cur_x += platform_length + gap_length

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals