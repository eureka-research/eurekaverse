import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Combination of ramps, platforms, and narrow beams to test climbing, balancing, and navigation skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and ramp dimensions
    ramp_length = 1.0 - 0.3 * difficulty
    ramp_length = m_to_idx(ramp_length)
    ramp_height_min, ramp_height_max = 0.1 + 0.2 * difficulty, 0.3 + 0.4 * difficulty
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_height_min, platform_height_max = 0.2 + 0.2 * difficulty, 0.4 + 0.5 * difficulty
    beam_width = np.random.uniform(0.4, 0.6)
    beam_width = m_to_idx(beam_width)
    gap_length = 0.3 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)
    
    mid_y = m_to_idx(width) // 2
    
    def add_ramp(start_x, end_x, mid_y, height):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slant = np.linspace(0, height, x2 - x1)[None, :]
        slant = np.broadcast_to(slant, (y2 - y1, x2 - x1))
        height_field[x1:x2, y1:y2] = slant.T
    
    def add_platform(start_x, end_x, mid_y, height):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height
    
    def add_beam(start_x, end_x, mid_y, height):
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - beam_width // 2, mid_y + beam_width // 2
        height_field[x1:x2, y1:y2] = height
    
    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(2):  # Multiple ramps
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        add_ramp(cur_x, cur_x + ramp_length, mid_y, ramp_height)
        goals[i+1] = [cur_x + ramp_length / 2, mid_y]
        cur_x += ramp_length + gap_length
    
    for i in range(2, 4):  # Multiple platforms
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)
        goals[i+1] = [cur_x + platform_length / 2, mid_y]
        cur_x += platform_length + gap_length
    
    for i in range(4, 6):  # Narrow beam
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        add_beam(cur_x, cur_x + platform_length, mid_y, platform_height)
        goals[i+1] = [cur_x + platform_length / 2, mid_y]
        cur_x += platform_length + gap_length
    
    # Final platform to reach goal 8
    add_platform(cur_x, cur_x + platform_length, mid_y, 0)
    goals[-2] = [cur_x + platform_length / 2, mid_y]
    
    # Last goal
    goals[-1] = [cur_x + platform_length + m_to_idx(0.5), mid_y]
    
    return height_field, goals