import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Series of ascending and descending ramps for the robot to navigate over."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    ramp_length = 1.0  # Length of each ramp in meters
    ramp_length_idx = m_to_idx(ramp_length)
    
    ramp_width = 1.0  # Width of each ramp in meters
    ramp_width_idx = m_to_idx(ramp_width)

    angle_min = 5 + 20 * difficulty  # Minimum angle of ramp based on difficulty, in degrees
    angle_max = 10 + 30 * difficulty # Maximum angle of ramp based on difficulty, in degrees

    x_start_idx = m_to_idx(2)
    mid_y_idx = m_to_idx(width) // 2

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    def add_ramp(start_x, end_x, mid_y, ascending=True):
        half_width = ramp_width_idx // 2
        angle = np.random.uniform(angle_min, angle_max)
        ramp_height = np.tan(np.radians(angle)) * (end_x - start_x)
        if not ascending:
            ramp_height = -ramp_height
        for x in range(start_x, end_x):
            height_field[x, mid_y - half_width: mid_y + half_width] = (x - start_x) * np.tan(np.radians(angle)) if ascending else (end_x - x) * np.tan(np.radians(angle))

    # Set spawn area to flat ground
    height_field[0:x_start_idx, :] = 0
    goals[0] = [x_start_idx - m_to_idx(0.5), mid_y_idx]  # First goal positioned in the flat spawn area

    cur_x = x_start_idx
    for i in range(6):  # Create 6 ramps alternating between ascending and descending
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        ascending = i % 2 == 0
        add_ramp(cur_x, cur_x + ramp_length_idx + dx, mid_y_idx + dy, ascending)

        # Position goal in the middle of each ramp
        goals[i+1] = [cur_x + (ramp_length_idx + dx) / 2, mid_y_idx + dy]

        # Move to end of the ramp
        cur_x += ramp_length_idx + dx

    # Final goal positioned behind the last ramp, fill remaining flat area
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y_idx]
    height_field[cur_x:, :] = 0

    return height_field, goals