import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Varying-height steps and platforms for the robot to navigate and step over."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Setup platform dimensions
    platform_length_base = 0.8  # Base length of platform
    platform_length_variation = 0.3 * difficulty
    platform_width = np.random.uniform(0.8, 1.2)  # Narrower and slightly varied platform width
    platform_width = m_to_idx(platform_width)
    step_height_min, step_height_max = 0.05 * difficulty, 0.3 * difficulty
    gap_length_base = 0.2
    gap_length_variation = 0.5 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2  # Reduced polarity variation in y direction for a consistent path
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Add platforms and steps
    cur_x = spawn_length
    heights = [0.0]

    for i in range(7):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        platform_length = platform_length_base + (platform_length_variation * np.random.rand())
        platform_length = m_to_idx(platform_length)
        gap_length = gap_length_base + (gap_length_variation * np.random.rand())
        gap_length = m_to_idx(gap_length)

        step_height = np.random.uniform(step_height_min, step_height_max) * (-1 if i % 2 == 0 else 1)
        heights.append(heights[-1] + step_height)

        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, heights[-1])

        # Set goal in the center of the platform
        goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += platform_length + dx + gap_length

    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals