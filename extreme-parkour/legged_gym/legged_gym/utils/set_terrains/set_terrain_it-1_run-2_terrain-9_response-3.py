import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Alternating ramps, platforms, and narrow beams requiring climbing, balancing, and jumping."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define various dimensions influenced by difficulty
    platform_length = 1.2 - 0.4 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.2)  # Narrower than before for difficulty
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.05 * difficulty, 0.3 * difficulty
    
    ramp_height_min, ramp_height_max = 0.1 + 0.5 * difficulty, 0.5 + 0.8 * difficulty
    beam_length = 0.6 + 0.2 * difficulty
    beam_width = 0.4 - 0.1 * difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = m_to_idx(beam_width)
    gap_length = 0.3 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_ramp(start_x, end_x, mid_y, upward=True):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max) * (1 if upward else -1)
        slope = np.linspace(0, ramp_height, num=x2-x1)
        slope = slope[:, None] + np.zeros(y2 - y1)
        height_field[x1:x2, y1:y2] = slope

    def add_beam(start_x, end_x, mid_y):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        beam_height = platform_height_max + np.random.uniform(0.1, 0.3)
        height_field[x1:x2, y1:y2] = beam_height

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
    for i in range(6):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        if i % 2 == 0:
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
            cur_x += platform_length + dx
        else:
            add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, upward=(i % 4 == 1))
            goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
            cur_x += platform_length + dx
        
        if i % 3 == 0 and i != 0:
            add_beam(cur_x, cur_x + beam_length + dx, mid_y + dy)
            goals[i+1] = [cur_x + (beam_length + dx) / 2, mid_y + dy]
            cur_x += beam_length + dx

        # Add gap
        cur_x += gap_length
    
    # Add final goal behind the last obstacle, fill in the remaining area
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals