import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Series of varied height platforms with narrow connecting bridges and gaps for balance and jump skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform dimensions
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.5)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.15 + 0.35 * difficulty
    gap_length = 0.3 + 0.8 * difficulty  # Larger gaps for higher difficulty
    gap_length = m_to_idx(gap_length)

    # Helper function to add a platform
    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Initialize variables
    mid_y = m_to_idx(width) // 2
    cur_x = spawn_length
    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)
    obstacle_key_points = []

    # First path with higher platforms and narrow bridges
    for i in range(3):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
        goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        obstacle_key_points.append((cur_x + (platform_length + dx) / 2, mid_y + dy, platform_height_min))

        # Create the gap
        cur_x += platform_length + dx + gap_length

    # Second path with varied heights and tighter gaps
    for i in range(3, 6):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
        goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        obstacle_key_points.append((cur_x + (platform_length + dx) / 2, mid_y + dy, platform_height_max))

        # Create the gap
        cur_x += platform_length + dx + gap_length

    # Final goal behind the last platform
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals