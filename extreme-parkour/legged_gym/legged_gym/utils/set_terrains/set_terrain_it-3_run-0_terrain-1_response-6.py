import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Dynamic platforms, rotating beams, and inclined ramps to test the quadruped's adaptability and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform parameters
    platform_length = 0.8 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.2)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.2 * difficulty, 0.05 + 0.28 * difficulty

    # Rotating beam parameters
    beam_length = 1.5 - 0.4 * difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = 0.4  # Narrower to test balance
    beam_width = m_to_idx(beam_width)
    
    # Ramp parameters 
    ramp_height_min, ramp_height_max = 0.1 + 0.2 * difficulty, 0.1 + 0.3 * difficulty
    ramp_length = 1.2 - 0.4 * difficulty 
    ramp_length = m_to_idx(ramp_length)
    gap_length = 0.1 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_rotating_beam(start_x, length, mid_y):
        half_width = beam_width // 2
        x1, x2 = start_x, start_x + length
        y1, y2 = mid_y - half_width, mid_y + half_width
        beam_height = (platform_height_min + platform_height_max) / 2  # Fixed height for rotating beam
        height_field[x1:x2, y1:y2] = beam_height

    def add_ramp(start_x, length, mid_y, direction):
        half_width = platform_width // 2
        x1, x2 = start_x, start_x + length
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        slant = np.linspace(0, ramp_height, num=y2-y1)[::direction]
        slant = slant[None, :]  # Broadcasting to x
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.0, 0.3  # Polarity for alternating
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)
    
    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(4):  # Setting up the course with various obstacles
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        if i % 2 == 0: 
            # Add a moving platform
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        else:
            # Add a rotating beam
            add_rotating_beam(cur_x, beam_length, mid_y + dy)
            goals[i+1] = [cur_x + (beam_length) / 2, mid_y + dy]
        
        # Add gap
        cur_x += platform_length + dx + gap_length

    for i in range(4, 6):  # Adding inclined ramps for the last section
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        direction = (-1) ** i  # Alternating left and right ramps
        dy = dy * direction

        add_ramp(cur_x, ramp_length + dx, mid_y + dy, direction)
        goals[i+1] = [cur_x + (ramp_length + dx) / 2, mid_y + dy]
        cur_x += ramp_length + dx + gap_length
        
    # Add final goal behind the last obstacle, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals