import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Stepping stones and varied height platforms for jumping and balancing."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Parameters for stepping stones and platforms
    stone_size_min = 0.4  # meters
    stone_size_max = 0.7  # meters
    platform_length = 1.0 - 0.3 * difficulty  # meters
    platform_width = np.random.uniform(0.5, 1.0)  # meters
    platform_height_min = 0.1  # meters
    platform_height_max = 0.5 * difficulty  # meters
    gap_length = 0.1 + 0.4 * difficulty  # meters

    mid_y = m_to_idx(width) // 2

    def add_stepping_stone(x, y, size, height):
        """Adds a stepping stone at specified coordinates."""
        size_idx = m_to_idx(size)
        x1, x2 = x - size_idx // 2, x + size_idx // 2
        y1, y2 = y - size_idx // 2, y + size_idx // 2
        height_field[x1:x2, y1:y2] = height
    
    def add_platform(start_x, end_x, mid_y, height):
        half_width = m_to_idx(platform_width) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = m_to_idx([0.1, 0.2])
    dy_min, dy_max = m_to_idx([-0.5, 0.5])
    
    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length

    # Add set of stepping stones
    for i in range(4):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        size = random.uniform(stone_size_min, stone_size_max)
        height = random.uniform(platform_height_min, platform_height_max)
        add_stepping_stone(cur_x, mid_y + dy, size, height)
        
        # Set goal on stepping stone
        goals[i+1] = [cur_x, mid_y + dy]
        cur_x += m_to_idx(size) + gap_length
    
    # Add set of platforms
    platform_length_idx = m_to_idx(platform_length)
    for i in range(4, 7):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        height = random.uniform(platform_height_min, platform_height_max)
        add_platform(cur_x, cur_x + platform_length_idx, mid_y + dy, height)
        
        # Set goal on platform
        goals[i+1] = [cur_x + platform_length_idx / 2, mid_y + dy]
        cur_x += platform_length_idx + gap_length
    
    # Add final goal behind the last platform
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals