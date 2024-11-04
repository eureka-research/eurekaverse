import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Narrow beams with sharp turns testing balance and agility of the quadruped."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    path_width = 0.4  # Fixed narrow path width for the beams
    path_height = 0.2 + 0.3 * difficulty  # As difficulty increases, height of beams increases
    path_width_idx = m_to_idx(path_width)
    path_height_idx = m_to_idx(path_height)
    cur_x = m_to_idx(2)  # Starting at x=2 meters to avoid spawn collision
    mid_y = m_to_idx(width / 2)  # Starting at middle of the width

    def add_narrow_path(start_x, end_x, y_center):
        half_width = path_width_idx // 2
        height_field[start_x:end_x, y_center-half_width:y_center+half_width+1] = path_height

    dx_choices = [1.0, 1.5, 2.0]  # Varying length of narrow paths
    dx_choices_idx = [m_to_idx(dx) for dx in dx_choices]

    turns = [(0, -2), (2, 0), (0, 2)]  # Straight, turn right, turn left
    num_obstacles = 6

    # Set spawn area to flat ground and initialize first goal
    height_field[:cur_x, :] = 0
    goals[0] = [m_to_idx(1), mid_y]

    for i in range(num_obstacles):
        dx = np.random.choice(dx_choices_idx)
        dy = random.choice([2, -2]) if i % 2 else 0  # Introduce turn every other obstacle
        cur_y = mid_y + m_to_idx(dy)

        end_x = cur_x + dx
        add_narrow_path(cur_x, end_x, mid_y)

        # Place goal in the middle of each path section
        goals[i+1] = [cur_x + dx//2, mid_y]

        if dy != 0:
            # Add goals at the start and end of the turn
            goals[i+1] = [cur_x + dx//2, mid_y + dy//2]
            goals[i+2] = [cur_x + dx, cur_y]
            i += 1

        # Update position for next path
        cur_x = end_x
        mid_y = cur_y

    # Fill remaining goals
    for j in range(i+2, 8):
        goals[j] = [cur_x, mid_y]

    # Ensure ending at flat ground
    height_field[cur_x:, :] = 0

    return height_field, goals