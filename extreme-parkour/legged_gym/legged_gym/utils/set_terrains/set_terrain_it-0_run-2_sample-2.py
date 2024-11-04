import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Narrow winding paths across 'lakes' for the robot to navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    path_width_min = 0.4  # Minimum width of the path
    path_width_max = 1.0  # Maximum width of the path
    lake_depth = -1.0      # Depth of the "lake"
    
    narrow_path_width = np.random.uniform(path_width_min, path_width_max)
    narrow_path_width = m_to_idx(narrow_path_width)

    def add_path(start_x, end_x, mid_y, width):
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = 0   # The path is flat and at height 0.

    def add_lake(start_x, end_x, mid_y, width):
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = lake_depth   # The lake is lower than the path height.

    dx_min, dx_max = 0.8, 2.0   # Length of each path segment
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -1.2, 1.2  # Lateral shift of the path
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    mid_y = m_to_idx(width) // 2

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    for i in range(7):  # 7 paths with lakes in between
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_path(cur_x, cur_x + dx, mid_y + dy, narrow_path_width)
        
        # Put goal in the center of the path
        goals[i+1] = [cur_x + dx / 2, mid_y + dy]
        
        # Add lake right after the path
        lake_width = np.random.uniform(0.5, 1.5)  # Random width for the lake
        lake_width = m_to_idx(lake_width)
        add_lake(cur_x + dx, cur_x + dx + lake_width, mid_y + dy, m_to_idx(width))

        # Move to next path start position
        cur_x += dx + lake_width
    
    # Ensure the final goal is reachable, avoid placing it over a lake
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    height_field[cur_x:, :] = 0   # Fill remaining area with flat ground

    return height_field, goals