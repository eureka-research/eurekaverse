import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Stepping platforms at varying heights and widths for the quadruped to step or jump up and down different levels."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform dimensions variables
    base_platform_length = 1.5 - 0.5 * difficulty
    platform_length = m_to_idx(base_platform_length)
    platform_width_low, platform_width_high = 1.0, 1.5
    platform_height_min, platform_height_max = 0.1 + 0.1 * difficulty, 0.3 + 0.5 * difficulty
    gap_length = 0.2 + 0.8 * difficulty
    gap_length = m_to_idx(gap_length)

    height_field[:m_to_idx(2),:] = 0
    
    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, center_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = center_y - half_width, center_y + half_width
        height_field[x1:x2, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at spawn

    last_x = spawn_length
    for i in range(1, 8):
        platform_length = m_to_idx(base_platform_length + 0.2 * difficulty * (i % 2))
        platform_width = np.random.uniform(platform_width_low, platform_width_high)
        platform_width = m_to_idx(platform_width)
        platform_height = np.random.uniform(platform_height_min, platform_height_max)

        if i % 2 == 0:
            current_gap_length = int(gap_length * 0.7)
        else:
            current_gap_length = gap_length

        start_x = last_x + current_gap_length
        end_x = start_x + platform_length
        center_y = mid_y + np.random.choice([-1, 1]) * np.random.randint(0, m_to_idx(0.3))

        add_platform(start_x, end_x, center_y, platform_height)

        goals[i] = [start_x + (platform_length) / 2, center_y]

        last_x = end_x

    return height_field, goals