import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Widening beam traversal with varying heights and occasional hurdles for balance, precision, and navigation."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up beam and hurdle dimensions
    beam_width_min, beam_width_max = 0.4, 1.2
    beam_width_min, beam_width_max = m_to_idx(beam_width_min), m_to_idx(beam_width_max)
    beam_length = 1.0 + 0.5 * difficulty
    beam_height_var = 0.1 * difficulty
    hurdle_height = 0.2 + 0.3 * difficulty

    platform_gap = 0.2 + 0.5 * difficulty
    platform_gap = m_to_idx(platform_gap)

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, y_center, height):
        half_width = np.random.randint(beam_width_min, beam_width_max)
        x1, x2 = start_x, end_x
        y1, y2 = y_center - half_width, y_center + half_width
        height_field[x1:x2, y1:y2] = height

    def add_hurdle(start_x, width, y_center):
        half_width = width // 2 
        x1, x2 = start_x, start_x + m_to_idx(0.2)
        y1, y2 = y_center - half_width, y_center + half_width
        height_field[x1:x2, y1:y2] = hurdle_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    height = 0

    for i in range(7):
        dx = np.random.randint(dx_min, dx_max)
        dy = (i % 2) * np.random.randint(dy_min, dy_max)
        height += np.random.uniform(-beam_height_var, beam_height_var)  # Vary the height of the beam

        add_beam(cur_x, cur_x + beam_length + dx, mid_y + dy, height)
        if i % 3 == 2:
            add_hurdle(cur_x + (beam_length // 2), beam_width_max, mid_y + dy)  # Add hurdle at the center of beam

        goals[i+1] = [cur_x + (beam_length // 2) + dx // 2, mid_y + dy]
        cur_x += beam_length + dx + platform_gap

    goals[-1] = [cur_x - m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals