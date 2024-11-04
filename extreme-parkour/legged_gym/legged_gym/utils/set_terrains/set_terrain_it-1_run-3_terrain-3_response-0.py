import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Narrow ledges with alternating heights for the robot to balance and navigate across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define parameters for platforms and gaps
    platform_length_min = 0.8 - 0.25 * difficulty
    platform_length_max = 1.2 - 0.1 * difficulty
    platform_width = 0.4 + 0.05 * difficulty
    platform_height_min = 0.0 + 0.2 * difficulty
    platform_height_max = 0.1 + 0.3 * difficulty
    gap_length_min = 0.1 + 0.05 * difficulty
    gap_length_max = 0.3 + 0.2 * difficulty

    platform_length_min, platform_length_max = m_to_idx([platform_length_min, platform_length_max])
    platform_width = m_to_idx(platform_width)
    gap_length_min, gap_length_max = m_to_idx([gap_length_min, gap_length_max])

    mid_y = m_to_idx(width) // 2
    half_width = platform_width // 2

    def add_platform(start_x, end_x, mid_y, height):
        """Adds a platform with a specified height."""
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[start_x:end_x, y1:y2] = height

    dx_offset = m_to_idx(0.1)
    dy_offset_min, dy_offset_max = m_to_idx([-0.2, 0.2])

    # Set spawn area to flat ground and the first goal
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(6):
        platform_length = np.random.randint(platform_length_min, platform_length_max)
        height = np.random.uniform(platform_height_min, platform_height_max)

        dy_offset = np.random.randint(dy_offset_min, dy_offset_max)
        add_platform(cur_x, cur_x + platform_length, mid_y + dy_offset, height)

        # Place goal at the middle of the platform
        goals[i+1] = [cur_x + platform_length // 2, mid_y + dy_offset]

        # Add a gap before the next platform
        gap_length = np.random.randint(gap_length_min, gap_length_max)
        cur_x += platform_length + gap_length

    # Ensure the final section is reachable
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals