import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Stepping platforms and ramps with variable gaps for the quadruped to navigate and adapt."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Enhanced ramp and platform dimensions
    platform_base_length = 1.2 - 0.4 * difficulty
    platform_length = m_to_idx(platform_base_length)
    platform_width = 1.4
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.3 * difficulty, 0.1 + 0.4 * difficulty
    gap_length = 0.3 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)

    ramp_length = m_to_idx(1.0 - 0.3 * difficulty)
    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_ramp(start_x, end_x, mid_y, height, direction):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slant = np.linspace(0, height, num=x2-x1)[::direction] + np.linspace(0, height, num=y2-y1)[None, ::direction] / 2
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.1, 0.15
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Set remaining area to pit
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    for i in range(7):
        is_ramp = (i % 3) == 0
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        center_y = mid_y + dy

        if is_ramp:
            direction = np.random.choice([-1, 1])
            ramp_height = np.random.uniform(platform_height_min, platform_height_max)
            add_ramp(cur_x, cur_x + ramp_length + dx, center_y, ramp_height, direction)
            goals[i + 1] = [cur_x + (ramp_length + dx) / 2, center_y]
            cur_x += ramp_length + dx + gap_length
        else:
            platform_height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, cur_x + platform_length + dx, center_y, platform_height)
            goals[i + 1] = [cur_x + (platform_length + dx) / 2, center_y]
            cur_x += platform_length + dx + gap_length

    # Add final goal behind the last platform or ramp
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals