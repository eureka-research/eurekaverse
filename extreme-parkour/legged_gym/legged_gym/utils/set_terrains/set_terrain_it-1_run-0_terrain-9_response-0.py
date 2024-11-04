import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Staggered stepping stones of varying heights and gaps to test agility and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up stepping stone dimensions and properties
    stone_length_min = 0.4
    stone_length_max = 1.2
    stone_width_min = 0.4
    stone_width_max = 1.0
    stone_height_min = 0.1 + 0.2 * difficulty
    stone_height_max = 0.3 + 0.4 * difficulty
    gap_min = 0.2
    gap_max = 0.6

    # Convert dimensions to indices
    stone_length_min_idx = m_to_idx(stone_length_min)
    stone_length_max_idx = m_to_idx(stone_length_max)
    stone_width_min_idx = m_to_idx(stone_width_min)
    stone_width_max_idx = m_to_idx(stone_width_max)
    gap_min_idx = m_to_idx(gap_min)
    gap_max_idx = m_to_idx(gap_max)

    mid_y = m_to_idx(width) // 2

    def add_stepping_stone(start_x, stone_length, stone_width, mid_y, stone_height):
        half_width = stone_width // 2
        end_x = start_x + stone_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[start_x:end_x, y1:y2] = stone_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    for i in range(6):  # Set up 6 stepping stones
        stone_length = random.randint(stone_length_min_idx, stone_length_max_idx)
        stone_width = random.randint(stone_width_min_idx, stone_width_max_idx)
        stone_height = random.uniform(stone_height_min, stone_height_max)
        
        add_stepping_stone(cur_x, stone_length, stone_width, mid_y, stone_height)
        
        # Put the goal at the center of each stone
        goals[i + 1] = [cur_x + stone_length // 2, mid_y]

        # Adding a gap between stones
        gap_length = random.randint(gap_min_idx, gap_max_idx)
        cur_x += stone_length + gap_length

    # Add the final goal at the end of the course
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals