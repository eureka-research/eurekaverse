import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Stepping stones, staggered narrow beams, and mild ramps for the quadruped to navigate and balance across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up stepping stone dimensions
    stepping_stone_width = 0.4 + 0.1 * difficulty
    stepping_stone_width = m_to_idx(stepping_stone_width)
    
    # Set up narrow beam dimensions
    narrow_beam_width = 0.4 + 0.1 * difficulty
    narrow_beam_width = m_to_idx(narrow_beam_width)
    
    # Set up ramp dimensions
    ramp_width = 0.9 - 0.2 * difficulty
    ramp_width = m_to_idx(ramp_width)
    
    max_height = 0.5 * difficulty
    gap_min, gap_max = 0.2, 0.6
    
    mid_y = m_to_idx(width / 2)

    def add_stepping_stone(x, y, height, width):
        half_width = width // 2
        height_field[x:x + width, y - half_width:y + half_width] = height

    def add_beam(x, y, length, width, height):
        half_width = width // 2
        height_field[x:x + length, y - half_width:y + half_width] = height

    def add_ramp(x, y, length, width, height):
        half_width = width // 2
        slant = np.linspace(0, height, num=m_to_idx(length))
        slant = slant[:, None]  # Add a dimension for broadcasting to y
        height_field[x:x + length, y - half_width:y + half_width] = slant

    dx_min, dx_max = m_to_idx(0.2), m_to_idx(1.0)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    dx = dx_min

    for i in range(3):  # Set up 3 stepping stones
        dy = (i % 2 * 2 - 1) * m_to_idx(0.5)
        height = np.random.uniform(0, max_height)
        add_stepping_stone(cur_x, mid_y + dy, height, stepping_stone_width)

        goals[i+1] = [cur_x, mid_y + dy]

        cur_x += dx + m_to_idx(0.4)

    for i in range(2):  # Set up 2 narrow beams
        height = np.random.uniform(0, max_height)
        length = m_to_idx(1.0 + 0.4 * difficulty)
        add_beam(cur_x, mid_y, length, narrow_beam_width, height)

        goals[len(goals) - 3 + i] = [cur_x + length // 2, mid_y]

        cur_x += length + m_to_idx(0.4)

    for i in range(2):  # Set up 2 mild ramps
        height = np.random.uniform(0, max_height)
        length = m_to_idx(1.2 + 0.5 * difficulty)
        add_ramp(cur_x, mid_y, length, ramp_width, height)

        goals[len(goals) - 1 + i] = [cur_x + length // 2, mid_y]

        cur_x += length + dx_min

    goals[-1] = [cur_x, mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals