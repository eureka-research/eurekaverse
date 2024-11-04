import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Series of staggered platforms for quadruped to jump, balance, and navigate through."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length_min, platform_length_max = 1.0 - 0.2 * difficulty, 1.4 - 0.1 * difficulty
    platform_width_min, platform_width_max = 0.8, 1.2
    height_variation_min, height_variation_max = 0.0 + 0.1 * difficulty, 0.3 + 0.2 * difficulty

    gap_length_min, gap_length_max = 0.1 + 0.4 * difficulty, 0.3 + 0.5 * difficulty

    def add_platform(x, y, length, width, height):
        x1, x2 = m_to_idx([x, x + length])
        y1, y2 = m_to_idx([y - width / 2, y + width / 2])
        height_field[x1:x2, y1:y2] = height

    # Set initial flat area for spawning.
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0.0
    goals[0] = [spawn_length - m_to_idx(0.5), m_to_idx(width) // 2]

    # Starting point for placing obstacles.
    cur_x = 2
    cur_y = m_to_idx(width) // 2

    for i in range(1, 8):  # Create 7 platforms
        platform_length = np.random.uniform(platform_length_min, platform_length_max)
        platform_width = np.random.uniform(platform_width_min, platform_width_max)
        platform_height = np.random.uniform(height_variation_min, height_variation_max)

        # Stagger platforms to create a non-linear path
        if i % 2 == 0:
            cur_y = m_to_idx(width) // 2 - m_to_idx(1)
        else:
            cur_y = m_to_idx(width) // 2 + m_to_idx(1)

        add_platform(cur_x, cur_y, platform_length, platform_width, platform_height)

        # Place goal in the center of the current platform
        goals[i] = [cur_x + m_to_idx(platform_length) // 2, cur_y]

        # Move to the starting x point of the next platform
        cur_x += m_to_idx(platform_length) + np.random.randint(m_to_idx(gap_length_min), m_to_idx(gap_length_max))

    return height_field, goals