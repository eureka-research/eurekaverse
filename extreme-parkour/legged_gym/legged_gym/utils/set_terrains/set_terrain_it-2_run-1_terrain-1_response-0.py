import numpy as np
import random

def set_terrain_harder(length, width, field_resolution, difficulty):
    """Series of taller platforms and longer gaps for the robot to navigate by jumping and climbing."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    mid_y = m_to_idx(width) // 2

    # Define platform parameters
    platform_length = 0.8 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.3)  # Slightly varied width to increase difficulty
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.2 + 0.4 * difficulty, 0.5 + 0.7 * difficulty
    gap_length = 0.3 + 0.8 * difficulty
    gap_length = m_to_idx(gap_length)

    def add_platform(x_start, x_end, y_mid, height):
        half_width = platform_width // 2
        x1, x2 = x_start, x_end
        y1, y2 = y_mid - half_width, y_mid + half_width
        height_field[x1:x2, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Add the first platform
    cur_x = spawn_length
    platform_height = random.uniform(platform_height_min, platform_height_max)
    add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)
    goals[1] = [cur_x + platform_length // 2, mid_y]
    cur_x += platform_length + gap_length

    for i in range(2, 7):
        dx = random.randint(-m_to_idx(0.1), m_to_idx(0.1))
        dy = random.randint(-m_to_idx(0.4), m_to_idx(0.4))
        platform_height = random.uniform(platform_height_min, platform_height_max)
        add_platform(cur_x + dx, cur_x + platform_length + dx, mid_y + dy, platform_height)
        goals[i] = [cur_x + platform_length // 2 + dx, mid_y + dy]
        cur_x += platform_length + gap_length + dx

    # Add final goal area
    height_field[cur_x:, :] = -1.0  # Adding a pit up to the end
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    return height_field, goals