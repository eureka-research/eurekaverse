import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Stepping stones across a flooded path requiring precise navigation."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Convert terrain dimensions to indices
    terrain_length = m_to_idx(length)
    terrain_width = m_to_idx(width)

    mid_y = terrain_width // 2

    # Define stepping stone features
    stone_size_min, stone_size_max = 0.4 - 0.2 * difficulty, 0.8 - 0.1 * difficulty
    stone_size_min = m_to_idx(stone_size_min)
    stone_size_max = m_to_idx(stone_size_max)
    stone_height_min, stone_height_max = 0.1, 0.4 * difficulty

    # Define the flooded path
    water_level_min, water_level_max = -0.5, -0.2
    water_level = np.random.uniform(water_level_min, water_level_max)
    height_field[:, :] = water_level

    def add_stepping_stone(x, y):
        size = np.random.randint(stone_size_min, stone_size_max)
        height = np.random.uniform(stone_height_min, stone_height_max)
        x1, x2 = x - size // 2, x + size // 2
        y1, y2 = y - size // 2, y + size // 2
        height_field[x1:x2, y1:y2] = height

    # Coordinates for stones and goals
    step_x_interval = terrain_length // 8
    step_y_variance = np.array([-0.3, 0.3]) * difficulty  # Variance in y direction based on difficulty
    step_y_interval = m_to_idx(np.random.uniform(step_y_variance[0], step_y_variance[1]))

    # Ensure spawn area is clear
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(1, 8):  # Set up 7 stepping stones
        step_x = cur_x + step_x_interval
        step_y = mid_y + step_y_interval * (i % 2 * 2 - 1)  # toggle up and down

        add_stepping_stone(step_x, step_y)
        
        # Set the goal at the center of each stone
        goals[i] = [step_x, step_y]
        
        cur_x = step_x

    return height_field, goals