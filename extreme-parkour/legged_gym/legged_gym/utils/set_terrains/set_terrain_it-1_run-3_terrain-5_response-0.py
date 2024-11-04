import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Elevated platforms with diagonal and rotating ramps for increased complexity and difficulty."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Ramp and platform dimensions
    platform_length_min, platform_length_max = 0.7, 1.0
    platform_height_min, platform_height_max = 0.2 * difficulty, 0.5 * difficulty
    ramp_slope_min, ramp_slope_max = 0.05 * difficulty, 0.1 * difficulty
    gap_length_min, gap_length_max = 0.2 * difficulty, 0.5 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = m_to_idx(0.8) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_ramp(start_x, end_x, mid_y, start_height, end_height):
        half_width = m_to_idx(0.8) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slope = np.linspace(start_height, end_height, num=x2-x1)
        height_field[x1:x2, y1:y2] = slope[:, None]

    current_x = m_to_idx(2)
    start_height = 0.0

    for i in range(6):
        platform_length = random.uniform(platform_length_min, platform_length_max)
        platform_length_idx = m_to_idx(platform_length)
        platform_height = random.uniform(platform_height_min, platform_height_max)
        add_platform(current_x, current_x + platform_length_idx, mid_y, start_height + platform_height)
        goals[i] = [current_x + platform_length_idx // 2, mid_y]
        current_x += platform_length_idx

        if i < 5:  # Only add ramps for the first 5 segments
            ramp_length = random.uniform(platform_length_min, platform_length_max)
            ramp_length_idx = m_to_idx(ramp_length)
            ramp_height = random.uniform(ramp_slope_min, ramp_slope_max)
            add_ramp(current_x, current_x + ramp_length_idx, mid_y, start_height + platform_height, start_height + platform_height + ramp_height)
            goals[i+1] = [current_x + ramp_length_idx // 2, mid_y]
            start_height += ramp_height
            current_x += ramp_length_idx

        gap_length = random.uniform(gap_length_min, gap_length_max)
        current_x += m_to_idx(gap_length)

    goals[7] = [current_x - gap_length // 2, mid_y]
    height_field[current_x:, :] = 0

    return height_field, goals