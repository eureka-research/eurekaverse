import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Narrow passages with varying heights for the robot to maneuver on."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define beam characteristics
    beam_length = m_to_idx(0.4 + 0.2 * difficulty)  # Varies from 0.4m to 0.6m depending on difficulty
    beam_width = m_to_idx(0.4)  # Constant width

    # Heights will have more variation with increased difficulty
    min_height = 0.05 * difficulty
    max_height = 0.2 + 0.3 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_beam(x, y_center):
        y1 = y_center - beam_width // 2
        y2 = y_center + beam_width // 2
        beam_height = np.random.uniform(min_height, max_height)
        height_field[x:x + beam_length, y1:y2] = beam_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [m_to_idx(1), mid_y]  # First goal at the spawn area

    cur_x = spawn_length
    dx_range = m_to_idx([-0.1, 0.1])  # Small variation in x direction
    dy_range = m_to_idx([-0.5 + 0.3 * difficulty, 0.5 - 0.3 * difficulty])  # Larger variation in y direction for difficulty

    for i in range(7):  # Set up 7 beams
        dx = np.random.randint(dx_range[0], dx_range[1])
        dy = np.random.randint(dy_range[0], dy_range[1])
        add_beam(cur_x + dx, mid_y + dy)

        # Place goal within each beam
        goals[i+1] = [cur_x + dx + beam_length // 2, mid_y + dy]

        # Pass to the next beam
        cur_x += beam_length + dx

    return height_field, goals