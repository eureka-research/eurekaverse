import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Narrow balance beams and variable height platforms for the robot to balance on and step across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up beam and platform dimensions
    beam_length = 1.6 - 0.5 * difficulty  # The length of each balance beam
    beam_length = m_to_idx(beam_length)
    beam_width = 0.4
    beam_width = m_to_idx(beam_width)
    platform_length = 0.6 + 0.7 * difficulty  # The length of each platform
    platform_length = m_to_idx(platform_length)
    platform_height_min, platform_height_max = 0.1 * difficulty, 0.2 * difficulty + 0.2

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, mid_y, height):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_platform(start_x, end_x, mid_y, height):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = 0, 0.2 * difficulty
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2 * difficulty, 0.2 * difficulty
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(6):  # Alternate between beams and platforms
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        if i % 2 == 0:  # Add beam
            beam_height = 0.1 + 0.2 * difficulty
            add_beam(cur_x, cur_x + beam_length + dx, mid_y + dy, beam_height)
            goals[i+1] = [cur_x + (beam_length + dx) / 2, mid_y + dy]
            cur_x += beam_length + dx
        else:  # Add platform
            platform_height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height)
            goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
            cur_x += platform_length + dx

    # Add the final balance beam to fill in the remaining space
    dx = np.random.randint(dx_min, dx_max)
    dy = np.random.randint(dy_min, dy_max)
    beam_height = 0.1 + 0.2 * difficulty
    add_beam(cur_x, cur_x + beam_length + dx, mid_y + dy, beam_height)
    goals[-1] = [cur_x + (beam_length + dx) / 2, mid_y + dy]
    # Allow the quadruped to finish the course on flat ground
    height_field[cur_x + beam_length + dx:, :] = 0

    return height_field, goals