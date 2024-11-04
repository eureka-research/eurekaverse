import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Series of raised platforms and variable-width pathways to test the quadruped's climbing, balancing and jumping skills."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions
    # We make the platform height near 0.2 at minimum difficulty, rising at higher difficulty levels
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_height_min = 0.2
    platform_height_max = 0.7 * difficulty
    
    # Set the width of the pathways and gaps between the platforms
    platform_width_min = np.random.uniform(0.8, 1.0)
    platform_width_max = np.random.uniform(1.2, 1.4)
    platform_width_min, platform_width_max = m_to_idx([platform_width_min, platform_width_max])
    gap_length = np.random.uniform(0.2, 0.8)
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, y_start, y_end, height):
        height_field[start_x:end_x, y_start:y_end] = height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx([dx_min, dx_max])
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx([dy_min, dy_max])

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(7):  # Set up 7 platforms
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        width = np.random.randint(platform_width_min, platform_width_max)
        height = np.random.uniform(platform_height_min, platform_height_max)
        
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy - width//2, mid_y + dy + width//2, height)
        goals[i+1] = [cur_x + (platform_length + dx) // 2, mid_y + dy]
        
        cur_x += platform_length + dx + gap_length

    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals