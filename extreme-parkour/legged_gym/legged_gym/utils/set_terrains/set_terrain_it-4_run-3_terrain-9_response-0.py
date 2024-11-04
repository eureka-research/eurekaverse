import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Stepping stones of varying sizes and heights across pits for the quadruped to navigate and jump."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Course parameters
    stone_width_range = (0.4, 0.7)  # In meters, size of stones
    stone_height_range = (0.05, 0.3) * difficulty  # Height increases with difficulty
    stone_gap_range = (0.2, 0.8) * difficulty  # Gap increases with difficulty

    start_pos_x = m_to_idx(2)
    mid_y = m_to_idx(width / 2)

    def add_stepping_stone(center_x, center_y, size, height):
        half_size = m_to_idx(size / 2)
        x1, x2 = center_x - half_size, center_x + half_size
        y1, y2 = center_y - half_size, center_y + half_size
        height_field[x1:x2, y1:y2] = height

    # Set quadruped spawn area
    height_field[:start_pos_x, :] = 0
    goals[0] = [start_pos_x - m_to_idx(0.5), mid_y]

    # Set remaining area to be pits
    height_field[start_pos_x:, :] = -1.0 * difficulty

    cur_x = start_pos_x
    for i in range(1, 8):  # Create 7 stepping stones
        stone_width = np.random.uniform(*stone_width_range)
        stone_height = np.random.uniform(*stone_height_range)
        stone_gap = np.random.uniform(*stone_gap_range)

        cur_x += m_to_idx(stone_gap)

        if i % 2 == 0:
            cur_y = mid_y + m_to_idx(np.random.uniform(0.4, 1.2) * difficulty)
        else:
            cur_y = mid_y - m_to_idx(np.random.uniform(0.4, 1.2) * difficulty)

        add_stepping_stone(cur_x, cur_y, stone_width, stone_height)

        # Place goal on each stone
        goals[i] = [cur_x, cur_y]

    # Clear area beyond last stepping stone for safe goal placement
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals