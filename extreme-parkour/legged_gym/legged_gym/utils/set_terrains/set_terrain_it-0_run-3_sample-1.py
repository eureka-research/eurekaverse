import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Stepping stones across a variable-width gap for the robot to maneuver through."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    def add_stepping_stone(x, y, size, height):
        """Adds a stepping stone at the specified location with the specified size and height."""
        half_size = size // 2
        x1, x2 = x - half_size, x + half_size
        y1, y2 = y - half_size, y + half_size
        height_field[x1:x2, y1:y2] = height

    def random_variation(base, variation):
        """Returns base value plus a random variation."""
        return base + random.uniform(-variation, variation)

    # Convert constants to indices
    spawn_length = m_to_idx(2)
    stepping_stone_size_min = m_to_idx(0.5)
    stepping_stone_size_max = m_to_idx(1.0)
    stepping_stone_height_min = 0.05 + 0.1 * difficulty
    stepping_stone_height_max = 0.2 + 0.3 * difficulty
    gap_width_min = m_to_idx(1.0)
    gap_width_max = m_to_idx(2.0)

    # Set spawn area to flat ground and place the first goal
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), m_to_idx(width) // 2]

    cur_x = spawn_length
    for i in range(7):  # Set up 7 stepping stones
        # Define the stone size and height
        stone_size = random.randint(stepping_stone_size_min, stepping_stone_size_max)
        stone_height = random.uniform(stepping_stone_height_min, stepping_stone_height_max)

        # Define the variable gap width
        gap_width = random.randint(gap_width_min, gap_width_max) + np.random.randint(-m_to_idx(difficulty), m_to_idx(difficulty))

        # Define offset from mid_y to add variation
        mid_y = m_to_idx(width) // 2
        y_offset = np.random.randint(-m_to_idx(difficulty), m_to_idx(difficulty))

        # Place the stepping stone
        cur_x += gap_width
        add_stepping_stone(cur_x, mid_y + y_offset, stone_size, stone_height)

        # Place the goal on the stepping stone
        goals[i + 1] = [cur_x, mid_y + y_offset]

        # Move to next placement position
        cur_x += stone_size

    return height_field, goals