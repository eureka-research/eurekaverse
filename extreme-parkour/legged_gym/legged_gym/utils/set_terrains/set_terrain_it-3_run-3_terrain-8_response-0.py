import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Alternating platforms and narrow beams for climbing and jumping skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        if isinstance(m, (list, tuple)):
            return [round(i / field_resolution) for i in m]
        return np.round(m / field_resolution).astype(np.int16)

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width_min, platform_width_max = 0.4, 1.5  # Range of widths
    platform_height_min, platform_height_max = 0.1, 0.4  # Adjusted heights
    
    gap_length = 0.2 + 0.3 * difficulty  # Moderate gap length
    gap_length = m_to_idx(gap_length)
    
    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height, width):
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    for i in range(6):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        platform_width = np.random.uniform(platform_width_min, platform_width_max)
        platform_width = m_to_idx(platform_width)

        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height, platform_width)
        goals[i+1] = [cur_x + (platform_length + dx) // 2, mid_y + dy]

        # Add gap
        cur_x += platform_length + dx + gap_length
    
    # Final descent ramp
    final_platform_length = m_to_idx(2)
    add_platform(cur_x, cur_x + final_platform_length, mid_y, 0, final_platform_length // 2)
    goals[-1] = [cur_x + final_platform_length // 2, mid_y]

    height_field[cur_x:, :] = 0

    return height_field, goals