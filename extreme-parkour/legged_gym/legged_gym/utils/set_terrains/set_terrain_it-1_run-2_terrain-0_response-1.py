import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Elevated platforms with varying gaps and heights to test jumping and landing precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define platform properties
    platform_length = 0.9 + 0.3 * difficulty  # Platform length increases with difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 1.0  # Fixed width for all platforms
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.4 * difficulty, 0.2 + 0.6 * difficulty  # Heights increase with difficulty
    gap_length_min = 0.5  # Minimum gap length
    gap_length_max = 1.2 * difficulty  # Maximum gap length increases with difficulty
    gap_length = [m_to_idx(gap_length_min), m_to_idx(gap_length_max)]

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x, cur_y = spawn_length, mid_y
    previous_height = 0  # Initial height at the spawn point

    for i in range(7):  # Create 7 platforms with increasing complexity
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        gap = np.random.randint(gap_length[0], gap_length[1])

        # Calculate the next platform's starting x position
        cur_x += gap

        add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)

        # Put goal in the center of the current platform
        goals[i + 1] = [cur_x + platform_length // 2, mid_y]

        # Move to the end of the current platform for the next iteration
        cur_x += platform_length
        previous_height = platform_height

    # Add final goal behind the last platform
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals