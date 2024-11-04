import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Raised platforms with varied heights and staggered pathways for the robot to navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform dimensions
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width_min, platform_width_max = 0.5, 1.2 - 0.3 * difficulty
    platform_heights = np.linspace(0.1, 0.35 * difficulty, 4)
    gap_length = 0.1 + 0.2 * difficulty
    gap_length = m_to_idx(gap_length)
    
    mid_y = m_to_idx(width) // 2
    
    def add_platform(start_x, end_x, mid_y, width, height):
        half_width = m_to_idx(width) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height
    
    # Initial Spawn Area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(6):
        platform_width = np.random.uniform(platform_width_min, platform_width_max)
        platform_height = np.random.choice(platform_heights)
        dx = np.random.uniform(-0.1, 0.1) * field_resolution
        dy = np.random.uniform(-0.4, 0.4) * field_resolution
        
        add_platform(cur_x, cur_x + platform_length, mid_y + m_to_idx(dy), platform_width, platform_height)
        goals[i+1] = [cur_x + platform_length // 2, mid_y + m_to_idx(dy)]
        
        cur_x += platform_length + gap_length
    
    # Final goal beyond last platform
    add_platform(cur_x, cur_x + platform_length, mid_y, platform_width, np.random.choice(platform_heights))
    goals[-1] = [cur_x + platform_length // 2, mid_y]
    
    return height_field, goals