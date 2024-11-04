import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Alternate moving platforms and stepping stones across a pit for the robot to jump and balance"""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up moving platform and stepping stone dimensions
    platform_length = 0.8 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 0.8 + 0.3 * difficulty  # Decrease width for harder steps
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.3 + 0.25 * difficulty
    gap_length = 0.5 + 0.4 * difficulty  # Increase gap length with difficulty
    gap_length = m_to_idx(gap_length)

    stepping_stone_length = 0.4  # Small stepping stones
    stepping_stone_length = m_to_idx(stepping_stone_length)
    stepping_stone_width = stepping_stone_length
    stepping_stone_height = 0.05 + 0.2 * difficulty  # Increase height with difficulty

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_stepping_stone(x, y):
        half_length = stepping_stone_length // 2
        half_width = stepping_stone_width // 2
        x1, x2 = x - half_length, x + half_length
        y1, y2 = y - half_width, y + half_width
        height_field[x1:x2, y1:y2] = stepping_stone_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at the end of the spawn area

    cur_x = spawn_length
    for i in range(3):  # Set up 3 moving platforms
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
        goals[i * 2 + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        cur_x += platform_length + dx + gap_length

        # Adding stepping stones in between
        for j in range(2):
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)
            stone_x = cur_x + j * stepping_stone_length * 2
            stone_y = mid_y + dy
            add_stepping_stone(stone_x, stone_y)
            goals[i * 2 + 2] = [stone_x, stone_y]

        cur_x += stepping_stone_length * 2

    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals