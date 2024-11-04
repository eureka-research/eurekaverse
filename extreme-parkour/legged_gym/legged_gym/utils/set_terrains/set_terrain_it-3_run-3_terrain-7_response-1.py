import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Mixed course with platforms, narrow beams, and tilted beams for agility and stability."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Course parameters
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width_specs = [np.random.uniform(1.0, 1.1), np.random.uniform(0.4, 0.7)]
    platform_width_specs = [m_to_idx(pw) for pw in platform_width_specs]
    platform_height_min, platform_height_max = 0.1 * difficulty, 0.4 * difficulty
    gap_length = 0.2 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)
    ramp_length = m_to_idx(1.5 - 0.5 * difficulty)

    mid_y = m_to_idx(width / 2)

    def add_platform(start_x, end_x, mid_y, width_spec):
        half_width = width_spec // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_beam(start_x, end_x, mid_y, width_spec):
        half_width = width_spec // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = np.random.uniform(0.1 * difficulty, 0.4 * difficulty)

    def add_tilted_beam(start_x, end_x, mid_y, direction, width_spec):
        half_width = width_spec // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(0.2, 0.6) * difficulty
        slant = np.linspace(0, ramp_height, num=end_x - start_x)[::direction]  # Create gradient
        height_field[x1:x2, y1:y2] = slant[:, None]

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.0, 0.5
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(7):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        if i % 3 == 0:
            obstacle = add_platform
            width_spec = platform_width_specs[0]
        elif i % 3 == 1:
            obstacle = add_beam
            width_spec = platform_width_specs[1]
        else:
            obstacle = add_tilted_beam
            width_spec = platform_width_specs[1]
            direction = 1 if i % 2 == 0 else -1

        if obstacle == add_tilted_beam:
            obstacle(cur_x, cur_x + ramp_length + dx, mid_y + dy, direction, width_spec)
            goals[i+1] = [cur_x + ramp_length // 2 + dx // 2, mid_y + dy]
            cur_x += ramp_length + dx + gap_length
        else:
            obstacle(cur_x, cur_x + platform_length + dx, mid_y + dy, width_spec)
            goals[i+1] = [cur_x + platform_length // 2, mid_y + dy]
            cur_x += platform_length + dx + gap_length

    # Set the final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals