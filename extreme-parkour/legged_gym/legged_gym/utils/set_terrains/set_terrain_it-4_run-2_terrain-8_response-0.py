import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Varied platforms and steps for the robot to climb and navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.3)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 * difficulty, 0.4 * difficulty
    gap_length = 0.2 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)

    step_height_min, step_height_max = 0.1, 0.3

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_step(start_x, end_x, mid_y):
        step_width = m_to_idx(0.4)
        half_width = step_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        step_height = np.random.uniform(step_height_min, step_height_max)
        height_field[x1:x2, y1:y2] = step_height

    dx_min, dx_max = np.round(-0.1/ field_resolution).astype(np.int16), np.round(0.1 /field_resolution).astype(np.int16)
    dy_min, dy_max = np.round(-0.2/ field_resolution).astype(np.int16), np.round(0.2 /field_resolution).astype(np.int16)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # First part: alternating platforms and steps
    cur_x = spawn_length
    for i in range(3):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
        goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

        add_step(cur_x, cur_x + m_to_idx(0.3), mid_y + dy)
        goals[i + 4] = [cur_x + m_to_idx(0.15), mid_y + dy]
        cur_x += m_to_idx(0.3) + gap_length

    # Final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals