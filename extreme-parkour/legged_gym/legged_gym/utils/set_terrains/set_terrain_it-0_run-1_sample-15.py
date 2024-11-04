import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Series of ascending and descending slopes, simulating hills and valleys, for the robot to traverse."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define terrain characteristics
    slope_length_base = 2.0  # Base length of a slope in meters
    slope_height_base = 0.3  # Base height change of a slope in meters

    variation_factor = difficulty * 0.5  # Variation factor to add challenge based on difficulty

    mid_y = m_to_idx(width) // 2

    def add_slope(start_x, end_x, base_height, slope_height):
        """Adds a linearly ascending or descending slope."""
        x1, x2 = m_to_idx(start_x), m_to_idx(end_x)
        height_change = np.linspace(base_height, base_height + slope_height, x2 - x1)
        height_field[x1:x2, :] = height_change[:, np.newaxis]

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length / field_resolution  # Start after spawn area
    base_height = 0.0

    for i in range(6):  # Set up 6 slopes
        slope_length = slope_length_base + random.uniform(-variation_factor, variation_factor)
        slope_height = slope_height_base + random.uniform(-variation_factor, variation_factor)
        
        # Adjust height variations for up and down slopes
        if i % 2 == 0:
            add_slope(cur_x, cur_x + slope_length, base_height, slope_height)
            base_height += slope_height
        else:
            add_slope(cur_x, cur_x + slope_length, base_height, -slope_height)
            base_height -= slope_height

        # Put goal in the middle of the slope
        goals[i + 1] = [cur_x + m_to_idx(slope_length / 2), mid_y]

        # Move to next slope start
        cur_x += slope_length

    # Add final goal at the end of the course
    end_x = cur_x + slope_length_base
    goals[-1] = [m_to_idx(end_x - 0.5), mid_y]

    # Ensure final section is flat
    height_field[m_to_idx(cur_x):, :] = base_height

    return height_field, goals