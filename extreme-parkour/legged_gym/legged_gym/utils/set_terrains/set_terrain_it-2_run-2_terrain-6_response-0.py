import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Mixed terrain with platforms, slopes, and ridges for the robot to climb and jump across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length = 0.8 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.4)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.3 + 0.4 * difficulty
    slope_height_min, slope_height_max = 0.05 + 0.1 * difficulty, 0.2 + 0.3 * difficulty
    ridge_height = 0.1 + 0.2 * difficulty
    gap_length = 0.2 + 0.4 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_slope(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slope = np.linspace(0, height, num=x2-x1)
        slope = slope[:, None]  # Add a dimension for broadcasting to y
        height_field[x1:x2, y1:y2] = slope

    def add_ridge(center_x, mid_y, height):
        half_width = platform_width // 2
        half_length = platform_length // 2
        x1, x2 = center_x - half_length, center_x + half_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = -0.2, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Set remaining area to be a pit
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    platform_count = 0
    while platform_count < 6 and cur_x < m_to_idx(length) - platform_length - gap_length:
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        if platform_count % 3 == 0 and platform_count <= 3:  # Adding platforms
            platform_height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height)
            cur_x += platform_length + dx + gap_length

        elif platform_count % 3 == 1 or platform_count == 3:  # Adding slopes
            slope_height = np.random.uniform(slope_height_min, slope_height_max)
            add_slope(cur_x, cur_x + platform_length + dx, mid_y + dy, slope_height)
            cur_x += platform_length + dx + gap_length

        else:  # Adding ridges
            add_ridge(cur_x, mid_y + dy, ridge_height)
            cur_x += platform_length + dx + gap_length

        goals[platform_count + 1] = [cur_x - gap_length//2, mid_y + dy]
        platform_count += 1

    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(1), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals