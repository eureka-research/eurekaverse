import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Series of varied height platforms interconnected by narrow beams and small ramps, testing balance and coordination."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up obstacle dimensions
    platform_length = np.random.uniform(0.8, 1.2 - 0.1 * difficulty)
    platform_width = np.random.uniform(0.5, 1.0)
    platform_height_range = [0.0, 0.15 + 0.2 * difficulty]
    beam_length = np.random.uniform(1.0, 2.0 - 0.1 * difficulty)
    beam_width = 0.4

    platform_length = m_to_idx(platform_length)
    platform_width = m_to_idx(platform_width)
    beam_length = m_to_idx(beam_length)
    beam_width = m_to_idx(beam_width)
    gap_length = m_to_idx(0.1 + 0.3 * difficulty)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, length, center_y):
        half_width = platform_width // 2
        x1, x2 = start_x, start_x + length
        y1, y2 = center_y - half_width, center_y + half_width
        platform_height = np.random.uniform(*platform_height_range)
        height_field[x1:x2, y1:y2] = platform_height
        return platform_height
    
    def add_beam(start_x, length, center_y, height_offset):
        half_width = beam_width // 2
        x1, x2 = start_x, start_x + length
        y1, y2 = center_y - half_width, center_y + half_width
        height_field[x1:x2, y1:y2] = height_offset

    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0  # Set spawn area to flat ground
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    current_height = 0.0

    for i in range(7):
        # Adding platforms
        platform_height = add_platform(cur_x, platform_length, mid_y)
        goals[i+1] = [cur_x + platform_length // 2, mid_y]
        cur_x += platform_length + gap_length

        # Adding connecting beams
        random_offset = np.random.uniform(-0.2, 0.2) * ((i % 2) * 2 - 1)  # Alternating offset for balance challenge
        goal_y = mid_y + m_to_idx(random_offset)
        add_beam(cur_x, beam_length, goal_y, platform_height)
        current_height = platform_height
        cur_x += beam_length + gap_length

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]  # Final goal

    return height_field, goals