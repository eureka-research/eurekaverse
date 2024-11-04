import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Sloped ramps and staggered platforms testing the robot's climb, descend, and jump abilities."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define obstacle configurations
    ramp_length = 1.5 - 0.5 * difficulty  # Length of ramp decreases with difficulty
    ramp_length = m_to_idx(ramp_length)
    ramp_width = m_to_idx(0.6)
    ramp_height_min, ramp_height_max = 0.2, 0.5

    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = m_to_idx(0.7)
    platform_height_min, platform_height_max = 0.1, 0.4
    
    gap_length = 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, height, stagger):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2 + stagger] = height

    def add_ramp(start_x, end_x, height, slope_direction):
        half_width = ramp_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_heights = np.linspace(0, height, num=x2 - x1)[::slope_direction]
        height_field[x1:x2, y1:y2] = ramp_heights[:, None]

    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    # Add a sequence of ramps and platforms
    for i in range(4):
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        slope_direction = 1 if i % 2 == 0 else -1
        add_ramp(cur_x, cur_x + ramp_length, ramp_height, slope_direction)
        goals[i*2 + 1] = [cur_x + ramp_length // 2, mid_y]
        
        cur_x += ramp_length + gap_length

        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        stagger = np.random.randint(-m_to_idx(0.2), m_to_idx(0.2))
        add_platform(cur_x, cur_x + platform_length, platform_height, stagger)
        goals[i*2 + 2] = [cur_x + platform_length // 2, mid_y]
        
        cur_x += platform_length + gap_length

    # Set final goal
    goals[7] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals