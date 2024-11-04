import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Raised platforms with varying heights and narrow passages to test robot's agility and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and passage dimensions
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.2 - 0.1 * difficulty)  # Slightly reduce width
    platform_width = m_to_idx(platform_width)
    
    gap_length_min = 0.2
    gap_length_max = 0.8
    gap_length_min = m_to_idx(gap_length_min)
    gap_length_max = m_to_idx(gap_length_max)
    
    platform_height_min = 0.2 * difficulty
    platform_height_max = 0.4 + 0.2 * difficulty
    
    mid_y = m_to_idx(width) // 2
    
    def add_platform(x_start, x_end, y_center, height):
        half_width = platform_width // 2
        y1, y2 = y_center - half_width, y_center + half_width
        height_field[x_start:x_end, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]
    
    cur_x = spawn_length
    for i in range(7):  # Set up 6 platforms
        height = np.random.uniform(platform_height_min, platform_height_max)
        gap_length = np.random.randint(gap_length_min, gap_length_max)
        
        add_platform(cur_x, cur_x + platform_length, mid_y, height)
        goals[i+1] = [cur_x + platform_length // 2, mid_y]
        
        cur_x += platform_length + gap_length
        
        if i % 2 == 0 and i != 6:
            # Add a narrow passageway after 2 platforms
            passage_width = m_to_idx(0.35 + 0.15 * (1 - difficulty))
            passage_start = m_to_idx(0.2 + 0.3 * difficulty)
            passage_height = np.random.uniform(0.1, 0.2) * (difficulty + 1)
            height_field[cur_x:cur_x + passage_start, (mid_y - passage_width // 2):(mid_y + passage_width // 2)] = passage_height
            
            goals[i+1][0] += passage_start // 2
            cur_x += passage_start
    
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0
    
    return height_field, goals