import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Combination of staircases, ramps, and small gaps to test climbing and jumping skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform, staircase, and ramp dimensions
    platform_length = 1.0 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.2, 1.6)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.2 + 0.4 * difficulty
    
    ramp_length = 1.2 - 0.3 * difficulty
    ramp_length = m_to_idx(ramp_length)
    ramp_width = platform_width
    ramp_height = 0.2 + 0.4 * difficulty

    gap_length = 0.4 + 0.3 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_ramp(start_x, end_x, mid_y, direction):
        half_width = ramp_width // 2
        height = np.linspace(0, ramp_height, end_x - start_x)
        if direction == 'down':
            height = height[::-1]
        for i in range(mid_y - half_width, mid_y + half_width):
            height_field[start_x:end_x, i] = height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length

    # Create mixed obstacles
    for i in range(6):
        # Randomly decide the obstacle type
        obstacle_type = np.random.choice(['platform', 'ramp_up', 'ramp_down'])

        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        if obstacle_type == 'platform':
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
            cur_x += platform_length + dx + gap_length
        elif obstacle_type == 'ramp_up':
            add_ramp(cur_x, cur_x + ramp_length + dx, mid_y + dy, 'up')
            goals[i + 1] = [cur_x + (ramp_length + dx) / 2, mid_y + dy]
            cur_x += ramp_length + dx + gap_length
        elif obstacle_type == 'ramp_down':
            add_ramp(cur_x, cur_x + ramp_length + dx, mid_y + dy, 'down')
            goals[i + 1] = [cur_x + (ramp_length + dx) / 2, mid_y + dy]
            cur_x += ramp_length + dx + gap_length

    # Add final goal behind the last obstacle
    goals[7] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals