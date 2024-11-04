import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Increased difficulty terrain with a mix of narrow beams, high platforms, and wider gaps."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set dynamic parameters for beams and platforms based on difficulty
    beam_length = 1.0 - 0.2 * difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = 0.4
    beam_width = m_to_idx(beam_width)
    beam_height_min, beam_height_max = 0.15 + 0.15 * difficulty, 0.25 + 0.35 * difficulty

    platform_length = 1.0 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.4)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.20 + 0.15 * difficulty, 0.40 + 0.35 * difficulty

    gap_length_min = 0.3 + 0.5 * difficulty
    gap_length_max = 0.5 + 0.6 * difficulty
    gap_length_min, gap_length_max = m_to_idx(gap_length_min), m_to_idx(gap_length_max)

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, mid_y, width, height):
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_platform(start_x, end_x, mid_y, width, height):
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

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
    for i in range(6):  # Combination of 6 different obstacles
        if i % 2 == 0:  # Alternating beams and platforms
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)

            if i % 4 == 0:  # Narrow beam
                height = np.random.uniform(beam_height_min, beam_height_max)
                add_beam(cur_x, cur_x + beam_length + dx, mid_y + dy, beam_width, height)
                goals[i + 1] = [cur_x + (beam_length + dx) / 2, mid_y + dy]
                cur_x += beam_length + dx
            else:  # Wide platform
                height = np.random.uniform(platform_height_min, platform_height_max)
                add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_width, height)
                goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
                cur_x += platform_length + dx

            # Add randomized gaps to increase difficulty
            gap_length = np.random.randint(gap_length_min, gap_length_max)
            height_field[cur_x:cur_x + gap_length, :] = -1.0  # Pit to force jumping
            cur_x += gap_length

        else:  # Sloped beam to test ramp navigation
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)
            beam_height = np.random.uniform(beam_height_min - 0.1, beam_height_max)

            slant_length = m_to_idx(0.5 * (beam_length + dx))
            slant = np.linspace(0, beam_height, num=slant_length)

            half_width = beam_width // 2
            x2 = cur_x + slant_length
            y_start, y_end = mid_y + dy - half_width, mid_y + dy + half_width

            for ii in range(cur_x, x2):
                height_field[ii, y_start:y_end] = slant[ii - cur_x]

            # Flat top of the ramp
            height_field[x2:cur_x + beam_length + dx, y_start:y_end] = beam_height

            goals[i + 1] = [cur_x + (beam_length + dx) / 2, mid_y + dy]
            cur_x += beam_length + dx

            # Add randomized gaps to increase difficulty
            gap_length = np.random.randint(gap_length_min, gap_length_max)
            height_field[cur_x:cur_x + gap_length, :] = -1.0  # Pit to force jumping
            cur_x += gap_length
    
    # Final goal behind the last obstacle
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals