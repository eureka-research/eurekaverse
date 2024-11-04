import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Stepping stones arranged in a staggered pattern to test lateral and forward movement."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Parameters for stepping stones
    stone_length = 0.4 
    stone_width = 0.4
    stone_height_min, stone_height_max = 0.1, 0.3  # Random height for stepping stones
    stone_length, stone_width = m_to_idx(stone_length), m_to_idx(stone_width)
    stone_gap = 0.8 - 0.4 * difficulty  # Gap size decreases with increased difficulty
    stone_gap = m_to_idx(stone_gap)

    mid_y = m_to_idx(width) // 2
    cur_x = m_to_idx(2)  # Start placing obstacles after the spawn area

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [m_to_idx(1), mid_y]  

    stone_positions = []

    for i in range(7):  # Set up 7 stepping stones
        stone_height = np.random.uniform(stone_height_min + difficulty, stone_height_max + difficulty)
        offset_y = m_to_idx(random.uniform(-0.6, 0.6))  # Lateral position variation
        x1, x2 = cur_x, cur_x + stone_length
        y1, y2 = mid_y + offset_y - stone_width // 2, mid_y + offset_y + stone_width // 2
        height_field[x1:x2, y1:y2] = stone_height

        # Store stone position for goals
        stone_positions.append([(x1 + x2) // 2, (y1 + y2) // 2])

        # Add gap for the next stone
        cur_x += stone_length + stone_gap

    # Assign goal positions centered on stepping stones
    for i in range(1, 8):
        goals[i] = stone_positions[i-1]

    return height_field, goals