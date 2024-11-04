import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Incline and decline traversal with varying steepness for the quadruped robot."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Constants
    ramp_length_base = 1.0  # Base length of each ramp in meters
    ramp_height_base = 0.1  # Base height of incline/decline in meters
    max_ramp_height_variation = 0.3 * difficulty  # Ramp height based on difficulty
    flat_length = 0.6  # Length of flat sections between ramps in meters

    ramp_length = m_to_idx(ramp_length_base)
    flat_length_idx = m_to_idx(flat_length)
    mid_y = m_to_idx(width) // 2  # Middle of the field's width

    def add_ramp(start_x, height_change):
        """Add an incline or decline to the height field."""
        end_x = start_x + ramp_length
        incline = np.linspace(0, height_change, ramp_length)
        height_field[start_x:end_x, :] += incline[:, np.newaxis]

    # Place the quadruped's spawn area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # Place the first goal at the end of the spawn area
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Initialize current x position
    cur_x = spawn_length

    for i in range(6):
        # Calculate the height change for the ramp
        height_change = ramp_height_base + np.random.uniform(0, max_ramp_height_variation)

        # Add incline ramp
        add_ramp(cur_x, height_change)
        cur_x += ramp_length
        
        # Add flat section
        height_field[cur_x:cur_x + flat_length_idx, :] += height_change
        cur_x += flat_length_idx

        goals[i+1] = [cur_x - flat_length_idx // 2, mid_y]

        # Add decline ramp
        add_ramp(cur_x, -height_change)
        cur_x += ramp_length
        
    # Place the final flat area and goal
    height_field[cur_x:, :] = 0
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    return height_field, goals