import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Series of angled ramps and narrow bridges over a pit to challenge the quadruped's navigation skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Ramp characteristics
    ramp_height = 0.15 + 0.5 * difficulty  # height of the ramp increases with difficulty
    ramp_length = 2.0  # length of the ramp in meters
    ramp_length_idx = m_to_idx(ramp_length)
    
    # Bridge characteristics
    bridge_width_min = 0.4  # minimum width of the bridge at hardest difficulty
    bridge_width = 2.0 - difficulty * (2.0 - bridge_width_min)
    bridge_width_idx = m_to_idx(bridge_width)
    
    # Pit characteristics
    pit_depth = -0.5  # constant depth of the pit
    
    # Helper function to add a ramp
    def add_ramp(start_x, end_x, start_y, end_y, height_field):
        height_increase = ramp_height / (end_x - start_x)
        for i in range(start_x, end_x):
            height_field[i, start_y:end_y] = (i - start_x) * height_increase

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [m_to_idx(0.5), m_to_idx(width / 2)]  # First goal at the center of the spawn area

    cur_x = spawn_length
    ramp_direction = 1  # 1 for going up, -1 for going down
    mid_y = m_to_idx(width) // 2

    for i in range(6):
        # Alternate ramp direction
        ramp_direction *= -1
        start_y = mid_y - bridge_width_idx // 2
        end_y = mid_y + bridge_width_idx // 2
        
        add_ramp(cur_x, cur_x + ramp_length_idx, start_y, end_y, height_field)
        
        # Set a goal at the end of each ramp
        goals[i + 1] = [cur_x + ramp_length_idx - m_to_idx(0.5), mid_y]

        cur_x += ramp_length_idx
        
        # Add a pit
        height_field[cur_x:cur_x + m_to_idx(1),:] = pit_depth
        cur_x += m_to_idx(1)
        
    # Add final goal
    goals[-1] = [cur_x + m_to_idx(1), mid_y]
    
    # Fill the remaining terrain with flat ground
    height_field[cur_x:, :] = 0

    return height_field, goals