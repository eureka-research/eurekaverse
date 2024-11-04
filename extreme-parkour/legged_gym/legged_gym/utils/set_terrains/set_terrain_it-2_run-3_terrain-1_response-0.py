import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Combination of narrow beams, platforms, and sloped ramps for advancing navigation skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Parameters for various obstacles
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.5)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.2 * difficulty, 0.10 + 0.25 * difficulty

    beam_length = 1.0
    beam_length = m_to_idx(beam_length)
    beam_width = 0.4
    beam_width = m_to_idx(beam_width)
    beam_height_min, beam_height_max = 0.20, 0.30 + 0.15 * difficulty

    ramp_height_min, ramp_height_max = 0.0 + 0.5 * difficulty, 0.10 + 0.55 * difficulty
    gap_length = 0.2 + 0.8 * difficulty  # Enough gap for jumps
    gap_length = m_to_idx(gap_length)

    def add_obstacle(start_x, end_x, mid_y, width, height, slope=False):
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        if slope:
            slant = np.linspace(0, height, num=x2-x1)[:, None]
            height_field[x1:x2, y1:y2] = slant
        else:
            height_field[x1:x2, y1:y2] = height

    mid_y = m_to_idx(width) // 2

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at spawn

    cur_x = spawn_length
    for i in range(6):  # Combination of 6 different obstacles
        if i % 3 == 0:  # Add platform
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)
            height = np.random.uniform(platform_height_min, platform_height_max)
            add_obstacle(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_width, height)
            goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
            cur_x += platform_length + dx + gap_length

        elif i % 3 == 1:  # Add narrow beam
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)
            height = np.random.uniform(beam_height_min, beam_height_max)
            add_obstacle(cur_x, cur_x + beam_length + dx, mid_y + dy, beam_width, height)
            goals[i + 1] = [cur_x + (beam_length + dx) / 2, mid_y + dy]
            cur_x += beam_length + dx + gap_length

        else:  # Add sloped ramp
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)
            height = np.random.uniform(ramp_height_min, ramp_height_max)
            add_obstacle(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_width, height, slope=True)
            goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
            cur_x += platform_length + dx + gap_length

    # Final goal behind the last obstacle
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals