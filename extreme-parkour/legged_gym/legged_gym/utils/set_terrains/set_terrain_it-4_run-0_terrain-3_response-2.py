import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Mixed platforms and ramps of varying heights, widths, and gap lengths for the quadruped to jump, climb or navigate through."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform and ramp dimensions
    platform_length_min = 0.8 - 0.3 * difficulty
    platform_length_max = 1.2 - 0.3 * difficulty
    platform_width_range = (1.0, 1.5)
    platform_height_min, platform_height_max = 0.0 + 0.3 * difficulty, 0.4 + 0.3 * difficulty
    ramp_height_min, ramp_height_max = 0.1 + 0.3 * difficulty, 0.35 + 0.3 * difficulty
    gap_length_min = 0.1 + 0.3 * difficulty
    gap_length_max = 0.4 + 0.6 * difficulty

    platform_length_min = m_to_idx(platform_length_min)
    platform_length_max = m_to_idx(platform_length_max)
    platform_width_range = m_to_idx(platform_width_range)
    gap_length_min = m_to_idx(gap_length_min)
    gap_length_max = m_to_idx(gap_length_max)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = np.random.randint(*platform_width_range) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_ramp(start_x, end_x, mid_y, direction):
        half_width = np.random.randint(*platform_width_range) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        slant = np.linspace(0, ramp_height, num=y2-y1)[::direction]
        slant = slant[None, :]  # Add a dimension for broadcasting to x
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.2, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.0, 0.3  # Keep dy variations to maintain platform/ramp configurations
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set the spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    for i in range(7):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        gap_length = np.random.randint(gap_length_min, gap_length_max)
        
        if i % 2 == 0:
            # Add platform
            platform_length = np.random.randint(platform_length_min, platform_length_max)
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i+1] = [cur_x + (platform_length + dx) // 2, mid_y + dy]
            cur_x += platform_length + dx + gap_length
        else:
            # Add ramp
            ramp_length = np.random.randint(platform_length_min, platform_length_max)
            direction = (-1) ** i  # Alternate left and right ramps
            add_ramp(cur_x, cur_x + ramp_length + dx, mid_y + dy, direction)
            goals[i+1] = [cur_x + (ramp_length + dx) // 2, mid_y + dy]
            cur_x += ramp_length + dx + gap_length

    # Add the final goal behind the last obstacle, filling in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals