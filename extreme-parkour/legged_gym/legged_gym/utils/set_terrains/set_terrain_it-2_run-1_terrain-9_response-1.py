import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Combination of varying height platforms and angle ramps for the quadruped to climb up and jump across."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up dimensions for platforms and ramps
    platform_length = 0.8 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width_min, platform_width_max = 0.8, 1.2
    platform_width_min = m_to_idx(platform_width_min)
    platform_width_max = m_to_idx(platform_width_max)
    platform_height_min, platform_height_max = 0.1, 0.3
    platform_height_min = platform_height_min * difficulty
    platform_height_max = platform_height_max * difficulty
    gap_length = 0.4 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)
    
    ramp_length = 1.2 - 0.2 * difficulty
    ramp_length = m_to_idx(ramp_length)
    ramp_height_min, ramp_height_max = 0.1, 0.35
    ramp_height_min = ramp_height_min * difficulty
    ramp_height_max = ramp_height_max * difficulty
    
    cur_x = m_to_idx(2)   # Start position after the spawn
    mid_y = m_to_idx(width // 2)
    
    def add_platform(x, y_mid):
        """Adds a platform."""
        half_width = np.random.randint(platform_width_min//2, platform_width_max//2)
        height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x:x + platform_length, y_mid - half_width:y_mid + half_width] = height
        return x + platform_length, height
    
    def add_ramp(x, y_mid, height, slope):
        """Adds a ramp."""
        half_width = np.random.randint(platform_width_min//2, platform_width_max//2)
        rem_height = slope * (height_field.shape[0] - x)
        rem_height = min(rem_height, height * 0.5)
        new_height = height + rem_height
        heights = np.linspace(height, new_height, ramp_length)
        for i in range(ramp_length):
            height_field[x + i, y_mid - half_width:y_mid + half_width] = heights[i]
        return x + ramp_length, new_height
    
    # Make the first goal just in front to start
    goals[0] = [m_to_idx(2) - m_to_idx(0.5), mid_y]
    
    # Create a series of platforms and ramps
    for i in range(7):
        if i % 2 == 0:
            cur_x, cur_height = add_platform(cur_x, mid_y)
        else:
            cur_x, cur_height = add_ramp(cur_x, mid_y, cur_height, 0.5)
        if i < 7-1:  # Add goals only for the first 7
            goals[i + 1] = [cur_x - platform_length // 2, mid_y]
        cur_x += gap_length  # Leave a gap after each obstacle

    # Add final goal slightly beyond the last obstacle
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    return height_field, goals