import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Varied obstacle course with jumps, narrow paths, and elevated platforms."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        if isinstance(m, (list, tuple)):
            return [round(i / field_resolution) for i in m]
        return np.round(m / field_resolution).astype(np.int16)
    
    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    mid_y = m_to_idx(width / 2)
    mid_x = length / 2
    
    # Ensure spawn area is flat
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    
    # Define helper functions for various obstacles
    def add_platform(start_x, start_y, length, width, height):
        height_field[start_x:start_x + length, start_y:start_y + width] = height

    def add_narrow_path(start_x, start_y, length, width, height):
        height_field[start_x:start_x + length, start_y:start_y + width] = height

    def add_gap(start_x, start_y, length, width):
        height_field[start_x:start_x + length, start_y:start_y + width] = -1.0
    
    # Set start goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    path_width = m_to_idx(1.0)
    
    # Define obstacle dimensions based on difficulty
    platform_height = 0.1 + 0.3 * difficulty
    platform_length = m_to_idx(1.0 + 0.5 * difficulty)
    small_gap_length = m_to_idx(0.3 + 0.4 * difficulty)
    narrow_path_width = m_to_idx(0.35)

    # Define the obstacles pattern
    obstacles = [
        ("platform", platform_length, path_width, platform_height),
        ("narrow_path", platform_length, path_width, platform_height / 2),
        ("gap", small_gap_length, path_width, 0),
        ("platform", platform_length, path_width, platform_height),
        ("gap", small_gap_length, path_width, 0),
        ("narrow_path", platform_length, narrow_path_width, platform_height / 2),
        ("platform", platform_length, path_width, platform_height),
        ("gap", small_gap_length, path_width, 0)
    ]

    for i, (type_, length, width, height) in enumerate(obstacles):
        length = int(length)
        width = int(width)
        if type_ == "platform":
            add_platform(cur_x, mid_y - width // 2, length, width, height)
            goals[i+1] = [cur_x + length // 2, mid_y]
        elif type_ == "narrow_path":
            add_narrow_path(cur_x, mid_y - width // 2, length, width, height)
            goals[i+1] = [cur_x + length // 2, mid_y]
        elif type_ == "gap":
            add_gap(cur_x, mid_y - width // 2, length, width)
            goals[i+1] = [cur_x + length + m_to_idx(0.5), mid_y]
        
        cur_x += length
    
    return height_field, goals