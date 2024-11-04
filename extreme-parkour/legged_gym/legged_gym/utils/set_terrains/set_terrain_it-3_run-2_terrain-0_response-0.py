import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Series of narrow beams and varied-height platforms with undulating terrain for the robot to climb up and navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up beam and platform dimensions
    beam_length = 1.0 - 0.3 * difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = np.random.uniform(0.4, 0.6)
    beam_width = m_to_idx(beam_width)
    beam_height_min, beam_height_max = 0.1 + 0.2 * difficulty, 0.3 + 0.25 * difficulty
    
    platform_width = 0.8 + 0.2 * difficulty  # Platforms between the beams
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.3 + 0.25 * difficulty
    
    gap_length = 0.2 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, mid_y, height):
        half_width = beam_width // 2
        height_field[start_x:end_x, mid_y - half_width: mid_y + half_width] = height

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        height_field[start_x:end_x, mid_y - half_width: mid_y + half_width] = height

    dx_min, dx_max = -0.05, 0.05
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.1, 0.1
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)
    
    height_field[0:m_to_idx(2), :] = 0  # Flat spawn area
    
    goals[0] = [m_to_idx(1), mid_y]
    
    cur_x = m_to_idx(2)
    i = 1
    while i < 7:  # Set up structure: platform-beam-platform-beam...
        dx, dy = np.random.randint(dx_min, dx_max), np.random.randint(dy_min, dy_max)
        
        if i % 2 == 1:  # Add a platform
            height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, cur_x + platform_width, mid_y + dy, height)
            goals[i] = [cur_x + platform_width / 2, mid_y + dy]
            cur_x += platform_width + gap_length
        else:  # Add a beam
            height = np.random.uniform(beam_height_min, beam_height_max)
            add_beam(cur_x, cur_x + beam_length, mid_y + dy, height)
            goals[i] = [cur_x + beam_length / 2, mid_y + dy]
            cur_x += beam_length + gap_length

        i += 1
    
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0  # Flat area after last obstacle
    
    return height_field, goals