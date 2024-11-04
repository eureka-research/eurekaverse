import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Stepping stones across a river with varying heights and distances."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Stepping stone parameters
    stone_diameter_min = 0.4  # meters
    stone_diameter_max = 0.8  # meters
    stone_height_min = 0.1  # meters
    stone_height_max = 0.4  # meters

    # Distance between stones varies with difficulty
    min_stone_distance = 0.5  # meters
    max_stone_distance = 1.5 + 3.5 * difficulty  # meters

    mid_y = m_to_idx(width) // 2

    def add_stone(center_x, center_y):
        x_rad = m_to_idx(random.uniform(stone_diameter_min, stone_diameter_max) / 2)
        y_rad = x_rad  # Making stones circular
        stone_height = random.uniform(stone_height_min, stone_height_max) * difficulty
        
        x1 = center_x - x_rad
        x2 = center_x + x_rad
        y1 = center_y - y_rad
        y2 = center_y + y_rad
        
        x1, x2 = max(x1, 0), min(x2, height_field.shape[0])
        y1, y2 = max(y1, 0), min(y2, height_field.shape[1])
        
        height_field[x1:x2, y1:y2] = stone_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # First goal, near the spawn area
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]
    
    # Keep track of the current position where new stones are added
    cur_x = spawn_length
    for i in range(7):  # Place 7 stepping stones
        stone_distance = random.uniform(min_stone_distance, max_stone_distance)
        center_x = cur_x + m_to_idx(stone_distance)
        center_y = mid_y + random.randint(m_to_idx(-0.5), m_to_idx(0.5))  # Allow small y deviations

        add_stone(center_x, center_y)

        # Place a goal at the middle of each stone
        goals[i + 1] = [center_x, center_y]

        cur_x = center_x  # Update the current x for the next stone
    
    # Ensure last part of terrain is flat, setting final goal
    final_running_length = m_to_idx(2)
    height_field[cur_x + m_to_idx(0.5):cur_x + final_running_length, :] = 0
    goals[-1] = [cur_x + m_to_idx(1), mid_y]

    return height_field, goals