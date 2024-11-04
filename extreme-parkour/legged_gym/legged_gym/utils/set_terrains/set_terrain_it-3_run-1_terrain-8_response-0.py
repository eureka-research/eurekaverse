import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Combines staggered steps, narrow beams, and varied-height platforms for balanced difficulty and feasibility."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up obstacle dimensions
    step_length = 0.5
    step_length = m_to_idx(step_length)
    step_width = 0.4 + 0.4 * difficulty
    step_width = m_to_idx(step_width)
    step_height = 0.15 + 0.15 * difficulty
    gap_length = 0.2 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    narrow_beam_length = 1.0 - 0.3 * difficulty
    narrow_beam_length = m_to_idx(narrow_beam_length)
    narrow_beam_width = 0.4
    narrow_beam_width = m_to_idx(narrow_beam_width)
    beam_height = 0.2 + 0.2 * difficulty

    platform_length = 1.0
    platform_length = m_to_idx(platform_length)
    platform_width = 1.0 + 0.4 * difficulty
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.3 * difficulty, 0.3 + 0.6 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_step(start_x, mid_y):
        half_width = step_width // 2
        x1 = start_x
        x2 = start_x + step_length
        y1 = mid_y - half_width
        y2 = mid_y + half_width
        height_field[x1:x2, y1:y2] = step_height

    def add_narrow_beam(start_x, end_x, mid_y):
        half_width = narrow_beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = beam_height

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height
  
    dx_min, dx_max = m_to_idx(-0.1), m_to_idx(0.1)
    dy_min, dy_max = m_to_idx(-0.4), m_to_idx(0.4)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    # Step 1: Add staggered elevated steps
    for i in range(2):
        add_step(cur_x, mid_y)
        goals[i + 1] = [cur_x + step_length / 2, mid_y]
        cur_x += step_length + gap_length

    # Step 2: Add narrow beam
    add_narrow_beam(cur_x, cur_x + narrow_beam_length, mid_y)
    goals[3] = [cur_x + narrow_beam_length / 2, mid_y]
    cur_x += narrow_beam_length + gap_length

    # Step 3: Add platform
    add_platform(cur_x, cur_x + platform_length, mid_y)
    goals[4] = [cur_x + platform_length / 2, mid_y]
    cur_x += platform_length + gap_length

    # Step 4: Additional narrow beams and steps in sequence
    for i in range(2):
        if i % 2 == 0:
            add_narrow_beam(cur_x, cur_x + narrow_beam_length, mid_y)
            goals[5 + i] = [cur_x + narrow_beam_length / 2, mid_y]
            cur_x += narrow_beam_length + gap_length
        else:
            add_step(cur_x, mid_y)
            goals[5 + i] = [cur_x + step_length / 2, mid_y]
            cur_x += step_length + gap_length

    # Add final goal behind the last beam, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals