import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Stepping stones at varying heights to test precise movements and height adjustments."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        if isinstance(m, (list, tuple)):
            return [round(i / field_resolution) for i in m]
        else:
            return np.round(m / field_resolution).astype(np.int16)

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    stone_size = m_to_idx(0.4)
    stone_min_height = 0.05 
    stone_max_height = 0.3 + 0.7 * difficulty  # Height scales with difficulty

    mid_y = m_to_idx(width) // 2

    # Function to add a stepping stone
    def add_stone(center_x, center_y, height):
        half_size = stone_size // 2
        x1, x2 = center_x - half_size, center_x + half_size
        y1, y2 = center_y - half_size, center_y + half_size
        height_field[x1:x2, y1:y2] = height

    # Start the setup
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(7):  # Create 7 stepping stones
        cur_x += stone_size + m_to_idx(0.3)
        dy_offset = np.random.randint(-m_to_idx(0.25), m_to_idx(0.25))  # Small random y offset for randomness
        stone_center_y = mid_y + dy_offset
        stone_height = np.random.uniform(stone_min_height, stone_max_height)
        
        add_stone(cur_x, stone_center_y, stone_height)

        # Set goals on the stones' centers
        goals[i + 1] = [cur_x, stone_center_y]

    # Add final goal behind the last stone, fill in the remaining area
    cur_x += stone_size + m_to_idx(1)
    height_field[cur_x:, :] = 0
    goals[-1] = [cur_x - m_to_idx(0.5), mid_y]

    return height_field, goals