import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Combination of narrow beams, balanced ramps, and varied-height platforms for increased difficulty and feasibility."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up obstacle dimensions
    platform_length = m_to_idx(1.0 - 0.2 * difficulty)
    platform_width = m_to_idx(np.random.uniform(0.9, 1.3))
    platform_height_min, platform_height_max = 0.0 + 0.3 * difficulty, 0.05 + 0.35 * difficulty
    ramp_length = m_to_idx(1.5 - 0.3 * difficulty)
    ramp_width = m_to_idx(0.4 - 0.05 * difficulty)
    ramp_height_min, ramp_height_max = 0.0 + 0.4 * difficulty, 0.05 + 0.45 * difficulty
    beam_width = m_to_idx(0.35 - 0.05 * difficulty)
    gap_length = m_to_idx(0.5 + 0.4 * difficulty)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_ramp(start_x, end_x, mid_y, direction):
        half_width = ramp_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        slant = np.linspace(0, ramp_height, num=end_x - start_x)[::direction]  # Create gradient
        height_field[x1:x2, y1:y2] = slant[:, None]

    def add_beam(start_x, end_x, mid_y):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = np.random.uniform(0.2 * difficulty, 0.5 * difficulty)

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    obstacle_types = [add_platform, add_ramp, add_beam]
    for i in range(7):
        obstacle = obstacle_types[i % 3]
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        if obstacle == add_ramp:
            direction = 1 if i % 4 < 2 else -1  # Alternate ramp directions
            obstacle(cur_x, cur_x + ramp_length + dx, mid_y + dy, direction)
            goals[i + 1] = [cur_x + m_to_idx(0.75) + dx // 2, mid_y + dy]
            cur_x += ramp_length + dx + gap_length
        elif obstacle == add_beam:
            obstacle(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i + 1] = [cur_x + platform_length // 2, mid_y + dy]
            cur_x += platform_length + gap_length
        else:
            obstacle(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i + 1] = [cur_x + platform_length // 2, mid_y + dy]
            cur_x += platform_length + gap_length

    goals[-1] = [cur_x - m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals