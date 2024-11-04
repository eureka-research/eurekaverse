import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Combination of raised steps and narrow beams to test balance, climbing, and traversal."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define the size parameters based on difficulty
    step_height_min = 0.1 + 0.2 * difficulty
    step_height_max = 0.3 + 0.3 * difficulty
    step_length = 0.8 - 0.2 * difficulty
    step_width_min = 0.4 + 0.1 * difficulty
    step_width_max = 1.0 - 0.2 * difficulty
    
    beam_width = 0.4 + 0.1 * difficulty
    beam_length = 1.0 - 0.2 * difficulty

    gap_min = 0.2
    gap_max = 1.0

    mid_y = m_to_idx(width / 2)

    def add_step(start_x, end_x, mid_y, width, height):
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_beam(start_x, end_x, mid_y, width):
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = np.random.uniform(step_height_min, step_height_max)

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    alternating_step = True
    for i in range(6):
        if alternating_step:
            width = np.random.uniform(step_width_min, step_width_max)
            height = np.random.uniform(step_height_min, step_height_max)
            add_step(cur_x, cur_x + m_to_idx(step_length), mid_y, m_to_idx(width), height)
            goals[i+1] = [cur_x + m_to_idx(step_length / 2), mid_y]

            cur_x += m_to_idx(step_length) + np.random.uniform(m_to_idx(gap_min), m_to_idx(gap_max))
        else:
            add_beam(cur_x, cur_x + m_to_idx(beam_length), mid_y, m_to_idx(beam_width))
            goals[i+1] = [cur_x + m_to_idx(beam_length / 2), mid_y]

            cur_x += m_to_idx(beam_length) + np.random.uniform(m_to_idx(gap_min), m_to_idx(gap_max))

        alternating_step = not alternating_step

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals