import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Series of staggered narrow beams with height variations for the quadruped to balance and navigate through."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    # Initialize height field and goals
    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Beam dimensions and setup
    beam_width = 0.2 + 0.1 * difficulty
    beam_width = m_to_idx(beam_width)
    beam_length = 1.0 + 0.2 * difficulty
    beam_length = m_to_idx(beam_length)
    beam_height_min, beam_height_max = 0.1 + 0.1 * difficulty, 0.2 + 0.4 * difficulty
    gap_length = 0.4 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, center_y, height):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = center_y - half_width, center_y + half_width
        height_field[x1:x2, y1:y2] = height

    # Flatten the spawn area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(6):  # Create a sequence of beams with gaps
        dx = np.random.randint(-m_to_idx(0.1), m_to_idx(0.1))
        dy = np.random.randint(-m_to_idx(0.3), m_to_idx(0.3))
        beam_height = np.random.uniform(beam_height_min, beam_height_max)
        add_beam(cur_x, cur_x + beam_length + dx, mid_y + dy, beam_height)

        # Place goal in the middle of each beam
        goals[i + 1] = [cur_x + (beam_length + dx) / 2, mid_y + dy]

        # Increment current x by the length of the beam and the gap
        cur_x += beam_length + dx + gap_length

    # Place the final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals