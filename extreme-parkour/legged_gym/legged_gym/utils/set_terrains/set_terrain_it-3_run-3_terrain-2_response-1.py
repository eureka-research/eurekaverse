import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Checkerboard pattern platforms with varied slants and narrow passageways for refined navigation and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions and properties
    platform_size_base = 0.8
    platform_size_variation = 0.2 * difficulty
    platform_height_base = 0.1 * difficulty
    platform_height_variation = 0.3 * difficulty
    gap_length_base = 0.2
    gap_length_variation = 0.4 * difficulty

    platform_size = m_to_idx(platform_size_base)
    gap_length = m_to_idx(gap_length_base + gap_length_variation)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, start_y, size, height):
        x1, x2 = start_x, start_x + size
        y1, y2 = start_y, start_y + size
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = -0.2, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Set remaining area to be a pit
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    for i in range(6):  # Set up 6 checkerboard platforms
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        platform_height = platform_height_base + np.random.uniform(0, platform_height_variation)
        
        # Checkerboard in X and Y direction
        add_platform(cur_x, mid_y + dy, platform_size, platform_height)
        add_platform(cur_x, mid_y - dy - platform_size, platform_size, platform_height)
        add_platform(cur_x + platform_size + gap_length, mid_y + dy, platform_size, platform_height)
        add_platform(cur_x + platform_size + gap_length, mid_y - dy - platform_size, platform_size, platform_height)

        # Put goals alternately on two different rows of the checkerboard
        if i % 2 == 0:
            goals[i+1] = [cur_x + platform_size / 2, mid_y + dy + platform_size / 2]
        else:
            goals[i+1] = [cur_x + platform_size / 2, mid_y - dy - platform_size / 2]
        
        # Adjust current x position considering gaps and platform size
        cur_x += 2 * (platform_size + gap_length)

    # Add final goal behind the last platform
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals