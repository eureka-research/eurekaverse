import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Varied elevation walkways with intermittent narrow beams to navigate across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up dimensions and parameters
    walkway_length = 1.2 - 0.3 * difficulty
    walkway_length = m_to_idx(walkway_length)
    walkway_width = np.random.uniform(0.6, 1.0)  # Slightly narrowing walkways
    walkway_width = m_to_idx(walkway_width)
    beam_width = np.random.uniform(0.3, 0.45)  # Very narrow beams
    beam_width = m_to_idx(beam_width)
    walkway_height_min, walkway_height_max = 0.05 + 0.2 * difficulty, 0.1 + 0.35 * difficulty
    beam_height = 0.2 + 0.3 * difficulty
    gap_length = 0.1 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_walkway(start_x, end_x, mid_y):
        """Creates a walkway between start_x and end_x."""
        half_width = walkway_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        walkway_height = np.random.uniform(walkway_height_min, walkway_height_max)
        height_field[x1:x2, y1:y2] = walkway_height

    def add_beam(start_x, end_x, mid_y):
        """Creates a narrow beam between start_x and end_x."""
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = beam_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Set remaining area to be a pit to force navigating on walkways and beams
    height_field[spawn_length:, :] = -1.0

    # Initial position after spawning area
    cur_x = spawn_length
    is_walkway = True

    for i in range(6):  # Set up 6 segments
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        if is_walkway:
            add_walkway(cur_x, cur_x + walkway_length + dx, mid_y + dy)
            goals[i+1] = [cur_x + (walkway_length + dx) / 2, mid_y + dy]
            cur_x += walkway_length + dx + gap_length
            is_walkway = False
        else:
            add_beam(cur_x, cur_x + walkway_length + dx, mid_y + dy)
            goals[i+1] = [cur_x + (walkway_length + dx) / 2, mid_y + dy]
            cur_x += walkway_length + dx + gap_length
            is_walkway = True

    # Add final goal behind the last segment, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals