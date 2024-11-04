import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Stepping stones and narrow path obstacle course for testing precise movements and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up stepping stone dimensions
    stone_size = 0.6 - 0.2 * difficulty
    stone_size_idx = m_to_idx(stone_size)
    stone_height_min, stone_height_max = 0.1 * difficulty, 0.3 * difficulty
    stone_gap_min, stone_gap_max = 0.5, 1.2 - 0.5 * difficulty
    stone_gap_min_idx, stone_gap_max_idx = m_to_idx(stone_gap_min), m_to_idx(stone_gap_max)

    # Mid y-coordinate
    mid_y = m_to_idx(width / 2)

    # Function to add a stone
    def add_stone(center_x, center_y):
        stone_height = np.random.uniform(stone_height_min, stone_height_max)
        half_size = stone_size_idx // 2
        x1, x2 = center_x - half_size, center_x + half_size
        y1, y2 = center_y - half_size, center_y + half_size
        height_field[x1:x2, y1:y2] = stone_height

    # Narrow path dimensions
    path_length = 2.0
    path_length_idx = m_to_idx(path_length)
    path_width = 0.4
    path_width_idx = m_to_idx(path_width)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [m_to_idx(1), mid_y]  

    cur_x = m_to_idx(2)
    for i in range(4):  # Set up stones and narrow paths in alternating fashion
        # Add stepping stone
        add_stone(cur_x + stone_size_idx // 2, mid_y)
        goals[i * 2 + 1] = [cur_x + stone_size_idx // 2, mid_y]

        # Move to start of narrow path
        cur_x += stone_size_idx + random.randint(stone_gap_min_idx, stone_gap_max_idx)

        # Add narrow path
        height_field[cur_x:cur_x + path_length_idx, mid_y - path_width_idx // 2:mid_y + path_width_idx // 2] = np.random.uniform(stone_height_min, stone_height_max)
        goals[i * 2 + 2] = [cur_x + path_length_idx // 2, mid_y]

        # Move to end of narrow path
        cur_x += path_length_idx + random.randint(stone_gap_min_idx, stone_gap_max_idx)

    # Final goal at the end
    goals[-1] = [m_to_idx(length - 1), mid_y]

    return height_field, goals