import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Multiple narrow paths with subtle ramps for balance and precision traversal."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define narrow path and ramp dimensions
    path_length = 1.0 - 0.3 * difficulty
    path_length = m_to_idx(path_length)
    path_width = np.random.uniform(0.4, 0.7)  # Ensure narrow but traversable paths
    path_width = m_to_idx(path_width)
    ramp_height_min, ramp_height_max = 0.05 + 0.25 * difficulty, 0.2 + 0.4 * difficulty
    ramp_length = 0.4 + 0.3 * difficulty
    ramp_length = m_to_idx(ramp_length)

    mid_y = m_to_idx(width) // 2

    def add_narrow_path(start_x, end_x, mid_y):
        half_width = path_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = 0

    def add_narrow_ramp(start_x, end_x, mid_y):
        half_width = path_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        linear_height = np.linspace(0, ramp_height, x2 - x1)[:, None]
        height_field[x1:x2, y1:y2] = linear_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Set first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    toggle = -1
    for i in range(6):  # Create alternating narrow paths and ramps
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        if i % 2 == 0:  # Add narrow path
            add_narrow_path(cur_x, cur_x + path_length + dx, mid_y + dy * toggle)
        else:  # Add ramp
            add_narrow_ramp(cur_x, cur_x + ramp_length + dx, mid_y + dy * toggle)

        # Place goal in the middle of each section
        goals[i + 1] = [cur_x + (path_length + dx) / 2, mid_y + dy * toggle]

        # Alternate path direction
        toggle *= -1
        cur_x += max(path_length, ramp_length) + dx

    # Add final goal behind the last section
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals