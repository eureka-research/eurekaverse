import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Combination of narrow walkways, descending steps, and angled ramps to test balance, climbing, and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up dimensions for features
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    walkway_length = m_to_idx(0.8 - 0.3 * difficulty)
    walkway_width = m_to_idx(0.35 if difficulty > 0.4 else 0.5)
    ramp_length = m_to_idx(1.0 - 0.3 * difficulty)
    gap_length = m_to_idx(0.2 + 0.5 * difficulty)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        height = np.random.uniform(0.15 * difficulty, 0.4 * difficulty)
        half_width = m_to_idx(0.5) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_walkway(start_x, end_x, mid_y):
        height = np.random.uniform(0.1 * difficulty, 0.3 * difficulty)
        half_width = walkway_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_ramp(start_x, end_x, mid_y, direction):
        height = np.random.uniform(0.2 * difficulty, 0.45 * difficulty)
        half_width = m_to_idx(0.5) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slope = np.linspace(0, height, num=x2 - x1)[::direction]
        height_field[x1:x2, y1:y2] = slope[:, None]

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Set up the starting platform
    cur_x = spawn_length
    dx = np.random.randint(dx_min, dx_max)
    dy = np.random.randint(dy_min, dy_max)
    add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
    goals[1] = [cur_x + (platform_length + dx) // 2, mid_y + dy]
    cur_x += platform_length + dx + gap_length

    # Add a narrow walkway
    dx = np.random.randint(dx_min, dx_max)
    add_walkway(cur_x, cur_x + walkway_length + dx, mid_y)
    goals[2] = [cur_x + (walkway_length + dx) // 2, mid_y]
    cur_x += walkway_length + dx + gap_length

    # Add an alternating height ramp sequence
    for i in range(3, 6):
        dx = np.random.randint(dx_min, dx_max)
        ramp_dir = 1 if i % 2 == 0 else -1
        add_ramp(cur_x, cur_x + ramp_length + dx, mid_y, ramp_dir)
        goals[i] = [cur_x + (ramp_length + dx) // 2, mid_y]
        cur_x += ramp_length + dx + gap_length

    # Add final goal at the end
    goals[6] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals