import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Combination of various sized platforms, narrow beams over pits, and elevated steps to test balance and agility."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length = 0.8 - 0.4 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 0.7
    platform_width = m_to_idx(platform_width)
    beam_width = 0.4
    beam_width = m_to_idx(beam_width)
    platform_height_min, platform_height_max = 0.1 + 0.25 * difficulty, 0.25 + 0.5 * difficulty
    gap_length = 0.2 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, width, height):
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_narrow_beam(start_x, end_x, mid_y, width):
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = 0.0  # height set to flat

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    
    for i in range(3):  # Set up combinations of 3 platforms
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_width, platform_height)

        # Place goals at center of each platform
        goals[i + 1] = [cur_x + platform_length // 2, mid_y + dy]

        # Add gap
        cur_x += platform_length + dx + gap_length
    
    for i in range(3, 6):  # Set up 3 narrow beams
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_narrow_beam(cur_x, cur_x + platform_length + dx, mid_y + dy, beam_width)

        # Place goals at center of each narrow beam
        goals[i + 1] = [cur_x + platform_length // 2, mid_y + dy]

        # Add gap
        cur_x += platform_length + dx + gap_length
    
    for i in range(6, 8):  # Set up 2 elevated steps
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        step_height = np.random.uniform(platform_height_min * 2, platform_height_max * 2)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_width * 0.5, step_height)

        # Place goals at center of each step
        goals[i + 1] = [cur_x + platform_length // 2, mid_y + dy]

        # Add gap
        cur_x += platform_length + dx + gap_length
    
    # Make final goal behind the last obstacle
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals