import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Series of sloped platforms and stairs for the robot to climb and balance across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define dimensions for platforms and stairs
    platform_length = 1.0 - 0.4 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.2)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.3 * difficulty, 0.1 + 0.4 * difficulty
    step_height_min, step_height_max = 0.1, 0.3 * difficulty
    step_depth = 0.3  # Depth of each step
    step_depth = m_to_idx(step_depth)
    gap_length = 0.3 + 0.5 * difficulty  # Increase gap length for added difficulty
    gap_length = m_to_idx(gap_length)
    
    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_stairs(start_x, num_steps, step_height, mid_y):
        half_width = platform_width // 2
        for step in range(num_steps):
            x1 = start_x + step * step_depth
            x2 = x1 + step_depth
            y1, y2 = mid_y - half_width, mid_y + half_width
            height = step * step_height
            height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = -0.1, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # First goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(3):  # Create 3 platforms
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length
    
    for i in range(3, 6):  # Create 3 sets of stairs
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        num_steps = np.random.randint(3, 6)
        step_height = np.random.uniform(step_height_min, step_height_max)
        add_stairs(cur_x, num_steps, step_height, mid_y + dy)
        stair_length = num_steps * step_depth
        goals[i+1] = [cur_x + stair_length / 2, mid_y + dy]
        cur_x += stair_length + gap_length
    
    # Final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals