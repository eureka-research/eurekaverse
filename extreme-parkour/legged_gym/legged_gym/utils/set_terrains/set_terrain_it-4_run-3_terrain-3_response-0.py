import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Alternating narrow beams, ramps, and elevated platforms to test balance, climbing and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    
    beam_width = m_to_idx(0.4 - 0.2 * difficulty)
    platform_length = m_to_idx(1.0)
    gap_length = m_to_idx(0.5 + 0.3 * difficulty)
    ramp_length = m_to_idx(1.5 - 0.5 * difficulty)
    max_y_disp = m_to_idx(0.3)
    frame_height = m_to_idx(0.3)

    mid_y = m_to_idx(width / 2)

    def add_beam(start_x, end_x, mid_y):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = max_y_disp

    def add_ramp(start_x, end_x, mid_y, direction):
        half_width = m_to_idx(0.5)
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(0.2, 0.6) * difficulty
        slant = np.linspace(0, ramp_height, num=end_x - start_x)[::direction]  # Create gradient
        height_field[x1:x2, y1:y2] = slant[:, None]

    def add_platform(start_x, end_x, mid_y):
        half_width = m_to_idx(0.6)
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = frame_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(7):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        if i % 3 == 0:
            add_beam(cur_x, cur_x + platform_length + dx, mid_y + dy)
        elif i % 3 == 1:
            direction = 1 if i % 4 < 2 else -1  # Alternate ramp directions
            add_ramp(cur_x, cur_x + ramp_length + dx, mid_y + dy, direction)
        else:
            add_platform(cur_x, cur_x + platform_length, mid_y + dy)

        goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

    goals[-1] = [cur_x - m_to_idx(0.5), mid_y]

    height_field[cur_x:, :] = 0

    return height_field, goals