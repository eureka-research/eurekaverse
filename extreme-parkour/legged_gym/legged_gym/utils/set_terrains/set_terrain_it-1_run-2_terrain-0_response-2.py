import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Mixed challenges with higher platforms, narrow beams, and varied gap jumps."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define properties of platforms and beams
    platform_length = 0.7 + 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 0.5 + 0.2 * difficulty
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.2 * difficulty, 0.5 + 0.3 * difficulty
    beam_length = 0.6 + 0.2 * difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = 0.2 + 0.1 * difficulty
    beam_width = m_to_idx(beam_width)
    gap_length_min, gap_length_max = 0.2 + 0.3 * difficulty, 0.5 + 0.5 * difficulty
    gap_length_min, gap_length_max = m_to_idx(gap_length_min), m_to_idx(gap_length_max)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, start_y, end_x, end_y):
        """Adds a platform to the terrain."""
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[start_x:end_x, start_y:end_y] = platform_height

    def add_beam(start_x, start_y, end_x, end_y, height):
        """Adds a narrow beam to the terrain."""
        height_field[start_x:end_x, start_y:end_y] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x, cur_y = spawn_length, mid_y - platform_width // 2

    # Create series of platforms and beams with varied gaps
    for i in range(1, 8):
        if i % 2 == 1:  # Add platform
            dx = np.random.randint(0, m_to_idx(0.2))
            dy = np.random.randint(-m_to_idx(0.4), m_to_idx(0.4))
            add_platform(cur_x + dx, cur_y + dy, cur_x + platform_length + dx, cur_y + platform_width + dy)
            goals[i] = [cur_x + platform_length // 2 + dx, cur_y + platform_width // 2 + dy]
            cur_x += platform_length + dx + np.random.randint(gap_length_min, gap_length_max)
        else:  # Add narrow beam
            height = np.random.uniform(0.1, 0.2)
            dx = np.random.randint(0, m_to_idx(0.2))
            dy = np.random.randint(-m_to_idx(0.2), m_to_idx(0.2))
            add_beam(cur_x + dx, cur_y + dy, cur_x + beam_length + dx, cur_y + beam_width + dy, height)
            goals[i] = [cur_x + beam_length // 2 + dx, cur_y + beam_width // 2 + dy]
            cur_x += beam_length + dx + np.random.randint(gap_length_min, gap_length_max)
            
    # Final goal after the last obstacle
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals