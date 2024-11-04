import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Series of uneven terrains with gradual slopes and steep cliffs for the robot to balance and navigate over."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    
    # Terrain configuration
    min_slope_height = 0.1 * difficulty  # Min height difference per slope
    max_slope_height = 0.6 * difficulty  # Max height difference per slope
    slope_length = 1.5  # Length of each slope in meters
    cliff_height = -0.2 * difficulty  # Height of cliffs (negative implies downward)
    flat_length = 0.5  # Length of flat terrain in-between slopes
    width_idx = m_to_idx(width)
    
    cur_x = m_to_idx(2)  # Start after the spawn area
    spawn_length = m_to_idx(2)
    
    # Set spawn area to flat ground
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), width_idx // 2]  # First goal at spawn

    for i in range(7):  # Create 7 sections of slope or cliff
        if i % 2 == 0:  # Even indices -> slope
            slope_height = random.uniform(min_slope_height, max_slope_height)
            slope_range = m_to_idx(slope_length)

            for j in range(slope_range):
                height_val = (j / slope_range) * slope_height
                height_field[cur_x + j, :] = height_val
            
            cur_x += slope_range
            goals[i+1] = [cur_x - m_to_idx(0.5), width_idx // 2]  # Goal at the end of the slope

        else:  # Odd indices -> cliff and flat terrain
            cliff_idx = m_to_idx(0.5)
            flat_range = m_to_idx(flat_length)
            
            # Create a cliff
            height_field[cur_x:cur_x + cliff_idx, :] += cliff_height
            
            cur_x += cliff_idx
            
            # Following flat terrain
            height_field[cur_x:cur_x + flat_range, :] = height_field[cur_x - 1, :]

            cur_x += flat_range
            goals[i+1] = [cur_x - m_to_idx(0.5), width_idx // 2]  # Goal at the end of the flat terrain
    
    # Ensure the last goal is on a flat terrain
    final_flat_length = m_to_idx(1)
    height_field[cur_x:cur_x + final_flat_length, :] = height_field[cur_x - 1, :]
    goals[-1] = [cur_x + m_to_idx(0.5), width_idx // 2]  # Final goal position
    
    return height_field, goals