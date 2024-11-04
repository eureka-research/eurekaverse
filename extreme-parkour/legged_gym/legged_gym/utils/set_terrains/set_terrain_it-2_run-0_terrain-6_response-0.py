import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Multiple climbing and jumping platforms with alternating orientations for the robot to navigate."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]
    
    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    
    # Set up platform and ramp dimensions
    # For higher difficulty, we increase the height and width variations and gaps
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.3)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.3 * difficulty, 0.1 + 0.35 * difficulty
    gap_length = 0.2 + 0.6 * difficulty  # Wider gaps for higher difficulty
    gap_length = m_to_idx(gap_length)
    
    mid_y = m_to_idx(width) // 2
    
    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height
    
    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.0, 0.3  # Alternating direction
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)
    
    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  
    
    # Set the remaining area to be a pit
    height_field[spawn_length:, :] = -1.0
    
    cur_x = spawn_length
    
    for i in range(6):  # Set up 6 platforms
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        direction = (-1) ** i  # Alternate left and right
        
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy * direction)
        
        # Put goal in the center of the platform
        goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy * direction]
        
        # Add gap
        cur_x += platform_length + dx + gap_length
    
    # Add final goal behind the last platform, fill in the remaining gap
    goals[7] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0
    
    return height_field, goals