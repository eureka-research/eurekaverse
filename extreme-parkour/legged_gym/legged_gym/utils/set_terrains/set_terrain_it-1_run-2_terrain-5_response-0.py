import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Elevated platforms with narrow beams and gaps to test dexterity and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up obstacle dimensions
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)

    platform_width = np.random.uniform(0.8, 1.0)  # Narrower platforms
    platform_width = m_to_idx(platform_width)

    platform_height_min, platform_height_max = 0.2 + 0.3 * difficulty, 0.5 + 0.3 * difficulty
    gap_length = 0.5 + 0.7 * difficulty
    gap_length = m_to_idx(gap_length)

    beam_width = 0.2 + 0.2 * difficulty  # Narrow beams with increasing difficulty
    beam_width = m_to_idx(beam_width)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, start_y, end_y, height):
        height_field[start_x:end_x, start_y:end_y] = height

    cur_x = m_to_idx(2)
    height_field[0:cur_x, :] = 0  # Set spawn area to flat ground
    n_obstacles = 6

    # Initial goal at spawn area
    goals[0] = [cur_x - m_to_idx(0.5), mid_y]

    for i in range(n_obstacles):
        height = np.random.uniform(platform_height_min, platform_height_max)

        if i % 2 == 0:  # Add platforms
            end_x = cur_x + platform_length
            add_platform(cur_x, end_x, mid_y - platform_width // 2, mid_y + platform_width // 2, height)
            goals[i + 1] = [cur_x + platform_length // 2, mid_y]
            cur_x = end_x + gap_length

        else:  # Add narrow beams
            end_x = cur_x + platform_length
            add_platform(cur_x, end_x, mid_y - beam_width // 2, mid_y + beam_width // 2, height)
            goals[i + 1] = [cur_x + platform_length // 2, mid_y]
            cur_x = end_x + gap_length

    # Final goal position
    goals[-1] = [cur_x + m_to_idx(1), mid_y]

    return height_field, goals
