import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Series of hurdles and narrow beams for the robot to traverse across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up hurdle dimensions
    hurdle_length = 0.4
    hurdle_length_idx = m_to_idx(hurdle_length)

    hurdle_width = 1.0 - 0.5 * difficulty  # narrow hurdles at higher difficulty
    hurdle_width_idx = m_to_idx(hurdle_width)

    hurdle_height_min = 0.1
    hurdle_height_max = 0.3 + 0.7 * difficulty  # taller hurdles at higher difficulty

    # Set up narrow beam dimensions
    beam_length = 2.0 - 0.5 * difficulty
    beam_length_idx = m_to_idx(beam_length)

    beam_width = 0.4
    beam_width_idx = m_to_idx(beam_width)

    beam_height = 0.1 + 0.4 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_hurdle(start_x, end_x, mid_y):
        half_width = hurdle_width_idx // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height = np.random.uniform(hurdle_height_min, hurdle_height_max)
        height_field[x1:x2, y1:y2] = height

    def add_beam(start_x, end_x, mid_y):
        half_width = beam_width_idx // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = beam_height

    # Set spawn area to flat ground
    spawn_length_idx = m_to_idx(2)
    height_field[0:spawn_length_idx, :] = 0
    # Put first goal at the end of the spawn area
    goals[0] = [spawn_length_idx - m_to_idx(0.5), mid_y]

    # Start generating hurdles and beams
    cur_x = spawn_length_idx
    num_obstacles = 4  # We will create 4 pairs of obstacles (each pair is hurdle + beam)
    for i in range(num_obstacles):
        # Add hurdle
        add_hurdle(cur_x, cur_x + hurdle_length_idx, mid_y)

        # Set goal after each hurdle
        goals[i*2 + 1] = [cur_x + hurdle_length_idx + m_to_idx(0.2), mid_y]

        # Advance the current x position
        cur_x += hurdle_length_idx + m_to_idx(0.5)
        
        # Add narrow beam
        add_beam(cur_x, cur_x + beam_length_idx, mid_y)

        # Set goal after each beam
        goals[i*2 + 2] = [cur_x + beam_length_idx + m_to_idx(0.2), mid_y]

        # Advance the current x position
        cur_x += beam_length_idx + m_to_idx(0.5)

    # Set the final goal past the last obstacle
    goals[-1] = [cur_x + m_to_idx(1.0), mid_y]
    height_field[cur_x:cur_x + m_to_idx(1.0), :] = 0

    return height_field, goals