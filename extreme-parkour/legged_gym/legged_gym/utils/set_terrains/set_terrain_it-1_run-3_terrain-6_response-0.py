import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Multiple elevated platforms and sideways ramps for the robot to climb, descend and jump across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and ramp dimensions
    platform_length_min = 0.8
    platform_length_max = 1.5
    platform_height_min = 0.1 + 0.2 * difficulty
    platform_height_max = 0.3 + 0.4 * difficulty
    ramp_length = 1.0
    ramp_height = 0.15 + 0.35 * difficulty

    platform_length_min = m_to_idx(platform_length_min)
    platform_length_max = m_to_idx(platform_length_max)
    ramp_length = m_to_idx(ramp_length)
    
    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = m_to_idx(1.2) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_ramp(start_x, end_x, mid_y):
        half_width = m_to_idx(1.0) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_slope = np.linspace(0, ramp_height, num=x2-x1)
        height_field[x1:x2, y1:y2] = ramp_slope[:, None]

    dx_min, dx_max = m_to_idx([-0.1, 0.2])
    dy_min, dy_max = m_to_idx([-0.4, 0.4])
    gap_min, gap_max = m_to_idx([0.2, 0.7])
    
    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    for i in range(3):
        dx, dy = np.random.randint(dx_min, dx_max), np.random.randint(dy_min, dy_max)
        gap = np.random.randint(gap_min, gap_max)

        # Add an elevated platform
        platform_length = np.random.randint(platform_length_min, platform_length_max)
        add_platform(cur_x, cur_x + platform_length, mid_y + dy)
        goals[i + 1] = [(cur_x + platform_length) / 2, mid_y + dy]  # Center of the platform
        cur_x += platform_length + gap

        # Add a sideways ramp
        dx, dy = np.random.randint(dx_min, dx_max), np.random.randint(dy_min, dy_max)
        add_ramp(cur_x, cur_x + ramp_length, mid_y + dy)
        goals[i + 4] = [cur_x + (ramp_length // 2), mid_y + dy]  # Center of the ramp
        cur_x += ramp_length + gap

    # Add a final goal behind the last ramp, filling in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals