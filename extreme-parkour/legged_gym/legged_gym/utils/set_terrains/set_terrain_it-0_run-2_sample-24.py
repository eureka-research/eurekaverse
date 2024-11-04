import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Stepping stones in a shallow water course, requiring the robot to navigate by stepping on a series of small platforms."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up stepping stone dimensions
    stone_diameter = 0.4 + 0.1 * difficulty  # Diameter of each stepping stone
    stone_diameter = m_to_idx(stone_diameter)
    stone_height = np.random.uniform(0.05, 0.2) + 0.15 * difficulty  # Height of the stones
    gap_distance = 0.4 + 0.6 * difficulty  # Distance between stepping stones
    gap_distance = m_to_idx(gap_distance)
    
    middle_y = m_to_idx(width) // 2

    def place_stone(x, y):
        radius = stone_diameter // 2
        height_field[x - radius:x + radius + 1, y - radius:y + radius + 1] = stone_height

    # Set the spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), middle_y]

    current_x = spawn_length
    for i in range(1, 7):
        dx = np.random.randint(-1, 2)  # Small variation in x position
        dy = np.random.randint(-3, 4)  # Small variation in y position
        x_pos = current_x + gap_distance + dx
        y_pos = middle_y + dy
        place_stone(x_pos, y_pos)

        # Place goal at each stepping stone
        goals[i] = [x_pos, y_pos]

        current_x += gap_distance + stone_diameter

    # Add final goal past the last stepping stone, ensuring it is on flat ground
    final_gap = m_to_idx(1)
    final_x = current_x + final_gap
    height_field[final_x:, :] = 0
    goals[-1] = [final_x - m_to_idx(0.5), middle_y]

    return height_field, goals