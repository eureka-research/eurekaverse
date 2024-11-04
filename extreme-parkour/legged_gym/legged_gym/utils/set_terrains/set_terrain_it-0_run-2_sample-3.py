import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Series of inclined ramps and steps for the robot to traverse."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define ramp and step parameters based on difficulty
    ramp_length = 1.5 - 0.5 * difficulty  # Ramp length decreases with difficulty
    ramp_length = m_to_idx(ramp_length)
    ramp_height = 0.25 + 0.25 * difficulty  # Ramp height increases with difficulty
    step_height = 0.1 + 0.15 * difficulty  # Step height also depends on difficulty

    mid_y = m_to_idx(width) // 2

    def add_ramp(start_x, end_x, mid_y, height_increase):
        """Add a ramp with a specific height increase."""
        half_width = m_to_idx(1.2) // 2  # Fixed width of ramps
        for x in range(start_x, end_x):
            slope = height_increase / (end_x - start_x)
            height_field[x, mid_y - half_width:mid_y + half_width] = slope * (x - start_x)
    
    def add_step(x, mid_y, step_height):
        """Add a single step at a given x position."""
        half_width = m_to_idx(1.2) // 2  # Fixed width of steps
        height_field[x:x + m_to_idx(0.4), mid_y - half_width:mid_y + half_width] = step_height

    # Set spawn area to be flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Generate ramps and steps in alternating pattern
    cur_x = spawn_length
    for i in range(6):  # Create 6 ramps and steps
        add_ramp(cur_x, cur_x + ramp_length, mid_y, ramp_height)
        # Place goal in the middle of the ramp
        goals[i + 1] = [cur_x + ramp_length // 2, mid_y]
        cur_x += ramp_length

        # Add a flat area before the step
        height_field[cur_x:cur_x + m_to_idx(0.2), :] = ramp_height
        cur_x += m_to_idx(0.2)

        # Add step
        add_step(cur_x, mid_y, ramp_height + step_height)
        cur_x += m_to_idx(0.4)

        # Adjust ramp height for next ramp
        ramp_height += step_height

    # Add final goal at the end of the course
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = ramp_height

    return height_field, goals