import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Sloped terrain with variable inclines and declines to test quadruped's climbing and descending skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    slope_length = 1.0 - 0.5 * difficulty  # Length of each sloped section
    slope_length = m_to_idx(slope_length)
    max_elevation = 0.3 + 0.4 * difficulty  # Maximum height difference in meters

    def add_slope(start_x, start_y, end_x, slope_type="up"):
        """Adds a slope incline or decline to the height_field."""
        height = np.linspace(0, max_elevation, end_x - start_x) if slope_type == "up" else np.linspace(max_elevation, 0, end_x - start_x)
        height_field[start_x:end_x, start_y] = height[:, np.newaxis]
        for i in range(1, m_to_idx(1.0)):  # Make the slope at least 1 meter wide
            height_field[start_x:end_x, start_y + i] = height

    # Ensure quadruped starts on flat terrain
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), m_to_idx(width / 2)]  # First goal near the spawn area

    cur_x = spawn_length
    cur_y = m_to_idx(width / 2) - m_to_idx(0.5)  # Starting in the center with enough space for 1m wide slopes

    for i in range(7):  # Create a series of 7 slopes
        slope_type = "up" if np.random.random() > 0.5 else "down"
        add_slope(cur_x, cur_y, cur_x + slope_length, slope_type)

        # Put goal at the end of each slope
        goals[i+1] = [cur_x + slope_length / 2, cur_y + m_to_idx(0.5)]

        # Move to the end of the current slope
        cur_x += slope_length
        if i % 2 == 0:  # Alternate columns
            cur_y -= m_to_idx(1.5)
        else:
            cur_y += m_to_idx(1.5)

    # Ensure the last goal is reachable
    goals[-1] = [m_to_idx(length) - m_to_idx(1), cur_y] 

    return height_field, goals