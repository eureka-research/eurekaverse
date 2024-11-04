import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Combination of narrow beams and raised platforms for an increased challenge."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Parameters for raised platforms and beams
    platform_length = 1.0 - 0.4 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width_min = 0.6  # Narrower platforms
    platform_width_max = 1.0
    platform_width_min = m_to_idx(platform_width_min)
    platform_width_max = m_to_idx(platform_width_max)

    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.15 + 0.25 * difficulty
    beam_width = 0.4  # Fixed narrow beam width
    beam_width = m_to_idx(beam_width)
    beam_length_min = 0.4  # Minimum beam length
    beam_length_max = 1.0  # Maximum beam length
    beam_length_min = m_to_idx(beam_length_min)
    beam_length_max = m_to_idx(beam_length_max)

    gap_length_min = 0.2
    gap_length_min = m_to_idx(gap_length_min)
    gap_length_max = 0.8 + 0.6 * difficulty
    gap_length_max = m_to_idx(gap_length_max)

    mid_y = m_to_idx(width) // 2

    def add_platform(center_x, center_y, size, height):
        half_size_length = size[0] // 2
        half_size_width = size[1] // 2
        x1, x2 = center_x - half_size_length, center_x + half_size_length
        y1, y2 = center_y - half_size_width, center_y + half_size_width
        height_field[x1:x2, y1:y2] = height

    def add_beam(start_x, mid_y, length, direction):
        if direction == 'horizontal':
            x1, x2 = start_x, start_x + length
            y1, y2 = mid_y - beam_width // 2, mid_y + beam_width // 2
        else:
            x1, x2 = start_x - beam_width // 2, start_x + beam_width // 2
            y1, y2 = mid_y, mid_y + length
        
        beam_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = beam_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(3):  # Set up 3 beams
        length = np.random.randint(beam_length_min, beam_length_max)
        direction = 'horizontal' if i % 2 == 0 else 'vertical'
        add_beam(cur_x, mid_y, length, direction)

        # Position goal in the middle of the beam
        if direction == 'horizontal':
            goals[i + 1] = [cur_x + length // 2, mid_y]
            cur_x += length + gap_length_min
        else:
            goals[i + 1] = [cur_x, mid_y + length // 2]

    for j in range(3):  # Set up 3 platforms
        size = [np.random.randint(platform_length // 2, platform_length),
                np.random.randint(platform_width_min, platform_width_max)]
        height = np.random.uniform(platform_height_min, platform_height_max)
        add_platform(cur_x, mid_y, size, height)

        goals[j + 4] = [cur_x, mid_y]
        cur_x += size[0] + gap_length_max

    # Add final goal behind the last platform
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals