import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Stepping stones scattered over a pit with varying heights for the robot to navigate and jump across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up dimensions for stepping stones
    stepping_stone_size = 0.3 + 0.4 * (1 - difficulty)  # Smaller stones for higher difficulty
    stepping_stone_size = m_to_idx(stepping_stone_size)
    stepping_stone_height_min, stepping_stone_height_max = 0.1 * difficulty, 0.4 * difficulty
    gap_length_min = 0.5 - 0.3 * (1 - difficulty)
    gap_length_max = 1.0 - 0.5 * (1 - difficulty)
    gap_length_min = m_to_idx(gap_length_min)
    gap_length_max = m_to_idx(gap_length_max)

    mid_y = m_to_idx(width) // 2

    def add_stepping_stone(x, y):
        half_size = stepping_stone_size // 2
        x1, x2 = x - half_size, x + half_size
        y1, y2 = y - half_size, y + half_size
        height = np.random.uniform(stepping_stone_height_min, stepping_stone_height_max)
        height_field[x1:x2, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Set terrain to be a pit initially
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    for i in range(1, 8):
        gap_length = np.random.randint(gap_length_min, gap_length_max)
        cur_x += gap_length

        # Randomly scatter stepping stones within a certain range
        dy = np.random.randint(-1, 2) * m_to_idx(0.5)
        
        # Place the stepping stone
        add_stepping_stone(cur_x, mid_y + dy)

        # Place the goal in the center of the stepping stone
        goals[i] = [cur_x, mid_y + dy]

    # Add a flat area behind the last stepping stone
    final_length = m_to_idx(2)
    height_field[cur_x+stepping_stone_size//2:cur_x+stepping_stone_size//2+final_length, :] = 0

    return height_field, goals