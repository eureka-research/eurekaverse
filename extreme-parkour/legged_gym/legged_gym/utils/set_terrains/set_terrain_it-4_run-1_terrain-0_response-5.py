import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Challenging course with alternating slopes and narrow elevated beams."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define parameters for slopes and beams
    slope_height_min, slope_height_max = 0.2 * difficulty, 0.5 * difficulty
    beam_width_min, beam_width_max = 0.4, 0.8 - 0.3 * difficulty
    beam_height_min, beam_height_max = 0.3 * difficulty, 0.6 * difficulty
    gap_length = 0.2 + 0.4 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    # Helper Functions
    def add_slope(start_x, end_x, mid_y, height):
        slope = np.linspace(0, height, end_x - start_x)
        for i in range(start_x, end_x):
            height_field[i, mid_y - 3:mid_y + 3] = slope[i - start_x]

    def add_beam(start_x, end_x, mid_y, width, height):
        half_width = m_to_idx(width / 2)
        y1 = mid_y - half_width
        y2 = mid_y + half_width
        height_field[start_x:end_x, y1:y2] = height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.0, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [m_to_idx(1), mid_y]

    current_x = spawn_length

    # Alternating slopes and beams
    for i in range(6):
        if i % 2 == 0:  # Add slope
            slope_length = m_to_idx(1.2)
            slope_height = np.random.uniform(slope_height_min, slope_height_max)
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)

            add_slope(current_x, current_x + slope_length + dx, mid_y + dy, slope_height)
            goals[i + 1] = [current_x + slope_length / 2, mid_y + dy]
            current_x += slope_length + dx + gap_length
        else:  # Add beam
            beam_length = m_to_idx(1.0)
            beam_width = np.random.uniform(beam_width_min, beam_width_max)
            beam_height = np.random.uniform(beam_height_min, beam_height_max)
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)

            add_beam(current_x, current_x + beam_length + dx, mid_y + dy, beam_width, beam_height)
            goals[i + 1] = [current_x + beam_length / 2, mid_y + dy]
            current_x += beam_length + dx + gap_length

    # Add final goal and fill remaining terrain
    goals[-1] = [current_x + m_to_idx(0.5), mid_y]
    height_field[current_x:, :] = 0

    return height_field, goals