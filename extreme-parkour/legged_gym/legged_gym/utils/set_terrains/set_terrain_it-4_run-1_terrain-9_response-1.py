import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Course with alternating stepping platforms and varying-beam widths for the quadruped to balance on, step up, and navigate across gaps."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up obstacle dimensions
    platform_length = 0.8 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    beam_width_min = 0.4 - 0.1 * difficulty
    beam_width_max = 0.8 - 0.1 * difficulty
    beam_width_min = m_to_idx(beam_width_min)
    beam_width_max = m_to_idx(beam_width_max)
    platform_height_min, platform_height_max = 0.1 + 0.05 * difficulty, 0.25 + 0.15 * difficulty
    gap_length = 0.1 + 0.3 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2
    num_platforms = 4  # Alternating platforms

    def add_platform(start_x, end_x, cur_y):
        half_width = (end_x - start_x) // 2
        x1, x2 = start_x, end_x
        y1, y2 = cur_y - half_width, cur_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    # Alternating platforms for stepping
    for i in range(num_platforms):
        dx = np.random.randint(dx_min, dx_max)
        width = np.random.randint(beam_width_min, beam_width_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y)

        # Set goal in the center of the platform
        goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y]

        # Add gap
        cur_x += platform_length + dx + gap_length

    # Add beams of varied widths between platforms
    for i in range(num_platforms, 7):
        dx = np.random.randint(dx_min, dx_max)
        width = np.random.randint(beam_width_min, beam_width_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y)

        # Set goal in the center of the beam
        goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y]

        # Add gap
        cur_x += platform_length + dx + gap_length

    # Add final goal behind the last obstacle
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals