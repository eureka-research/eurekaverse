import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Stepping stone challenge, with varying heights requiring precise foot placement."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up stepping stone dimensions
    stone_length = 0.6 + 0.2 * difficulty
    stone_length = m_to_idx(stone_length)
    stone_width = 0.6 + 0.2 * difficulty
    stone_width = m_to_idx(stone_width)
    stone_height_min = 0.05
    stone_height_max = 0.3 + 0.4 * difficulty
    gap_length = 0.2 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    mid_y = m_to_idx(width) // 2

    def add_stepping_stone(start_x, mid_y):
        half_width = stone_width // 2
        x1 = start_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        stone_height = np.random.uniform(stone_height_min, stone_height_max)
        height_field[x1:x1 + stone_length, y1:y2] = stone_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    for i in range(6):  # Set up 6 stepping stones
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_stepping_stone(cur_x + dx, mid_y + dy)

        # Put goal in the center of the current stone
        goals[i+1] = [cur_x + dx + (stone_length / 2), mid_y + dy]

        # Add gap
        cur_x += stone_length + dx + gap_length
    
    # Add final goal at the end of the course
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals