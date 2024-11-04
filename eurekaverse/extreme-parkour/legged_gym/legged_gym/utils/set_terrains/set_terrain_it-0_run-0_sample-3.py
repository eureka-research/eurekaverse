import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """A series of tilted ramps and a narrow passageway to test climbing and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Parameters for the tilted ramps
    ramp_length = 1.0
    ramp_length = m_to_idx(ramp_length)
    ramp_width = np.random.uniform(1.0, 1.6)
    ramp_width = m_to_idx(ramp_width)
    max_ramp_height = 0.3 * difficulty
    max_ramp_slope = max_ramp_height / ramp_length

    # Parameters for the narrow passageway
    passage_length = 2.0
    passage_length = m_to_idx(passage_length)
    passage_width = np.random.uniform(0.4, 0.6)
    passage_width = m_to_idx(passage_width)
    
    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    
    # Place first goal at spawn
    goals[0] = [1, m_to_idx(width / 2)]
    
    current_x = spawn_length

    # Add tilted ramps
    for i in range(3):
        ramp_height = np.random.uniform(0.1, max_ramp_height)
        slope = ramp_height / ramp_length
        for x in range(current_x, current_x + ramp_length):
            height_field[x, m_to_idx(width / 2 - ramp_width / 2):m_to_idx(width / 2 + ramp_width / 2)] = (x - current_x) * slope
        
        goals[i + 1] = [current_x + ramp_length / 2, m_to_idx(width / 2)]
        current_x += ramp_length

        for x in range(current_x, current_x + ramp_length):
            height_field[x, m_to_idx(width / 2 - ramp_width / 2):m_to_idx(width / 2 + ramp_width / 2)] = ramp_height - (x - current_x) * slope
        
        current_x += ramp_length
        
    # Add narrow passageway
    passage_start_x = current_x
    passage_y_center = m_to_idx(width / 2)
    height_field[passage_start_x:passage_start_x + passage_length, 
                 passage_y_center - passage_width // 2:passage_y_center + passage_width // 2] = -0.1

    goals[4] = [passage_start_x + passage_length // 2, passage_y_center]
    
    current_x += passage_length
    
    # Add remaining tilted ramps
    for i in range(3):
        ramp_height = np.random.uniform(0.1, max_ramp_height)
        slope = ramp_height / ramp_length
        for x in range(current_x, current_x + ramp_length):
            height_field[x, m_to_idx(width / 2 - ramp_width / 2):m_to_idx(width / 2 + ramp_width / 2)] = (x - current_x) * slope

        goals[i + 5] = [current_x + ramp_length / 2, m_to_idx(width / 2)]
        current_x += ramp_length

        for x in range(current_x, current_x + ramp_length):
            height_field[x, m_to_idx(width / 2 - ramp_width / 2):m_to_idx(width / 2 + ramp_width / 2)] = ramp_height - (x - current_x) * slope

        current_x += ramp_length
    
    # Add final goal at the end of the terrain
    goals[-1] = [current_x - ramp_length // 2, m_to_idx(width / 2)]

    return height_field, goals