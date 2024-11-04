import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Stepping stones in a zigzag pattern to test the robot's balance and maneuvering skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set stepping stone dimensions
    stone_size = m_to_idx(random.uniform(0.4, 0.6))
    stone_height_min, stone_height_max = 0.05, 0.15 + 0.15 * difficulty
    
    mid_y = m_to_idx(width) // 2
    
    cur_x, cur_y = m_to_idx(2), mid_y  # Start after the spawn region
    spawn_region_length = m_to_idx(2)
    
    # Ensure the spawn area is flat
    height_field[:spawn_region_length, :] = 0

    def add_stepping_stone(x, y):
        """Add a stepping stone at a particular (x, y) position."""
        stone_height = np.random.uniform(stone_height_min, stone_height_max)
        half_size = stone_size // 2
        height_field[x - half_size:x + half_size, y - half_size:y + half_size] = stone_height

    # Place the stones in a zigzag pattern
    zigzag_length = m_to_idx(1.2)
    lateral_shift = m_to_idx(0.7)

    # Place first goal at the spawn location
    goals[0] = [cur_x - m_to_idx(0.5), cur_y]

    for i in range(1, 8):
        add_stepping_stone(cur_x, cur_y)
        goals[i] = [cur_x, cur_y]
        
        direction = -1 if i % 2 == 0 else 1
        cur_y += direction * lateral_shift
        cur_x += zigzag_length

    return height_field, goals