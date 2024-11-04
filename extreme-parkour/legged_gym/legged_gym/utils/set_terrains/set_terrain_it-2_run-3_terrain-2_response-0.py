import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Series of stepping stones with alternating heights that the robot needs to navigate by jumping and balancing."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up stepping stone dimensions
    stone_length = 0.5  # meters
    stone_length = m_to_idx(stone_length)
    stone_width = 0.5  # meters
    stone_width = m_to_idx(stone_width)
    stone_height_min = 0.1 * difficulty  # Starting height
    stone_height_max = 0.5 * difficulty  # Max height
    gap_length_min = 0.3  # meters
    gap_length_max = 0.9 * difficulty  # Gap length increases with difficulty
    gap_length_min = m_to_idx(gap_length_min)
    gap_length_max = m_to_idx(gap_length_max)

    mid_y = m_to_idx(width) // 2

    def add_stepping_stone(x, y, height):
        x1 = x
        x2 = x + stone_length
        y1 = y - stone_width // 2
        y2 = y + stone_width // 2
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = m_to_idx(-0.2), m_to_idx(0.2)  # Slight random variation in x-coordinate of stones
    dy_min, dy_max = m_to_idx(-0.4), m_to_idx(0.4)  # Random variation in y-coordinate of stones

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    for i in range(7):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        stone_height = np.random.uniform(stone_height_min, stone_height_max)
        gap_length = np.random.randint(gap_length_min, gap_length_max)
        
        add_stepping_stone(cur_x, mid_y + dy, stone_height)
        
        # Put goal in the center of the stepping stone
        goals[i + 1] = [cur_x + stone_length / 2, mid_y + dy]
        
        # Move to next position
        cur_x += stone_length + gap_length
    
    return height_field, goals