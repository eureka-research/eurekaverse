import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Alternating narrow beams and steep ramps for testing precision and balance."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]
    
    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    
    # Setup parameters
    beam_length_short = m_to_idx(0.4 + 0.2 * difficulty)
    beam_length_long = m_to_idx(1.0 + 0.5 * difficulty)
    beam_width = m_to_idx(0.2)  # Narrow beams

    ramp_length = m_to_idx(1.0)
    ramp_height_min, ramp_height_max = 0.05 + 0.2 * difficulty, 0.1 + 0.3 * difficulty
    
    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, center_y):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = center_y - half_width, center_y + half_width
        height_field[x1:x2, y1:y2] = 0.1 * difficulty  # Small elevation

    def add_ramp(start_x, end_x, center_y, ascend=True):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = center_y - half_width, center_y + half_width
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        slant = np.linspace(0, ramp_height, num=x2-x1) if ascend else np.linspace(ramp_height, 0, num=x2-x1)
        slant = slant[:, None]  # Add a dimension for broadcasting to y
        height_field[x1:x2, y1:y2] = slant
    
    # Initialize starting area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  
    
    # Setup alternating beams and ramps
    cur_x = spawn_length
    for i in range(4):  # Alternating narrow beams and ramps
        # Beam Section
        add_beam(cur_x, cur_x + beam_length_short, mid_y)
        cur_x += beam_length_short

        # Update goals
        goals[2*i+1] = [cur_x - beam_length_short // 2, mid_y]

        # Ramp Section
        add_ramp(cur_x, cur_x + ramp_length, mid_y, ascend=(i % 2 == 0))
        cur_x += ramp_length

        # Update goals
        goals[2*i+2] = [cur_x - ramp_length // 2, mid_y]

    # Setting the last section for goal completion
    goals[7] = [cur_x + m_to_idx(0.5), mid_y]

    return height_field, goals