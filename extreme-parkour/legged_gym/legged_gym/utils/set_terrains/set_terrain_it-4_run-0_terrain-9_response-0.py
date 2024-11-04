import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Multiple types of obstacles, including steps, jumps, and narrow beams for the quadruped to navigate through."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]
    
    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    
    # Define obstacle dimensions
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.6, 1.2)  # Narrower width for beam-like obstacles
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.05 + 0.15 * difficulty, 0.15 + 0.35 * difficulty
    gap_length = 0.1 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)
    
    mid_y = m_to_idx(width) // 2
    
    def add_platform(start_x, end_x, mid_y, height):
        """Adds a platform (rectangle) of a given height at the specified x, y coordinates."""
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height
    
    def add_beam(start_x, end_x, mid_y, height):
        """Adds a narrow beam with a given height at specified x, y coordinates."""
        beam_width = m_to_idx(0.2)
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height
    
    # Initialize terrain with flat ground and set spawn area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]
    
    cur_x = spawn_length
    
    for i in range(6):
        dx = m_to_idx(0.1 * (-1 if i % 2 == 0 else 1))
        dy = m_to_idx(0.2 * (-1 if i % 2 == 1 else 1))
        obstacle_type = np.random.choice(['platform', 'beam'], p=[0.7, 0.3])
        obstacle_height = np.random.uniform(platform_height_min, platform_height_max)
        
        if obstacle_type == 'platform':
            add_platform(cur_x, cur_x + platform_length, mid_y + dy, obstacle_height)
        else:
            add_beam(cur_x, cur_x + platform_length, mid_y + dy, obstacle_height)
        
        goals[i+1] = [cur_x + platform_length / 2, mid_y + dy]
        
        cur_x += platform_length + gap_length
    
    # Set remaining to flat ground after the last gap
    height_field[cur_x:, :] = 0
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    
    return height_field, goals