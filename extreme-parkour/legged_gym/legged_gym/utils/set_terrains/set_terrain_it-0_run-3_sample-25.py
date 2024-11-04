import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Design a stair-step terrain for the quadruped to navigate by climbing up and down different heights."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    
    # Function to create stairs
    def add_stairs(start_x, start_y, stair_width, stair_depth, stair_height, num_steps):
        for i in range(num_steps):
            x1 = start_x + i * stair_depth
            x2 = x1 + stair_depth
            y1 = start_y
            y2 = start_y + stair_width
            height_field[x1:x2, y1:y2] = i * stair_height
    
    # Terrain specifications based on difficulty
    stair_width = np.random.uniform(1.2, 1.8)
    stair_depth = 0.4 + 0.6 * difficulty
    stair_height = 0.1 + 0.2 * difficulty
    num_steps = int(2 / stair_depth)  # Ensure that each stair set is around 2 meters in depth
    stair_width = m_to_idx(stair_width)
    stair_depth = m_to_idx(stair_depth)
    stair_height = m_to_idx(stair_height)
    
    mid_y = m_to_idx(width) // 2
    
    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put the first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y] 

    cur_x = spawn_length
    for i in range(4):  # Create 4 stair sections with 2 sets of up-and-down each (total 8 goals)
        # Up stairs
        add_stairs(cur_x, mid_y - stair_width // 2, stair_width, stair_depth, stair_height, num_steps)
        goals[2 * i + 1] = [cur_x + stair_depth * num_steps // 2, mid_y]
        
        # Move to the end of the first stairs
        cur_x += stair_depth * num_steps
        
        # Down stairs
        add_stairs(cur_x, mid_y - stair_width // 2, stair_width, stair_depth, -stair_height, num_steps)
        goals[2 * i + 2] = [cur_x + stair_depth * num_steps // 2, mid_y]
        
        # Move to the end of the second stairs
        cur_x += stair_depth * num_steps
    
    # Fill remaining terrain flat and add final goal
    height_field[cur_x:, :] = 0
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    return height_field, goals