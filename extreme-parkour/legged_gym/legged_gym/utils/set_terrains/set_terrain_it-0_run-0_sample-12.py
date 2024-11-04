import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Multi-skill course featuring small ramps, jumps, and a final narrow bridge."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    mid_y = m_to_idx(width / 2)

    def add_ramp(start_x, end_x, mid_y, start_height, end_height):
        """Add a ramp to the height field."""
        for x in range(start_x, end_x):
            height_value = start_height + ((end_height - start_height) * (x - start_x) / (end_x - start_x))
            height_field[x, mid_y- m_to_idx(0.5): mid_y + m_to_idx(0.5)] = height_value

    def add_jump(start_x, mid_y, height, length, width):
        """Add a platform to jump onto."""
        x1, x2 = start_x, start_x + length
        y1, y2 = mid_y - width//2, mid_y + width//2
        height_field[x1:x2, y1:y2] = height

    def add_narrow_bridge(start_x, end_x, mid_y, width):
        """Add a narrow bridge towards the end of the course."""
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - width//2, mid_y + width//2
        height_field[x1:x2, y1:y2] = 0.5

    # Set up levels and parameters
    ramp_height = 0.2 + 0.3 * difficulty
    platform_height = 0.4 + 0.3 * difficulty
    gap_length = m_to_idx(0.4)
    narrow_bridge_width = m_to_idx(0.4)

    # Clear spawn area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    # Add series of ramps and platforms
    for i in range(3):
        ramp_length = m_to_idx(1.0 + 0.5 * difficulty)
        add_ramp(cur_x, cur_x + ramp_length, mid_y, 0, ramp_height)
        goals[i+1] = [cur_x + ramp_length//2, mid_y]
        
        cur_x += ramp_length + gap_length
        
        platform_length = m_to_idx(1.0)
        add_jump(cur_x, mid_y, platform_height, platform_length, m_to_idx(1.0))
        goals[i+2] = [cur_x + platform_length//2, mid_y]
        
        cur_x += platform_length + gap_length

    # Add a final narrow bridge
    bridge_length = m_to_idx(2.0)
    add_narrow_bridge(cur_x, cur_x + bridge_length, mid_y, narrow_bridge_width)
    goals[6] = [cur_x + bridge_length//2, mid_y]

    cur_x += bridge_length
    
    # Set final goal
    goals[7] = [cur_x + m_to_idx(0.5), mid_y]

    #Ensure remaining area is flat
    height_field[cur_x:, :] = 0

    return height_field, goals