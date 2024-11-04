import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Series of hills and mounds for the robot to climb up and down, testing balance and stability."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set the overall length and width of the hill segments
    hill_length = 1.5 + 1.0 * difficulty  # Length of a hill, increases with difficulty
    hill_length = m_to_idx(hill_length)

    space_between_hills = 0.1 * difficulty
    space_between_hills = m_to_idx(space_between_hills)

    hill_height_min = 0.1 + 0.1 * difficulty  # Minimum height of the hills
    hill_height_max = 0.25 + 0.5 * difficulty  # Maximum height of the hills

    mid_y = m_to_idx(width) // 2

    def add_hill(start_x, end_x, mid_y, height, slope):
        half_width = m_to_idx(1.5)  # ensuring around 1.5 meters width for hills
        y1, y2 = mid_y - half_width // 2, mid_y + half_width // 2

        # Create slope: linear increase from ground to peak height
        for x in range(start_x, end_x):
            current_height = height * ((x - start_x) / (end_x - start_x)) ** slope
            height_field[x, y1:y2] = current_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    
    # Place first goal near the spawn point
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(6):  # Plan a sequence consisting of 6 hills
        hill_height = np.random.uniform(hill_height_min, hill_height_max)
        slope = np.random.uniform(1, 2)  # Randomized slope between 1 (linear) and 2 (quadratic)
        add_hill(cur_x, cur_x + hill_length, mid_y, hill_height, slope)
        
        # Place goal near the peak of each hill
        goals[i+1] = [cur_x + hill_length // 2, mid_y]

        cur_x += hill_length + space_between_hills  # Move to the position for the next hill

    # Add final goal behind the last hill, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals