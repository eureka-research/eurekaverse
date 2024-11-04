import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Multiple hurdles and narrow beams require the quadruped to balance and jump across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Setting hurdle dimensions
    hurdle_height_min = 0.2 + 0.3 * difficulty  # Min height of 0.2m, max height of 0.5m
    hurdle_height_max = 0.3 + 0.6 * difficulty  # Min height of 0.3m, max height of 0.9m
    hurdle_width = 0.1 + 0.2 * difficulty  # Min width of 0.1m, max width of 0.3m
    hurdle_width = m_to_idx(hurdle_width)  # Convert to index units
    gap_length = 0.4 + 0.4 * difficulty  # Gaps between obstacles

    # Setting narrow beam dimensions
    beam_length = 1.0 - 0.6 * difficulty  # Beams get shorter with higher difficulty
    beam_length = m_to_idx(beam_length)  # Convert to index units
    beam_width = 0.3 - 0.2 * difficulty  # Beams get narrower with higher difficulty
    beam_width = m_to_idx(beam_width)  # Convert to index units
    mid_y = m_to_idx(width) // 2  # Center line of the width

    def add_hurdle(x, mid_y):
        half_width = hurdle_width // 2
        y1, y2 = mid_y - half_width, mid_y + half_width
        hurdle_height = np.random.uniform(hurdle_height_min, hurdle_height_max)
        height_field[x, y1:y2] = hurdle_height

    def add_beam(start_x, end_x, mid_y):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = 0.1  # Slight elevation for the beams 

    # Set the spawning area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [1, mid_y]  # First goal slightly ahead of the spawn

    cur_x = spawn_length
    alternating = True  # To alternate between hurdles and beams
    
    for i in range(6):  # Alternating between hurdles and beams
        if alternating:
            add_hurdle(cur_x, mid_y)
            goals[i + 1] = [cur_x, mid_y]
            cur_x += m_to_idx(0.3)
        else:
            next_x = cur_x + beam_length
            add_beam(cur_x, next_x, mid_y)
            goals[i + 1] = [(cur_x + next_x) // 2, mid_y]
            cur_x = next_x
        cur_x += gap_length
        alternating = not alternating

    # Add final goal
    goals[7] = [cur_x - m_to_idx(0.5), mid_y]

    return height_field, goals