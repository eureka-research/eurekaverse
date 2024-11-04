import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Narrow beams and larger platforms for balance and transition skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Terrain dimensions and parameters
    mid_y = m_to_idx(width) // 2
    beam_height_min, beam_height_max = 0.05, 0.4 * difficulty
    beam_width = m_to_idx(0.2)  # Narrow beam, 0.2 meters
    platform_width = m_to_idx(1.2)  # Broad platform, 1.2 meters
    platform_length = m_to_idx(1.0 - 0.3 * difficulty)
    gap_length = m_to_idx(0.5 + 0.5 * difficulty)

    def add_beam(start_x, end_x, mid_y):
        """Add a narrow beam to the terrain."""
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        beam_height = np.random.uniform(beam_height_min, beam_height_max)
        height_field[x1:x2, y1:y2] = beam_height

    def add_platform(start_x, end_x, mid_y):
        """Add a broad platform to the terrain."""
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(beam_height_min, beam_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    cur_x = m_to_idx(2)
    height_field[:cur_x, :] = 0
    goals[0] = [cur_x / 2, mid_y]

    def add_goal(i, cur_x, length, mid_y):
        """Add a goal at the center of the current surface."""
        goals[i] = [cur_x + length // 2, mid_y]

    # Place obstacles and goals
    for i in range(7):
        if i % 2 == 0:  # Add a narrow beam
            beam_length = platform_length if i == 0 else platform_length - m_to_idx(0.2)
            add_beam(cur_x, cur_x + beam_length, mid_y)
            add_goal(i + 1, cur_x, beam_length, mid_y)
            cur_x += beam_length + gap_length
        else:  # Add a broad platform
            add_platform(cur_x, cur_x + platform_length, mid_y)
            add_goal(i + 1, cur_x, platform_length, mid_y)
            cur_x += platform_length + gap_length

    goals[-1] = [cur_x - gap_length / 2, mid_y]
    
    # Final area should be flat
    height_field[cur_x:, :] = 0

    return height_field, goals