import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Stepping stones course that tests the quadruped's precision jumping ability."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    # Initialize height field and goals array
    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    def add_stepping_stone(center_x, center_y, stone_size):
        """Add a stepping stone obstacle to the height field."""
        half_stone_size = stone_size // 2
        height_field[center_x - half_stone_size: center_x + half_stone_size, center_y - half_stone_size: center_y + half_stone_size] = np.random.uniform(0.1, 0.3)  # Random height variation

    # Constants for the stepping stones
    stone_size = m_to_idx(0.4)  # Stepping stone size in meters
    stone_spacing = m_to_idx(0.3 + 0.5 * difficulty)  # Spacing between stones scales with difficulty

    mid_y = m_to_idx(width / 2)
    initial_x = m_to_idx(2 / field_resolution)  # Initial x-offset to avoid spawn

    # Set spawn area to flat ground
    height_field[0:initial_x, :] = 0
    goals[0] = [initial_x - m_to_idx(0.5), mid_y]

    # Generate stepping stones and place goals
    cur_x = initial_x
    for i in range(1, 8):
        dy = random.choice([-m_to_idx(0.3), 0, m_to_idx(0.3)])
        add_stepping_stone(cur_x, mid_y + dy, stone_size)
        
        # Set goal at the center of each stepping stone
        goals[i] = [cur_x, mid_y + dy]
        
        cur_x += stone_size + stone_spacing

    return height_field, goals