import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Combination of double-incline ramps, balance beams, and dynamic height platforms for the robot to climb and balance on."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Configuration parameters
    ramp_length = 1.0 - 0.2 * difficulty
    beam_length = 1.2 + 0.2 * difficulty
    platform_length = 1.0 - 0.1 * difficulty

    ramp_length = m_to_idx(ramp_length)
    beam_length = m_to_idx(beam_length)
    platform_length = m_to_idx(platform_length)

    ramp_width = np.random.uniform(0.3, 0.5)
    beam_width_min = 0.1
    beam_width_max = 0.3 + 0.1 * difficulty
    platform_width = np.random.uniform(0.8, 1.2)

    ramp_width = m_to_idx(ramp_width)
    beam_width_min, beam_width_max = m_to_idx(beam_width_min), m_to_idx(beam_width_max)
    platform_width = m_to_idx(platform_width)

    ramp_height_min, ramp_height_max = 0.2 + 0.1 * difficulty, 0.4 + 0.2 * difficulty
    gap_length = 0.2 + 0.4 * difficulty
    gap_length = m_to_idx(gap_length)
    
    mid_y = m_to_idx(width) // 2

    def add_ramp(x, y, length, width, height):
        y1, y2 = y - width // 2, y + width // 2
        ramp_slope = np.linspace(0, height, num=length)
        height_field[x:x+length, y1:y2] = ramp_slope[:, np.newaxis]

    def add_beam(x, y, length, width):
        y1, y2 = y - width // 2, y + width // 2
        height_field[x:x+length, y1:y2] = 0.1  # Slight elevation to simulate a beam

    def add_platform(x, y, length, width, height):
        y1, y2 = y - width // 2, y + width // 2
        height_field[x:x+length, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    dy_max = m_to_idx(0.6)

    # Adding a series of double-incline ramps
    for i in range(2):
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        add_ramp(cur_x, mid_y, ramp_length, ramp_width, ramp_height)
        
        goals[i + 1] = [cur_x + ramp_length // 2, mid_y]
        cur_x += ramp_length + gap_length

    # Adding balance beams with varying widths
    for i in range(2, 5):
        beam_width = np.random.uniform(beam_width_min, beam_width_max)
        add_beam(cur_x, mid_y, beam_length, beam_width)
        
        goals[i + 1] = [cur_x + beam_length // 2, mid_y]
        cur_x += beam_length + gap_length

    # Adding dynamic height platforms
    for i in range(5, 7):
        platform_height = np.random.uniform(0.2, 0.4 + 0.2 * difficulty)
        add_platform(cur_x, mid_y, platform_length, platform_width, platform_height)
        
        goals[i + 1] = [cur_x + platform_length // 2, mid_y]
        cur_x += platform_length + gap_length

    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals