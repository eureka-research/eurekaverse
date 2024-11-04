import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Combines jumping gaps, narrow platforms, and varied-height platforms for the quadruped to navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Parameters
    platform_width_min, platform_width_max = 0.4, 1.0  # Testing balance by making platforms narrower
    gap_width = 0.2 + 0.5 * difficulty  # Increase gap width with difficulty
    platform_height_min, platform_height_max = 0.05 + 0.20 * difficulty, 0.1 + 0.35 * difficulty

    platform_width_min, platform_width_max = m_to_idx([platform_width_min, platform_width_max])
    gap_width = m_to_idx(gap_width)
    mid_y = m_to_idx(width) // 2

    # Function to create a platform
    def add_platform(start_x, length, width, height, mid_y):
        half_width = width // 2
        height_field[start_x:start_x+length, mid_y-half_width:mid_y+half_width] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at the spawn point

    # Create terrain
    cur_x = spawn_length
    for i in range(7):
        # Determine platform parameters
        platform_length = m_to_idx(1.0)  # Fixed length for uniformity
        platform_width = np.random.randint(platform_width_min, platform_width_max)
        platform_height = np.random.uniform(platform_height_min, platform_height_max)

        # Create platform
        add_platform(cur_x, platform_length, platform_width, platform_height, mid_y)

        # Set goal on the platform
        goals[i+1] = [cur_x + platform_length // 2, mid_y]
        
        # Add gap before the next platform
        cur_x += platform_length + gap_width

    # Fill the rest of the terrain to flat ground
    height_field[cur_x:, :] = 0
    goals[-1] = [m_to_idx(length) - m_to_idx(0.5), mid_y]  # Make sure final goal is within bounds

    return height_field, goals