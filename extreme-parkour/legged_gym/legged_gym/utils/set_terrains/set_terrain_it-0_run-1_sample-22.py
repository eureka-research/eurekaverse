import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Staggered stepping stones and narrow beams to test precise foot placement and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    mid_y = m_to_idx(width / 2)
    
    # First goal at the end of the spawn area
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Define obstacle properties based on difficulty
    stone_height_min, stone_height_max = 0.05, 0.2 + 0.3 * difficulty
    stone_size_min, stone_size_max = 0.25 - 0.1 * difficulty, 0.5 + 0.1 * difficulty  # stone size in meters
    beam_length = 1.0 + 0.5 * difficulty
    beam_width = 0.4 + 0.2 * difficulty
    beam_height = 0.05 + 0.2 * difficulty

    current_x = spawn_length
    goal_index = 1

    def add_stepping_stone(x, y):
        stone_size_x = random.uniform(stone_size_min, stone_size_max)
        stone_size_y = random.uniform(stone_size_min, stone_size_max)
        height = random.uniform(stone_height_min, stone_height_max)
        x_start, x_end = m_to_idx(x - stone_size_x/2), m_to_idx(x + stone_size_x/2)
        y_start, y_end = m_to_idx(y - stone_size_y/2), m_to_idx(y + stone_size_y/2)
        
        height_field[x_start:x_end, y_start:y_end] = height

    def add_narrow_beam(x, y):
        x_start, x_end = m_to_idx(x - beam_length/2), m_to_idx(x + beam_length/2)
        y_start, y_end = m_to_idx(y - beam_width/2), m_to_idx(y + beam_width/2)
        height = beam_height
        
        height_field[x_start:x_end, y_start:y_end] = height

    # Distribute stepping stones randomly across the course
    num_stones = 8
    
    for i in range(num_stones):
        if goal_index >= 8:
            break
        y_offset = random.uniform(-1.0, 1.0)
        add_stepping_stone(current_x, mid_y + m_to_idx(y_offset))
        goals[goal_index] = [current_x, mid_y + y_offset]
        current_x += m_to_idx(0.7)
        goal_index += 1

    # Add a beam to challenge balance
    if goal_index < 8:
        add_narrow_beam(current_x + m_to_idx(1), mid_y)
        goals[goal_index] = [current_x + m_to_idx(1), mid_y]
        current_x += m_to_idx(2)
        goal_index += 1

    # Set the final goal to ensure the robot has to pass all obstacles
    if goal_index < 8:
        goals[goal_index] = [m_to_idx(length) - m_to_idx(0.5), mid_y]
        goal_index += 1

    return height_field, goals