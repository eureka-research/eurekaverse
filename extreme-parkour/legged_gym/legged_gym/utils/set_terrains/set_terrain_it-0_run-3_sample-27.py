import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Series of alternating ramps to test the robot's climbing and descending abilities."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    ramp_length = m_to_idx(2.0 - 1.5 * difficulty)  # Ramp length decreases with difficulty
    ramp_height = m_to_idx(0.5 + 0.5 * difficulty)  # Ramp height increases with difficulty
    flat_length = m_to_idx(0.5)  # Flat sections between ramps
    mid_y = m_to_idx(width) // 2

    def add_ramp(start_x, ramp_up=True):
        x1 = start_x
        x2 = x1 + ramp_length
        if ramp_up:
            for i in range(ramp_length):
                height_field[x1 + i, :] = (i / ramp_length) * ramp_height
        else:
            for i in range(ramp_length):
                height_field[x1 + i, :] = ramp_height - (i / ramp_length) * ramp_height

    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at spawn

    cur_x = spawn_length
    ramp_up = True  # Alternates ramps going up and down
    for i in range(7):  # Create 7 ramps
        add_ramp(cur_x, ramp_up)
        # Place goal at the end of the ramp
        goals[i + 1] = [cur_x + ramp_length - m_to_idx(0.1), mid_y]

        # Add a flat section after each ramp
        flat_start = cur_x + ramp_length
        flat_end = flat_start + flat_length
        height_field[flat_start:flat_end, :] = ramp_height if ramp_up else 0
        
        cur_x = flat_end
        ramp_up = not ramp_up

    return height_field, goals