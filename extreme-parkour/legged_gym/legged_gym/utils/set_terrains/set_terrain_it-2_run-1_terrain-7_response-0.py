import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Mixed terrain including uneven steps, narrow planks, and tilted surfaces for the quadruped to navigate through."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Constants
    platform_length = 1.0 - 0.3 * difficulty  # Adjusted for difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 0.3 + 0.05 * difficulty
    platform_width = m_to_idx(platform_width)
    pit_depth = -1.0
    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_plank(start_x, end_x, mid_y, height, tilt):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slant = np.linspace(0, tilt, num=x2-x1)[:, None]  # tilt effect
        height_field[x1:x2, y1:y2] = height + slant

    def add_gap(cur_x):
        # Set gap area to pit depth
        height_field[cur_x:cur_x + gap_length, :] = pit_depth
        return cur_x + gap_length

    dx_min, dx_max = -0.1, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)
    tilt_range = 0.0, 0.05 + 0.1 * difficulty

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Set remaining area to be a pit and platforms
    cur_x = spawn_length
    for i in range(6):  # Set up 6 mixed platforms and bridges
        dx = np.random.randint(dx_min, dx_max)
        height_min, height_max = 0.1 * difficulty, 0.5 * difficulty
        platform_height = np.random.uniform(height_min, height_max)
        dy = np.random.randint(dy_min, dy_max)
        if i % 2 == 0:
            # Plank with slope
            tilt = np.random.uniform(*tilt_range)
            add_plank(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height, tilt)
        else:
            # Regular platform
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height)

        # Put goal in the center of the platform/plank
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Add gap
        gap_length = m_to_idx(0.1 + 0.5 * difficulty)
        cur_x = add_gap(cur_x + platform_length + dx)
    
    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals