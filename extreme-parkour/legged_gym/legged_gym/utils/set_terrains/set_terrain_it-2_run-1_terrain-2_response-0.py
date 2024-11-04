import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Narrow beams with varying heights to test the quadruped's balance and agility."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up beam and platform dimensions
    beam_length = 1.0 - 0.3 * difficulty
    beam_length_idx = m_to_idx(beam_length)
    beam_width = 0.2  # Narrow beam width of 0.2 meters
    beam_width_idx = m_to_idx(beam_width)
    beam_height_min, beam_height_max = 0.05 * difficulty, 0.3 * difficulty

    plank_width = np.random.uniform(0.5, 1.0)  # Mildly wider than beam for variety
    plank_width_idx = m_to_idx(plank_width)
    plank_height_min, plank_height_max = 0.05 * difficulty, 0.2 * difficulty

    gap_length = 0.1 + 0.6 * difficulty
    gap_length_idx = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, mid_y):
        """Adds a narrow beam with varying height."""
        half_width = beam_width_idx // 2
        beam_height = np.random.uniform(beam_height_min, beam_height_max)
        height_field[start_x:end_x, mid_y - half_width:mid_y + half_width] = beam_height

    def add_plank(start_x, end_x, mid_y):
        """Adds a wider plank with varying height."""
        half_width = plank_width_idx // 2
        plank_height = np.random.uniform(plank_height_min, plank_height_max)
        height_field[start_x:end_x, mid_y - half_width:mid_y + half_width] = plank_height

    dx_min, dx_max = -0.1, 0.2
    dx_min_idx, dx_max_idx = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min_idx, dy_max_idx = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # First goal near spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    # Begin placing beams and planks
    for i in range(4):  # Alternating 4 beams and 4 planks in total
        dx = np.random.randint(dx_min_idx, dx_max_idx)
        dy = np.random.randint(dy_min_idx, dy_max_idx)

        # Alternate between beams and planks
        if i % 2 == 0:
            add_beam(cur_x, cur_x + beam_length_idx + dx, mid_y + dy)
        else:
            add_plank(cur_x, cur_x + beam_length_idx + dx, mid_y + dy)

        goals[i + 1] = [cur_x + (beam_length_idx + dx) // 2, mid_y + dy]
        cur_x += beam_length_idx + dx + gap_length_idx

    # Fill remaining gap and add last goals behind the final beam
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals