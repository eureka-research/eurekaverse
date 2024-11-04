import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Combination of narrow and wide platforms with slight elevation changes for the robot to balance, climb, and navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Dimensions of platforms and gaps
    base_platform_length = 1.2 - 0.2 * difficulty
    base_platform_width = np.random.uniform(0.6, 1.2)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.25 + 0.3 * difficulty
    base_gap_length = 0.5 + 0.5 * difficulty
    base_gap_length = m_to_idx(base_gap_length)

    def add_platform(start_x, end_x, mid_y, width, height):
        half_width = m_to_idx(width) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    mid_y = m_to_idx(width) // 2

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at spawn

    last_x = spawn_length
    for i in range(1, 8):
        platform_length = m_to_idx(base_platform_length + 0.1 * difficulty * (i % 2))
        platform_width = m_to_idx(base_platform_width + 0.3 * difficulty * (i % 2))
        platform_height = np.random.uniform(platform_height_min, platform_height_max)

        if i % 2 == 0:
            current_gap_length = int(base_gap_length * 0.7)
        else:
            current_gap_length = base_gap_length

        start_x = last_x + current_gap_length
        end_x = start_x + platform_length
        dy = np.random.randint(-m_to_idx(0.2), m_to_idx(0.2))
        mid_platform_y = mid_y + dy

        add_platform(start_x, end_x, mid_platform_y, platform_width, platform_height)

        goals[i] = [start_x + (platform_length) / 2, mid_platform_y]

        last_x = end_x

    return height_field, goals