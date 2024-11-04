import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Stepping stones across a wide river that the quadruped must navigate across by carefully placing its legs."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up stepping stone dimensions
    stone_radius_min = 0.2
    stone_radius_max = 0.4
    stone_radius = round(np.random.uniform(stone_radius_min, stone_radius_max), 2)
    stone_radius_idx = m_to_idx(stone_radius)
    gap_min = 0.4
    gap_max = 1.0 + 1.0 * difficulty
    gap_length = round(np.random.uniform(gap_min, gap_max), 2)
    gap_length_idx = m_to_idx(gap_length)
    
    river_width = 2.1  # Slightly wider than the robot's width, so always challenging.
    river_width_idx = m_to_idx(river_width)
    river_y_min = (m_to_idx(width) - river_width_idx) // 2
    river_y_max = river_y_min + river_width_idx

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), m_to_idx(width) // 2]

    # Riverbank at the spawn end
    height_field[:spawn_length, river_y_min:river_y_max] = -0.3

    # Define the river
    height_field[spawn_length:, river_y_min:river_y_max] = -0.3

    cur_x = spawn_length
    num_stones = 6
    
    def add_stepping_stone(center_x, center_y):
        radius = stone_radius_idx
        for i in range(-radius, radius + 1):
            for j in range(-radius, radius + 1):
                if i**2 + j**2 <= radius**2:
                    height_field[center_x + i, center_y + j] = np.random.uniform(0.1 * difficulty, 0.5 * difficulty)

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    for i in range(num_stones):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_stepping_stone(cur_x + stone_radius_idx + dx, river_y_min + river_width_idx // 2 + dy * (i % 2 == 0))
        
        goals[i + 1] = [cur_x + stone_radius_idx + dx, river_y_min + river_width_idx // 2 + dy * (i % 2 == 0)]
        cur_x += gap_length_idx

    # Riverbank at the end of the course
    height_field[cur_x:, river_y_min:river_y_max] = -0.3

    # Add final goal behind the last stepping stone
    goals[-1] = [cur_x + m_to_idx(0.5), river_y_min + river_width_idx // 2]

    return height_field, goals