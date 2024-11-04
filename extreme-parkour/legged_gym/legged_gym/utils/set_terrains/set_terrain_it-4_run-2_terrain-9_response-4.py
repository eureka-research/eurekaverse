import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Balance beams, stepping stones, and slight ramps for improved balance and strategic navigation."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Stepping stones and balance beams dimensions
    step_length = 0.3 + 0.2 * difficulty
    step_length = m_to_idx(step_length)
    beam_length = 1.0 - 0.3 * difficulty
    beam_length = m_to_idx(beam_length)
    step_width = 0.3
    step_width = m_to_idx(step_width)
    beam_width = 0.2 + 0.1 * difficulty
    beam_width = m_to_idx(beam_width)
    step_height = 0.1 + 0.2 * difficulty
    ramp_height_min, ramp_height_max = 0.1, 0.2 + 0.3 * difficulty
    gap_length = 0.2 + 0.4 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_stepping_stone(start_x, end_x, start_y, end_y):
        height_field[start_x:end_x, start_y:end_y] = step_height

    def add_balance_beam(start_x, end_x, start_y, end_y):
        height_field[start_x:end_x, start_y:end_y] = step_height

    def add_ramp(start_x, end_x, start_y, end_y, direction):
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        slant = np.linspace(0, ramp_height, num=end_x-start_x)[::direction]
        height_field[start_x:end_x, start_y:end_y] = slant[:, np.newaxis]

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(2):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_stepping_stone(cur_x, cur_x + step_length + dx, mid_y + dy, mid_y + step_width + dy)
        goals[i+1] = [cur_x + (step_length + dx) / 2, mid_y + dy]
        cur_x += step_length + dx + gap_length

    for i in range(2, 4):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_balance_beam(cur_x, cur_x + beam_length + dx, mid_y - beam_width//2, mid_y + beam_width//2 + dy)
        goals[i+1] = [cur_x + (beam_length + dx) / 2, mid_y + dy]
        cur_x += beam_length + dx + gap_length

    for i in range(4, 6):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        direction = (-1) ** i
        add_ramp(cur_x, cur_x + step_length + dx, mid_y - step_width//2, mid_y + step_width//2 + dy, direction)
        goals[i+1] = [cur_x + (step_length + dx) / 2, mid_y + dy]
        cur_x += step_length + dx + gap_length

    for i in range(6, 7):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_balance_beam(cur_x, cur_x + beam_length + dx, mid_y - beam_width//2, mid_y + beam_width//2 + dy)
        goals[i+1] = [cur_x + (beam_length + dx) / 2, mid_y + dy]
        cur_x += beam_length + dx + gap_length

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals