import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Zigzag Stepping Stones and Alternating Platforms for agility and precision."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    
    def add_stepping_stone(start_x, y, length, width, height):
        """Adds a stepping stone to the height_field."""
        half_w = width // 2
        height_field[start_x:start_x+length, y-half_w:y+half_w] = height

    def add_platform(start_x, end_x, y, height):
        """Adds a platform to the height_field."""
        half_width = width // 3
        x1, x2 = start_x, end_x
        y1, y2 = y - half_width, y + half_width
        height_field[x1:x2, y1:y2] = height

    # Convert distances
    step_length = m_to_idx(0.5)
    step_width = m_to_idx(0.4 + 0.2 * difficulty)
    platform_length = m_to_idx(1.0 - 0.3 * difficulty)
    gap_length = m_to_idx(0.3 + 0.2 * difficulty)

    step_height_min, step_height_max = 0.05, 0.15 + 0.1 * difficulty
    platform_height_min, platform_height_max = 0.1, 0.25 + 0.15 * difficulty

    # Set flat ground for spawn area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    mid_y = m_to_idx(width) // 2
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length

    # Add zigzag stepping stones
    for i in range(3):
        height = np.random.uniform(step_height_min, step_height_max)
        if i % 2 == 0:
            add_stepping_stone(cur_x, mid_y - m_to_idx(1), step_length, step_width, height)
            goals[i + 1] = [cur_x + step_length / 2, mid_y - m_to_idx(1)]
        else:
            add_stepping_stone(cur_x, mid_y + m_to_idx(1), step_length, step_width, height)
            goals[i + 1] = [cur_x + step_length / 2, mid_y + m_to_idx(1)]

        cur_x += step_length + gap_length

    # Add alternating platforms
    for i in range(3, 7):
        plat_height = np.random.uniform(platform_height_min, platform_height_max)
        add_platform(cur_x, cur_x + platform_length, mid_y, plat_height)
        
        # Add gaps between platforms
        add_platform(cur_x + platform_length + m_to_idx(0.2), cur_x + platform_length + gap_length, mid_y, -1.0)
        goals[i + 1] = [cur_x + platform_length / 2, mid_y]
        
        cur_x += platform_length + gap_length
    
    # Final Goal
    goals[7] = [cur_x + m_to_idx(1), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals