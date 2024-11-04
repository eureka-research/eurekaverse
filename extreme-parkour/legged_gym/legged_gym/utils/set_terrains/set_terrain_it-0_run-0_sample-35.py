import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Irregularly spaced stepping stones of varying heights and widths for balance and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Parameters for stepping stones
    stone_min_width = 0.4
    stone_max_width = 1.2 - 0.6 * difficulty
    stone_min_height = 0.1
    stone_max_height = 0.3 + 0.3 * difficulty
    gap_min_length = 0.2
    gap_max_length = 0.6 + 0.4 * difficulty

    def add_stepping_stone(start_x, start_y, stone_width, stone_height):
        x1, x2 = int(start_x), int(start_x + stone_width)
        y1, y2 = int(start_y - stone_width / 2), int(start_y + stone_width / 2)
        height_field[x1:x2, y1:y2] = stone_height

    # Set spawn area to be flat ground
    spawn_area_length = m_to_idx(2)
    height_field[:spawn_area_length, :] = 0
    mid_y = m_to_idx(width) // 2

    # Initial goal at the spawn area
    goals[0] = [spawn_area_length - m_to_idx(0.5), mid_y]
    
    # Generate stepping stones
    current_x = spawn_area_length
    for i in range(7):
        stone_width = m_to_idx(random.uniform(stone_min_width, stone_max_width))
        stone_height = random.uniform(stone_min_height, stone_max_height)
        gap_length = m_to_idx(random.uniform(gap_min_length, gap_max_length))

        ypos_variation = m_to_idx(np.random.uniform(-0.8, 0.8) * difficulty)
        
        add_stepping_stone(current_x, mid_y + ypos_variation, stone_width, stone_height)
        
        # Center of each stone is the goal position
        goals[i + 1] = [current_x + stone_width / 2, mid_y + ypos_variation]

        # Move to the next position
        current_x += stone_width + gap_length

    return height_field, goals