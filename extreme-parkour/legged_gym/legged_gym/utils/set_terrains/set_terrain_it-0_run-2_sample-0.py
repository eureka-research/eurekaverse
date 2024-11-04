import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Stepping stones across a stream for the robot to jump and balance on."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up stepping stone dimensions
    stone_diameter_min = 0.4  # minimum diameter of stepping stones
    stone_diameter_max = 0.8  # maximum diameter of stepping stones
    stone_height_min, stone_height_max = 0.1 + 0.1 * difficulty, 0.15 + 0.25 * difficulty
    gap_length_min = 0.3  # minimum gap between stepping stones
    gap_length_max = 0.7 + 0.3 * difficulty  # maximum gap increases with difficulty

    def add_stepping_stone(center_x, center_y):
        radius = np.random.uniform(stone_diameter_min / 2, stone_diameter_max / 2)
        radius_idx = m_to_idx(radius)
        stone_height = np.random.uniform(stone_height_min, stone_height_max)

        x, y = m_to_idx(center_x), m_to_idx(center_y)
        for i in range(-radius_idx, radius_idx + 1):
            for j in range(-radius_idx, radius_idx + 1):
                if i**2 + j**2 <= radius_idx**2:
                    height_field[x + i, y + j] = stone_height

    spawn_length = m_to_idx(2)
    mid_y = m_to_idx(width / 2)

    # Set spawn area to flat ground
    height_field[0:spawn_length, :] = 0
    # Put the first goal at spawn area
    goals[0] = [m_to_idx(1), mid_y]

    cur_x = 2.0
    for i in range(1, 8):  # Set up 7 stepping stones
        stone_center_y = width / 2 + np.random.uniform(-width / 4, width / 4)
        stone_center_x = cur_x + np.random.uniform(gap_length_min, gap_length_max)
        add_stepping_stone(stone_center_x, stone_center_y)

        # Place goal on the current stepping stone
        goals[i] = [m_to_idx(stone_center_x), m_to_idx(stone_center_y)]
        
        # Update current x position for the next stone
        cur_x = stone_center_x

    return height_field, goals