import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Series of sloped ramps and narrow elevated paths testing balance and elevation traversal."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Terrain setup
    ramp_length = 2.0 - difficulty  # Adjust ramp length based on difficulty
    ramp_length_idx = m_to_idx(ramp_length)
    ramp_height = 0.3 + 0.5 * difficulty  # Adjust ramp height based on difficulty
    elevated_path_height = ramp_height + 0.2

    path_width_min = 0.4
    path_width_max = 1.0 - 0.2 * difficulty  # Narrows the path width with increased difficulty
    mid_y = m_to_idx(width / 2)

    def add_ramp(start_x, height, up=True):
        """Adds a ramp to the height field."""
        for x in range(start_x, start_x + ramp_length_idx):
            height_field[x, :] = height * ((x - start_x) / ramp_length_idx) if up else height * (1 - (x - start_x) / ramp_length_idx)

    def add_narrow_path(start_x, end_x):
        """Adds a narrow elevated path to the height field."""
        path_width = m_to_idx(np.random.uniform(path_width_min, path_width_max))
        y1 = mid_y - path_width // 2
        y2 = mid_y + path_width // 2
        height_field[start_x:end_x, y1:y2] = elevated_path_height

    dx_min, dx_max = 0.5, 1.0
    dx_min_idx, dx_max_idx = m_to_idx(dx_min), m_to_idx(dx_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    cur_x = spawn_length
    for i in range(4):  # Create 4 sets of ramps and narrow paths
        # Add a ramp ascending
        add_ramp(cur_x, ramp_height, up=True)
        cur_x += ramp_length_idx

        # Set goal at the end of the ramp
        goals[i * 2] = [cur_x - ramp_length_idx / 2, mid_y]

        # Add a narrow elevated path
        next_dx = np.random.randint(dx_min_idx, dx_max_idx)
        next_dx = max(next_dx, ramp_length_idx)  # Ensure enough space between paths
        add_narrow_path(cur_x, cur_x + next_dx)
        
        # Set goal halfway along the narrow path
        goals[i * 2 + 1] = [cur_x + next_dx / 2, mid_y]

        cur_x += next_dx

    # Add a final descending ramp
    add_ramp(cur_x, ramp_height, up=False)

    # Final goal at the end of the final ramp
    goals[7] = [cur_x + ramp_length_idx / 2, mid_y]

    return height_field, goals