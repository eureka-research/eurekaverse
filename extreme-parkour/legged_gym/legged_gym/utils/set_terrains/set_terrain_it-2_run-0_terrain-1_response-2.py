import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Series of staggered small steps and narrow beams for the quadruped to balance and navigate across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define the characteristics of beams and steps
    step_width_min = 0.4
    step_width_max = 0.6
    step_height_min = 0.1
    step_height_max = 0.4 * difficulty
    gap_length_min = 0.1 + 0.2 * difficulty
    gap_length_max = 0.3 + 0.3 * difficulty

    step_length = m_to_idx(1.0)
    beam_width = m_to_idx(0.4)
    step_y_range = np.arange(m_to_idx(step_width_min), m_to_idx(step_width_max) + 1)
    gap_range = np.arange(m_to_idx(gap_length_min), m_to_idx(gap_length_max) + 1)

    mid_y = m_to_idx(width) // 2

    # Place obstacles
    cur_x = m_to_idx(2)
    height_field[0:cur_x, :] = 0
    goals[0] = [1, mid_y]

    for i in range(7):
        step_y_offset = np.random.choice(step_y_range)
        gap_x_offset = np.random.choice(gap_range)

        step_height = np.random.uniform(step_height_min * difficulty, step_height_max * difficulty)
        beam_height = np.random.uniform(step_height_min, step_height_max)

        # Adding staggered steps
        y1 = mid_y - step_y_offset // 2
        y2 = mid_y + step_y_offset // 2

        height_field[cur_x:cur_x + step_length, y1:y2] = step_height

        # Adding gap and beams
        cur_x += step_length + gap_x_offset

        beam_y1 = mid_y - beam_width // 2
        beam_y2 = mid_y + beam_width // 2

        height_field[cur_x:cur_x + step_length, beam_y1:beam_y2] = beam_height

        # Set goal at the middle of steps
        goals[i+1] = [cur_x + step_length // 2, mid_y]

        cur_x += step_length

    # Final section (flat area)
    height_field[cur_x:, :] = 0
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    return height_field, goals