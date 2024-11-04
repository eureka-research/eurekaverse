import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Combination of staggered elevated platforms, directional ramps, and narrow balance beams to challenge navigation, balance, and agility."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    mid_y = m_to_idx(width) // 2

    platform_min_len, platform_max_len = 0.8, 1.2  # meters
    platform_min_width, platform_max_width = 0.4, 0.8  # meters
    platform_height_min, platform_height_max = 0.1, 0.3 + 0.2 * difficulty  # meters
    gap_min_len, gap_max_len = 0.4, 0.8 + 0.4 * difficulty  # meters
    
    def add_platform(start_x, platform_length, platform_width, height):
        half_width = platform_width // 2
        height_field[start_x:(start_x + platform_length), (mid_y - half_width):(mid_y + half_width)] = height

    def add_ramp(start_x, ramp_length, platform_width, height_start, height_end):
        half_width = platform_width // 2
        height_field[start_x:(start_x + ramp_length), (mid_y - half_width):(mid_y + half_width)] = np.linspace(height_start, height_end, ramp_length).reshape(-1, 1)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # First goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]
    
    # Initialize current x
    cur_x = spawn_length
    for i in range(1, 8):
        # Randomize the next platform/beam parameters
        platform_length = np.random.uniform(platform_min_len, platform_max_len)
        platform_length = m_to_idx(platform_length)
        platform_width = np.random.uniform(platform_min_width, platform_max_width)
        platform_width = m_to_idx(platform_width)
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        
        if i % 3 == 0:
            # Every 3rd obstacle is a ramp
            ramp_length = platform_length
            height_start = platform_height
            height_end = np.random.uniform(platform_height_min, platform_height_max)
            add_ramp(cur_x, ramp_length, platform_width, height_start, height_end)
            platform_height = height_end
        else:
            # Add a normal platform
            add_platform(cur_x, platform_length, platform_width, platform_height)

        # Set the goal on this platform
        goals[i] = [cur_x + platform_length // 2, mid_y]

        # Advance cur_x accounting for the length of the current obstacle and a random gap
        gap_length = np.random.uniform(gap_min_len, gap_max_len)
        gap_length = m_to_idx(gap_length)
        cur_x += platform_length + gap_length

    # Add final goal after the last platform
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    
    return height_field, goals