import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Dynamic platforms, narrow pathways, and staggered ramps to test the robot's balance, agility, and adaptiveness."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform and ramp configurations
    platform_length = 1.0 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = m_to_idx(0.6)
    platform_height_min, platform_height_max = 0.1, 0.4 * difficulty
    narrow_path_width = m_to_idx(0.4)  # Narrow pathways
    gap_length_min, gap_length_max = 0.2, 0.5 * difficulty
    gap_length_min, gap_length_max = m_to_idx(gap_length_min), m_to_idx(gap_length_max)
    ramp_length = m_to_idx(1.0)

    mid_y = m_to_idx(width / 2)

    def add_platform(x_start, x_end, y_mid):
        half_width = platform_width // 2
        y1, y2 = y_mid - half_width, y_mid + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x_start:x_end, y1:y2] = platform_height

    def add_ramp(start_x, end_x, y_mid, sloped_up=True):
        half_width = platform_width // 2
        y1, y2 = y_mid - half_width, y_mid + half_width
        height_gradient = np.linspace(0, (platform_height_max if sloped_up else -platform_height_max), num=end_x-start_x)
        for x in range(start_x, end_x):
            height_field[x, y1:y2] = height_gradient[x - start_x]

    def add_narrow_path(start_x, end_x, y_mid):
        half_width = narrow_path_width // 2
        y1, y2 = y_mid - half_width, y_mid + half_width
        height_field[start_x:end_x, y1:y2] = 0  # Narrow path is at ground level

    spawn_length = m_to_idx(2)
    height_field[:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    obstacles = ['platform', 'ramp', 'narrow_path']
    for i in range(6):
        obstacle = random.choice(obstacles)
        if obstacle == 'platform':
            add_platform(cur_x, cur_x + platform_length, mid_y)
            goals[i + 1] = [cur_x + platform_length / 2, mid_y]
            cur_x += platform_length
        elif obstacle == 'ramp':
            sloped_up = random.choice([True, False])
            add_ramp(cur_x, cur_x + ramp_length, mid_y, sloped_up)
            goals[i + 1] = [cur_x + ramp_length / 2, mid_y]
            cur_x += ramp_length
        elif obstacle == 'narrow_path':
            add_narrow_path(cur_x, cur_x + ramp_length, mid_y)
            goals[i + 1] = [cur_x + ramp_length / 2, mid_y]
            cur_x += ramp_length

        # Add a varying gap between obstacles
        cur_x += random.randint(gap_length_min, gap_length_max)

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0  # Set remaining area to flat ground

    return height_field, goals