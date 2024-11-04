import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Mixed platforms and gaps with varying heights for the robot to navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up variables for platforms and gaps
    platform_length_min, platform_length_max = 0.8, 1.2
    platform_length_range = platform_length_max - platform_length_min
    gap_length_min, gap_length_max = 0.3, 1.0
    platform_height_min, platform_height_max = 0.1 * difficulty, 0.5 * difficulty

    platform_width_min, platform_width_max = 0.5, 1.2
    platform_width_range = platform_width_max - platform_width_min

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = int(np.random.uniform(platform_width_min, platform_width_max) / field_resolution) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # Put first goal at spawn point
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    # Create mixed platforms and gaps
    for i in range(6):
        # Determine platform dimensions and position
        platform_length = random.uniform(platform_length_min, platform_length_max) * min(1 + 0.5 * difficulty, 1.5)
        platform_length = m_to_idx(platform_length)
        gap_length = random.uniform(gap_length_min, gap_length_max) * min(1 - 0.5 * difficulty, 1)
        gap_length = m_to_idx(gap_length)
        platform_height = random.uniform(platform_height_min, platform_height_max)

        # Add platform
        add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)
        
        # Set goal on the platform
        goals[i + 1] = [cur_x + platform_length / 2, mid_y]

        # Update position for the next platform
        cur_x += platform_length + gap_length

    # Add final goal at the end of terrain
    final_gap = m_to_idx(0.5)
    goals[-1] = [cur_x + final_gap, mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals