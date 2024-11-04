import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Mixed terrain with stairs and narrow bridges to test climbing, descending, and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    
    platform_width = m_to_idx(1.0)  # Consistent width for narrow bridges
    stair_height_increment = 0.05 + difficulty * 0.15  # Higher stairs for higher difficulty
    stair_depth = m_to_idx(0.3)  # Consistent stair depth
    stair_steps = int(1 / field_resolution)  # Number of steps in each stair set
    
    start_x = m_to_idx(2)
    cur_x = start_x
    mid_y = m_to_idx(width) // 2

    def add_stairs(start_x):
        """Adds a flight of stairs."""
        for step in range(stair_steps):
            height = stair_height_increment * step
            height_field[start_x + step * stair_depth:start_x + (step + 1) * stair_depth, mid_y - platform_width//2:mid_y + platform_width//2] = height
        return start_x + stair_steps * stair_depth
    
    def add_bridge(start_x, length, height):
        """Adds a narrow bridge."""
        height_field[start_x:start_x + length, mid_y - platform_width//2:mid_y + platform_width//2] = height
        return start_x + length
    
    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at the end of spawn area

    # First obstacle: a flight of stairs
    cur_x = add_stairs(cur_x)
    goals[1] = [cur_x - stair_depth // 2, mid_y]  # Goal right after the stairs

    # Second obstacle: a narrow bridge
    bridge_length = m_to_idx(2) + m_to_idx(1 * difficulty) 
    cur_x = add_bridge(cur_x + m_to_idx(0.2), bridge_length, stair_height_increment * stair_steps)  # Small gap before bridge

    goals[2] = [cur_x - bridge_length // 2, mid_y]  # Goal in the middle of the bridge

    # Third obstacle: a descending staircase
    cur_x += m_to_idx(0.2)  # Small gap before stairs
    cur_x = add_stairs(cur_x)
    goals[3] = [cur_x - stair_depth // 2, mid_y]  # Goal after descending stairs

    # Fourth obstacle: another bridge but longer
    bridge_length = m_to_idx(2.5) + m_to_idx(1 * difficulty) 
    cur_x = add_bridge(cur_x + m_to_idx(0.2), bridge_length, stair_height_increment * stair_steps)

    goals[4] = [cur_x - bridge_length // 2, mid_y]  # Goal in the middle of the bridge

    # Fifth obstacle: an ascending staircase 
    cur_x += m_to_idx(0.2)  # Small gap before stairs
    cur_x = add_stairs(cur_x)
    goals[5] = [cur_x - stair_depth // 2, mid_y]  # Goal after the ascending stairs

    # Sixth obstacle: a final bridge
    bridge_length = m_to_idx(3) + m_to_idx(1 * difficulty) 
    cur_x = add_bridge(cur_x + m_to_idx(0.2), bridge_length, stair_height_increment * stair_steps)

    goals[6] = [cur_x - bridge_length // 2, mid_y]  # Goal in the middle of the bridge

    # Final goal
    goals[7] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals