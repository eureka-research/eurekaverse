import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Obstacle course featuring staggered stepping stones and varying elevation platforms to test agility and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    stepping_stone_length = 0.6 - 0.2 * difficulty
    stepping_stone_length = m_to_idx(stepping_stone_length)
    stepping_stone_width = np.random.uniform(0.4, 0.6)
    stepping_stone_width = m_to_idx(stepping_stone_width)
    stepping_stone_height_min, stepping_stone_height_max = 0.15 * difficulty, 0.35 * difficulty
    small_gap_length = 0.05 + 0.25 * difficulty
    small_gap_length = m_to_idx(small_gap_length)

    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.1)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.4 * difficulty, 0.1 + 0.5 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_stepping_stone(start_x, end_x, y_start, y_end, height):
        """Add a stepping stone to the height_field."""
        height_field[start_x:end_x, y_start:y_end] = height
        
    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.1, 0.1
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length

    for i in range(3):  # Set up 3 stepping stones
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        stone_height = np.random.uniform(stepping_stone_height_min, stepping_stone_height_max)
        
        # Ensure that stones remain within bounds
        y_center = mid_y + dy
        y_start = max(1, y_center - stepping_stone_width // 2, m_to_idx(1))
        y_end = min(m_to_idx(width) - 1, y_center + stepping_stone_width // 2, m_to_idx(width - 1))
        
        add_stepping_stone(cur_x, cur_x + stepping_stone_length + dx, y_start, y_end, stone_height)

        # Put goal in the center of the current stone
        goals[i+1] = [cur_x + (stepping_stone_length + dx) / 2, y_center]

        # Creating gaps
        cur_x += stepping_stone_length + dx + small_gap_length

    for i in range(4, 8):  # Adding 4 platforms
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)

        # Put goal in the center of the platform
        goals[i] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += platform_length + dx + small_gap_length
    
    # Add final goal near the end of the course
    goals[-1] = [cur_x + m_to_idx(1), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals