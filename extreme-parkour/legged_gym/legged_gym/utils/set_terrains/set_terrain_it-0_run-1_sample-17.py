import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """A sequence of hurdles of increasing heights for the quadruped to jump over."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    def add_hurdle(start_x, end_x, y_positions, height):
        """Adds a hurdle across specified y_positions with a given height."""
        for y_pos in y_positions:
            height_field[start_x:end_x, y_pos] = height

    # Calculate hurdle and gap parameters
    hurdle_width = 0.4
    hurdle_width = m_to_idx(hurdle_width)
    gap_length = 2.0 - difficulty * 1.5  # Smaller gap at higher difficulty
    gap_length = m_to_idx(gap_length)
    min_hurdle_height = 0.1
    max_hurdle_height = 0.4 + difficulty * 0.6  # Taller hurdles at higher difficulty
    num_hurdles = 6  # Adding six hurdles in total

    # Set spawn area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    mid_y = m_to_idx(width) // 2
    goals[0] = [1, mid_y]  # Initial spawn point goal

    cur_x = spawn_length
    for i in range(1, num_hurdles + 1):
        # Random hurdle height based on difficulty
        hurdle_height = min_hurdle_height + difficulty * (max_hurdle_height - min_hurdle_height) * (i / num_hurdles)
        start_x, end_x = cur_x, cur_x + hurdle_width
        
        # Adding hurdle in the middle of the width
        y_positions = list(range(mid_y - m_to_idx(1), mid_y + m_to_idx(1)))
        add_hurdle(start_x, end_x, y_positions, hurdle_height)
        
        # Place the goal right after each hurdle
        goals[i] = [end_x + m_to_idx(0.5), mid_y]

        # Add gap after the hurdle
        cur_x += hurdle_width + gap_length

    # Final goal at the end of the terrain
    goals[-1] = [m_to_idx(length - 0.5), mid_y]

    return height_field, goals