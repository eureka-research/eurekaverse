import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Tilted platforms and narrow beams for climbing and balancing."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length = 0.8 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 0.5
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1, 0.3 + 0.3 * difficulty
    beam_width = 0.1
    beam_width = m_to_idx(beam_width)
    gap_length = 0.2 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_tilted_platform(start_x, end_x, mid_y, tilt_angle):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slant = np.linspace(0, np.tan(tilt_angle) * (x2 - x1), num=y2 - y1)
        slant = slant[None, :]  # Add a dimension for broadcasting to x
        height_field[x1:x2, y1:y2] = slant

    def add_narrow_beam(start_x, end_x, mid_y):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(3):  # 3 Tilted Platforms
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        tilt_angle = np.radians(np.random.uniform(5, 15) * difficulty)
        add_tilted_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, tilt_angle)
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

    for i in range(3, 7):  # 4 Narrow Beams
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_narrow_beam(cur_x, cur_x + platform_length + dx, mid_y + dy)
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals