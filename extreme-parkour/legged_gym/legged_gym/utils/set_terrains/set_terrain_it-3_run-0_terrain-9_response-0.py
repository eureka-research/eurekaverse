import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Series of rotating platforms and narrow beams over pits to test balance and agility."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up beam dimensions
    beam_length = 1.2 - 0.3 * difficulty
    beam_length_idx = m_to_idx(beam_length)
    beam_width = 0.4
    beam_width_idx = m_to_idx(beam_width)
    beam_height_min, beam_height_max = 0.1 + 0.1 * difficulty, 0.15 + 0.2 * difficulty
    gap_length = 0.3 + 0.6 * difficulty
    gap_length_idx = m_to_idx(gap_length)

    # Set up rotating platform dimensions
    platform_length = 1.0 - 0.2 * difficulty
    platform_length_idx = m_to_idx(platform_length)
    platform_width = 0.8 + 0.2 * difficulty
    platform_width_idx = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.15 + 0.2 * difficulty, 0.25 + 0.25 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, mid_y):
        half_width = beam_width_idx // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        beam_height = np.random.uniform(beam_height_min, beam_height_max)
        height_field[x1:x2, y1:y2] = beam_height

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width_idx // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    dx_min, dx_max = m_to_idx(-0.1), m_to_idx(0.1)
    dy_min, dy_max = m_to_idx(-0.4), m_to_idx(0.4)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at the end of the spawn area

    cur_x = spawn_length
    for i in range(4):  # Interleave 4 beams and 4 platforms
        # Adding a beam
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_beam(cur_x, cur_x + beam_length_idx + dx, mid_y + dy)

        # Put goal in the center of the beam
        goals[i * 2 + 1] = [cur_x + (beam_length_idx + dx) / 2, mid_y + dy]

        # Add gap before the platform
        cur_x += beam_length_idx + dx + gap_length_idx

        # Adding a rotating platform
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + platform_length_idx + dx, mid_y + dy)

        # Put goal in the center of the platform
        goals[i * 2 + 2] = [cur_x + (platform_length_idx + dx) / 2, mid_y + dy]

        # Add another gap before the next beam
        cur_x += platform_length_idx + dx + gap_length_idx

    # Final goal just beyond the last platform
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals