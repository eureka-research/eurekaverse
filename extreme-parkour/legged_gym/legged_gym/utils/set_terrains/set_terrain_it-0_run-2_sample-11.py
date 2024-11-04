import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Series of narrow beams and wider platforms to test precision and balance of the quadruped."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        if isinstance(m, (list, tuple)):
            return [round(i / field_resolution) for i in m]
        else:
            return np.round(m / field_resolution).astype(np.int16)

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Setting up dimensions for beams and platforms
    beam_width = 0.4  # Keep this narrow for balance test
    beam_width = m_to_idx(beam_width)
    beam_length = 1.0  # Length of each beam
    beam_length = m_to_idx(beam_length)

    platform_width = 1.2 + 0.4 * difficulty  # Slightly wider with difficulty
    platform_width = m_to_idx(platform_width)
    platform_length = 1.0
    platform_length = m_to_idx(platform_length)
    platform_height = 0.1 + 0.3 * difficulty

    gap_length = 0.3 + 0.5 * difficulty  # Increase gap with difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, mid_y):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = 0.1  # Beams are slightly above ground to require precision

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = platform_height  # Platforms are a bit higher for resting points

    # Initial flat ground for spawn area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at spawn

    cur_x = spawn_length
    alternate = True  # Alternate between beam and platform

    for i in range(6):  # Creating 6 obstacles (3 beams, 3 platforms)
        if alternate:
            add_beam(cur_x, cur_x + beam_length, mid_y)
            goals[i+1] = [cur_x + beam_length / 2, mid_y]
            cur_x += beam_length + gap_length
        else:
            add_platform(cur_x, cur_x + platform_length, mid_y)
            goals[i+1] = [cur_x + platform_length / 2, mid_y]
            cur_x += platform_length + gap_length

        alternate = not alternate

    # Last part, a wider platform followed by a beam to end
    add_platform(cur_x, cur_x + platform_length, mid_y)
    goals[7] = [cur_x + platform_length / 2, mid_y]
    height_field[cur_x + platform_length:, :] = 0

    return height_field, goals