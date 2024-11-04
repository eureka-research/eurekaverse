import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Obstacle course with staggered platforms and diagonal beams to test balance, climbing, and orientation adjustments."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and beam dimensions
    platform_length = 1.0 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.9, 1.2)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.3 * difficulty, 0.2 + 0.4 * difficulty

    beam_length = 1.2  # Slightly longer to increase difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = 0.4  # Narrow beams for balance
    beam_width = m_to_idx(beam_width)
    beam_height_min, beam_height_max = 0.2, 0.4 + 0.4 * difficulty

    gap_length = 0.2 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_beam(start_x, end_x, mid_y, slope_direction):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        beam_slope = np.linspace(0, slope_direction * (beam_height_max - beam_height_min), num=x2 - x1)
        height_field[x1:x2, y1:y2] = beam_slope[:, np.newaxis]

    dx_min, dx_max = -0.15, 0.15
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.25, 0.25
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0.0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    next_height = np.random.uniform(platform_height_min, platform_height_max)

    for i in range(4):  # First set 4 platforms in a staggered pattern
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, next_height)

        goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length
        next_height = np.random.uniform(platform_height_min, platform_height_max)

    previous_height = next_height

    for i in range(4, 7):  # Now set 3 diagonal beams for balance challenges
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        direction = (-1) ** i  # Alternate slope direction

        add_beam(cur_x, cur_x + beam_length + dx, mid_y + dy, direction)
        goals[i + 1] = [cur_x + (beam_length + dx) / 2, mid_y + dy]
        cur_x += beam_length + dx + gap_length
        previous_height = np.random.uniform(beam_height_min, beam_height_max)

    # Add final goal behind the last beam 
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0.0

    return height_field, goals