import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Series of interconnected platforms and tilted planes to test the quadruped's balance and navigation abilities."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and plane dimensions
    platform_length = 1.5 - 0.5 * difficulty
    platform_length = m_to_idx(platform_length)
    small_platform_length = 0.6 - 0.2 * difficulty
    small_platform_length = m_to_idx(small_platform_length)
    obstacle_width = np.random.uniform(1.0, 1.2)
    obstacle_width = m_to_idx(obstacle_width)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.3 + 0.4 * difficulty
    ramp_height_min, ramp_height_max = 0.1 + 0.3 * difficulty, 0.2 + 0.5 * difficulty
    gap_length = 0.3 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, center_y):
        half_width = obstacle_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = center_y - half_width, center_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_ramp(start_x, end_x, center_y, slope_direction):
        half_width = obstacle_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = center_y - half_width, center_y + half_width
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        slant = np.linspace(0, ramp_height, num=y2-y1)[::slope_direction]
        slant = slant[None, :]  # Add a dimension for broadcasting to x
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.2, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.1, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Set remaining area to be a pit
    height_field[spawn_length:, :] = -1.0

    # Add first large platform
    cur_x = spawn_length
    dx = np.random.randint(dx_min, dx_max)
    dy = np.random.randint(dy_min, dy_max)
    add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
    goals[1] = [cur_x + (platform_length + dx) / 2, mid_y]
    cur_x += platform_length + dx + gap_length

    # Add interconnected ramps and small platforms
    for i in range(2, 6):
        if i % 2 == 0:  # Add small platform
            add_platform(cur_x, cur_x + small_platform_length, mid_y)
            cur_x += small_platform_length
        else:  # Add ramp
            slope_direction = (-1) ** (i // 2)  # Alternate direction
            add_ramp(cur_x, cur_x + platform_length // 2, mid_y, slope_direction)
            cur_x += platform_length // 2
            add_ramp(cur_x, cur_x + platform_length // 2, mid_y, -slope_direction)
            cur_x += platform_length // 2
        
        goals[i] = [cur_x - platform_length // 4, mid_y]
        cur_x += gap_length
    
    # Add last ramp and fill in remaining area
    slope_direction = 1 if (len(goals) - 1) % 2 else -1  # Alternate direction
    add_ramp(cur_x, cur_x + platform_length, mid_y, slope_direction)
    goals[-1] = [cur_x + platform_length / 2, mid_y]
    height_field[cur_x + platform_length:, :] = 0

    return height_field, goals