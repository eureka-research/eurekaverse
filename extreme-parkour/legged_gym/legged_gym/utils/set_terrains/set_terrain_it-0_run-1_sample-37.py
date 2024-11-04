import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Stepping stones varying in height for the robot to navigate across."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    
    # Define stepping stone characteristics
    stone_size = 0.5 - 0.2 * difficulty  # Stone size decreases with difficulty
    stone_size = m_to_idx(stone_size)
    stone_height_min, stone_height_max = 0.1 + 0.3 * difficulty, 0.3 + 0.5 * difficulty  # Height range of the stones
    
    def add_stone(center_x, center_y):
        half_size = stone_size // 2
        x1, x2 = center_x - half_size, center_x + half_size
        y1, y2 = center_y - half_size, center_y + half_size
        stone_height = np.random.uniform(stone_height_min, stone_height_max)
        height_field[x1:x2, y1:y2] = stone_height

    mid_y = m_to_idx(width) // 2

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # Initial goal
    
    locations = [(3, 2), (5, 3.5), (7, 2.5), (9, 3.7), (11, 1.5), (13.5, 3), (12, 2), (14, 2.5)]  # Predefined locations
    
    for i, (x, y) in enumerate(locations):
        center_x, center_y = m_to_idx(x), m_to_idx(y)
        add_stone(center_x, center_y)
        goals[i] = [center_x, center_y]

    # Set the area outside stones to be lower to prevent cheating
    height_field[spawn_length:, :] = -0.5

    return height_field, goals