import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Narrow beams and small platforms requiring precise foot placement and jumping."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform and beam dimensions
    platform_length = 0.5
    platform_width = 0.5 
    beam_length = 2.0 
    beam_width = 0.2 
    platform_height = 0.1 + 0.3 * difficulty  # Platform height varies with difficulty
    beam_height = 0.1 + 0.3 * difficulty  # Beam height varies with difficulty
    gap_length = 0.4 + 1.0 * difficulty  # Gap length varies with difficulty

    mid_y = m_to_idx(width / 2)

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = platform_height

    def add_beam(start_x, end_x, mid_y):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = beam_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Set remaining area to be a pit
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    for i in range(4):  # Set up 4 platforms
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + m_to_idx(platform_length) + dx, mid_y + dy)

        # Put goal in the center of the platform
        goals[i * 2 + 1] = [cur_x + (m_to_idx(platform_length) + dx) / 2, mid_y + dy]
        cur_x += m_to_idx(platform_length) + dx + m_to_idx(gap_length)

        # Connect platforms with beams
        if i < 3:  # Only place 3 beams between platforms
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)
            add_beam(cur_x, cur_x + m_to_idx(beam_length) + dx, mid_y + dy)
            
            # Put goal in the center of the beam
            goals[i * 2 + 2] = [cur_x + (m_to_idx(beam_length) + dx) / 2, mid_y + dy]
            cur_x += m_to_idx(beam_length) + dx + m_to_idx(gap_length)
    
    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals