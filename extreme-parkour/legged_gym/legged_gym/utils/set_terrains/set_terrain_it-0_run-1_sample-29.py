import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Stepping stones obstacle course over water pits, requiring precise navigation."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up stepping stone dimensions
    step_length = 0.5 + 0.2 * difficulty  # Stone length varies with difficulty
    step_length = m_to_idx(step_length)
    step_width = np.random.uniform(0.5, 0.7)  # Ensure stepping stones are narrow
    step_width = m_to_idx(step_width)
    step_height = 0.1 + 0.15 * difficulty  # Height increases with difficulty
    water_height = -0.5  # Set water level to be a constant negative height
    step_gap_min = 0.3 - 0.1 * difficulty
    step_gap_max = 0.5 - 0.2 * difficulty
    step_gap_min, step_gap_max = m_to_idx(step_gap_min), m_to_idx(step_gap_max)

    field_bounds_x, field_bounds_y = m_to_idx(length), m_to_idx(width)
    mid_y = field_bounds_y // 2

    def add_stepping_stone(start_x, end_x, center_y):
        half_width = step_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = center_y - half_width, center_y + half_width
        height_field[x1:x2, y1:y2] = step_height

    dx_range = [-step_gap_max, step_gap_min] if np.random.rand() < 0.5 else [step_gap_min, step_gap_max]
    dy_range = [-step_width // 2, step_width // 2]  # Allow slight shifts in y-axis within the stepping stone range

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # Put first goal at spawn, slightly behind the quadruped
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Set water pits between stepping stones
    height_field[spawn_length:, :] = water_height

    cur_x = spawn_length
    for i in range(6):  # Set up 6 stepping stones
        dx = random.randint(*dx_range) 
        dy = random.randint(-dy_range[1], dy_range[1])
        add_stepping_stone(cur_x, cur_x + step_length, mid_y + dy)

        # Put goal in the center of the stepping stone
        goals[i+1] = [cur_x + step_length // 2, mid_y + dy]

        # Add between-step gapping
        cur_x += step_length + dx

    # Add final goal behind the last stepping stone, fill in the remaining gap with flat ground
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals