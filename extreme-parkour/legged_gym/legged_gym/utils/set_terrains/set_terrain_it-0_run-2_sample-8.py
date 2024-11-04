import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Slalom course with alternating poles to navigate around."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set the height of poles to be sufficiently tall relative to the quadruped's height
    pole_height = 0.5 + 0.5 * difficulty  
    pole_radius = m_to_idx(0.2)
    pole_distance_min = 1.0
    pole_distance_max = 1.2
    pole_distance_min, pole_distance_max = m_to_idx(pole_distance_min), m_to_idx(pole_distance_max)

    mid_y = m_to_idx(width) // 2
    start_x = m_to_idx(2)  # Spawn area ends at x=2 meters to avoid the robot spawning inside a pole

    # Set flat ground for spawn area
    height_field[0:start_x, :] = 0
    goals[0] = [start_x - m_to_idx(0.5), mid_y]  # First goal at spawn area

    cur_x = start_x
    
    # Place poles and goals
    for i in range(7):  # 7 poles to navigate around, with the 8th goal beyond the last pole
        pole_shift = (-1)**i * m_to_idx(0.5 + 0.5 * difficulty)  # Alternate poles to left and right
        
        # Prevent poles from being out of bounds
        if mid_y + pole_shift - pole_radius < 0 or mid_y + pole_shift + pole_radius >= m_to_idx(width):
            pole_shift = 0
        
        # Create the pole
        height_field[cur_x:cur_x+pole_radius*2, mid_y+pole_shift-pole_radius:mid_y+pole_shift+pole_radius] = pole_height
        
        # Each goal is just past each pole
        goals[i+1] = [cur_x + m_to_idx(0.1), mid_y + pole_shift]
        
        # Move to next pole location
        cur_x += random.randint(pole_distance_min, pole_distance_max)

    # Final goal after the last pole
    cur_x += m_to_idx(1)
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    # Ensure rest of the field beyond the last goal is flat
    height_field[cur_x:, :] = 0
    
    return height_field, goals