import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Varied platforms, narrow beams, and tilted ramps for the robot to navigate, jump, and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up obstacle dimensions
    step_length = 0.4 + 0.1 * difficulty
    step_length = m_to_idx(step_length)
    step_width = 0.3 + 0.3 * difficulty
    step_width = m_to_idx(step_width)
    step_height_min, step_height_max = 0.1, 0.25 + 0.15 * difficulty
    narrow_beam_length = 0.8 + 0.2 * difficulty
    narrow_beam_length = m_to_idx(narrow_beam_length)
    narrow_beam_width = 0.3
    narrow_beam_width = m_to_idx(narrow_beam_width)
    beam_height_min, beam_height_max = 0.2 + 0.2 * difficulty, 0.35 + 0.3 * difficulty
    platform_length = 0.8 + 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.6)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.2 + 0.4 * difficulty, 0.05 + 0.6 * difficulty
    ramp_length = 1.0
    ramp_length = m_to_idx(ramp_length)
    ramp_height = 0.2 + 0.4 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_stepping_stone(start_x, mid_y):
        half_width = step_width // 2
        x1 = start_x
        x2 = start_x + step_length
        y1 = mid_y - half_width
        y2 = mid_y + half_width
        step_height = np.random.uniform(step_height_min, step_height_max)
        height_field[x1:x2, y1:y2] = step_height

    def add_narrow_beam(start_x, mid_y, height):
        half_width = narrow_beam_width // 2
        x1 = start_x
        x2 = start_x + narrow_beam_length
        y1 = mid_y - half_width
        y2 = mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_platform(start_x, mid_y):
        half_width = platform_width // 2
        x1 = start_x
        x2 = start_x + platform_length
        y1 = mid_y - half_width
        y2 = mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_ramp(start_x, mid_y, height):
        half_width = platform_width // 2
        x1 = start_x
        x2 = start_x + ramp_length
        y1 = mid_y - half_width
        y2 = mid_y + half_width
        height_field[x1:x2, y1:y2] = np.linspace(0, height, x2-x1)[:, None]

    dx_min = m_to_idx(-0.2)
    dx_max = m_to_idx(0.2)
    dy_min = m_to_idx(-0.2)
    dy_max = m_to_idx(0.2)

    # Set spawn area to flat ground and first goal at the spawn
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    # Stepping stones
    for i in range(2):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_stepping_stone(cur_x, mid_y + dy)
        goals[i+1] = [cur_x + step_length / 2, mid_y + dy]
        cur_x += step_length + dx + step_length

    # Narrow beams
    for i in range(2):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        beam_height = np.random.uniform(beam_height_min, beam_height_max)
        add_narrow_beam(cur_x, mid_y + dy, beam_height)
        goals[i+3] = [cur_x + narrow_beam_length / 2, mid_y + dy]
        cur_x += narrow_beam_length + dx + narrow_beam_length

    # Raised platforms
    for i in range(2):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, mid_y + dy)
        goals[i+5] = [cur_x + platform_length / 2, mid_y + dy]
        cur_x += platform_length + dx + step_length
    
    # Tilted ramp
    dx = np.random.randint(dx_min, dx_max)
    dy = np.random.randint(dy_min, dy_max)
    add_ramp(cur_x, mid_y + dy, ramp_height)
    goals[-2] = [cur_x + ramp_length / 2, mid_y + dy]
    cur_x += ramp_length + dx + step_length

    # Final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals