import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Complex course with elevated platforms, beams, and narrow paths to challenge the quadruped's agility and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Setup terrain specifics based on difficulty:
    platform_length = 1.2 - 0.4 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.4)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.4 * difficulty, 0.2 + 0.6 * difficulty
    balance_path_width = 0.35 + 0.1 * difficulty
    balance_path_width = m_to_idx(balance_path_width)
    gap_length = 0.15 + 0.85 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = platform_height

    def add_beam(start_x, end_x, mid_y, incline=False):
        half_width = balance_path_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        if incline:
            max_height = np.random.uniform(platform_height_max, platform_height_max + 0.15)
            beam_height = np.linspace(0, max_height, x2 - x1)
            height_field[x1:x2, y1:y2] = beam_height[:, None]
        else:
            beam_height = np.random.uniform(platform_height_min, platform_height_max)
            height_field[x1:x2, y1:y2] = beam_height

    dx_min, dx_max = -0.2, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    for i in range(3):  # Set up initial platforms
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

    for i in range(3, 6):  # Horizontal and inclined balance beams
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        incline = (i % 2 == 0)  # Alternate between horizontal and inclined beams
        add_beam(cur_x, cur_x + platform_length + dx, mid_y + dy, incline)
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

    final_platform_length = platform_length + m_to_idx(0.6)  # Slightly larger last platform
    add_platform(cur_x, cur_x + final_platform_length, mid_y)

    goals[-2] = [cur_x + final_platform_length / 2, mid_y]  # Goal before the final gap
    goals[-1] = [cur_x + final_platform_length + m_to_idx(0.5), mid_y]
    height_field[cur_x + final_platform_length:, :] = 0

    return height_field, goals