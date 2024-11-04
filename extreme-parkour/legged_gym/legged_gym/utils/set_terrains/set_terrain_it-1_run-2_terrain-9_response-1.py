import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Staggered stepping stones over a pit for the robot to navigate and jump across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up stepping stone dimensions
    stone_size = 0.5 + 0.5 * difficulty
    stone_size = m_to_idx(stone_size)
    stone_height_min, stone_height_max = 0.1 + 0.1 * difficulty, 0.3 + 0.3 * difficulty
    gap_length_min, gap_length_max = 0.4 + 0.2 * difficulty, 0.8 + 0.4 * difficulty
    gap_length_min, gap_length_max = m_to_idx(gap_length_min), m_to_idx(gap_length_max)

    mid_y = m_to_idx(width) // 2

    def add_stepping_stone(center_x, center_y):
        half_size = stone_size // 2
        x1, x2 = center_x - half_size, center_x + half_size
        y1, y2 = center_y - half_size, center_y + half_size
        stone_height = np.random.uniform(stone_height_min, stone_height_max)
        height_field[x1:x2, y1:y2] = stone_height

    # Spawn area flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Pit setup
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    cur_y = mid_y
    for i in range(7):  # Create 7 stepping stones
        gap_length = np.random.randint(gap_length_min, gap_length_max)
        direction = (-1) ** i  # Alternate sides for staggered placement
        dx = np.random.randint(gap_length_min, gap_length_max) * direction
        dy = np.random.randint(gap_length_min, gap_length_max) * direction

        cur_x += gap_length
        cur_y += dy
        cur_x = max(cur_x, spawn_length)  # Ensure within bounds

        add_stepping_stone(cur_x, cur_y)

        goals[i+1] = [cur_x, cur_y]

    goals[7] = [cur_x + m_to_idx(1), mid_y]  # Place final goal beyond the last stone
    height_field[cur_x:, :] = 0  # Ensure flat ground after last stone

    return height_field, goals