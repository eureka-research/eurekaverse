import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Undulating narrow paths for the quadruped to balance and traverse heightened platforms."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Obstacle Parameters
    path_length = np.random.uniform(0.8, 1.5)  # length of each obstacle in meters
    path_length = m_to_idx(path_length)
    path_width = 0.45  # width in meters for narrow paths
    path_width = m_to_idx(path_width)
    platform_height_base = 0.1  # base height for platforms
    platform_height_incr = 0.2 * difficulty  # height increment based on difficulty
    gap_length_base = 0.1  # base gap length in meters
    gap_length_incr = 0.2 * difficulty  # gap length increment based on difficulty
    total_length = m_to_idx(length)
    total_width = m_to_idx(width)

    mid_y = total_width // 2
    spawn_length = m_to_idx(2)
    
    def add_platform(start_x, end_x, y_center, height):
        """
        Adds a narrow platform to the height_field.
        """
        half_width = path_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = y_center - half_width, y_center + half_width
        height_field[x1:x2, y1:y2] = height
    
    # Set spawn area to flat ground
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]
    
    cur_x = spawn_length
    height = 0

    for i in range(7):
        height += platform_height_base + platform_height_incr  # Increment height based on difficulty
        add_platform(cur_x, cur_x + path_length, mid_y, height)
        
        # Set goal in the middle of the current platform
        goals[i + 1] = [cur_x + path_length // 2, mid_y]

        # Add gap between platforms
        gap_length = gap_length_base + gap_length_incr
        cur_x += path_length + m_to_idx(gap_length)

    # Set final goal at the end
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals