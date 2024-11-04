import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Obstacle course with varied platforms and thin beams for balance and navigation challenges."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if isinstance(m, (int, float)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Dimensions and height ranges of platforms and beams
    basic_height_min, basic_height_max = 0.1 + 0.2 * difficulty, 0.3 + 0.4 * difficulty
    beam_width = np.random.uniform(0.4, 0.5)  # Narrower beams for greater difficulty
    beam_width = m_to_idx(beam_width)
    platform_length = 0.8 + 0.4 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width_range = [1.0, 1.4]
    gap_length_range = [0.2, 0.7]
    
    mid_y = m_to_idx(width) // 2

    def add_platform(x_start, length, height, mid_y):
        """Creates a rectangular platform at provided location."""
        width = np.random.uniform(*platform_width_range)
        width = m_to_idx(width)
        x_end = x_start + length
        half_width = width // 2
        height_field[x_start:x_end, mid_y - half_width:mid_y + half_width] = height

    def add_beam(x_start, length, height, mid_y, shift=0):
        """Creates a thin beam for balance challenge."""
        x_end = x_start + length
        y_start = mid_y - beam_width // 2 + shift
        y_end = mid_y + beam_width // 2 + shift
        height_field[x_start:x_end, y_start:y_end] = height

    # Set flat ground for spawning area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(1), mid_y]

    cur_x = spawn_length
    cur_y_shift = 0

    for i in range(7):
        platform_height = np.random.uniform(basic_height_min, basic_height_max)
        gap_length = np.random.uniform(*gap_length_range)
        gap_length = m_to_idx(gap_length)

        if i % 2 == 0:  # Even indices -> platform
            add_platform(cur_x, platform_length, platform_height, mid_y + cur_y_shift)
            goals[i+1] = [cur_x + platform_length / 2, mid_y + cur_y_shift]
            cur_x += platform_length + gap_length
        else:  # Odd indices -> beam
            add_beam(cur_x, platform_length, platform_height, mid_y, shift=cur_y_shift)
            goals[i+1] = [cur_x + platform_length / 2, mid_y + cur_y_shift]
            cur_x += platform_length + gap_length
        
        # Alternate y-shift to promote diverse navigation
        cur_y_shift = (-1) ** i * np.random.randint(0, m_to_idx(0.4))
    
    goals[-1] = [cur_x + m_to_idx(1), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals