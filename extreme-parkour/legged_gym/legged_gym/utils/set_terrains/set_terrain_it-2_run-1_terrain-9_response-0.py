import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Stepping stones over a water-filled pit for the robot to navigate, with increased height variation and narrower targets."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    stepping_stone_size_min = 0.5 - 0.2 * difficulty
    stepping_stone_size_max = 0.8 - 0.2 * difficulty
    stepping_stone_height_min = 0.1 * difficulty
    stepping_stone_height_max = 0.3 * difficulty
    gap_length_min = 0.2 + 0.1 * difficulty
    gap_length_max = 0.5 + 0.3 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_stepping_stone(start_x, mid_y, size, height):
        half_size = size // 2
        x1, x2 = start_x - half_size, start_x + half_size
        y1, y2 = mid_y - half_size, mid_y + half_size
        height_field[x1:x2, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Set remaining area to be a pit
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    for i in range(6):
        size = m_to_idx(np.random.uniform(stepping_stone_size_min, stepping_stone_size_max))
        height = np.random.uniform(stepping_stone_height_min, stepping_stone_height_max)
        gap = m_to_idx(np.random.uniform(gap_length_min, gap_length_max))
        add_stepping_stone(cur_x, mid_y, size, height)
        goals[i + 1] = [cur_x, mid_y]

        cur_x += size + gap

    # Final goal after the last stepping stone and fill the remaining space
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals