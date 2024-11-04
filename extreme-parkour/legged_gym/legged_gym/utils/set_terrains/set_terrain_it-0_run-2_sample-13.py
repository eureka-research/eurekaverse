import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Alternating raised beams and trenches to test balance and agility"""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Configurations
    beam_height_min, beam_height_max = 0.2 * difficulty, 0.4 * difficulty
    trench_depth_min, trench_depth_max = -0.15 * difficulty, -0.3 * difficulty
    beam_width = m_to_idx(0.4)
    trench_width = m_to_idx(0.6 + 0.4 * difficulty)
    beam_length = m_to_idx(1.2)
    trench_length = m_to_idx(1.2)

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, mid_y):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        beam_height = np.random.uniform(beam_height_min, beam_height_max)
        height_field[x1:x2, y1:y2] = beam_height

    def add_trench(start_x, end_x, mid_y):
        half_width = trench_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        trench_depth = np.random.uniform(trench_depth_min, trench_depth_max)
        height_field[x1:x2, :] = trench_depth

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    for i in range(4):  # Set up 4 beam-trench pairs
        # Add beam
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_beam(cur_x, cur_x + beam_length + dx, mid_y + dy)

        # Put goal in the center of the beam
        goals[i*2+1] = [cur_x + (beam_length + dx) / 2, mid_y + dy]

        # Add trench after beam
        cur_x += beam_length + dx
        dy = np.random.randint(dy_min, dy_max)
        add_trench(cur_x, cur_x + trench_length + dx, mid_y + dy)

        # Put goal in the center of the trench
        goals[i*2+2] = [cur_x + (trench_length + dx) / 2, mid_y + dy]

        cur_x += trench_length + dx

    # Add final goal behind the last trench, fill in the remaining gap with flat ground
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals