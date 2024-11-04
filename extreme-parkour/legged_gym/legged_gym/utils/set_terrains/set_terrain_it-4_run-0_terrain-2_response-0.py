import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Staggered elevated platforms and gaps testing balance, precision, and jumping abilities."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions
    platform_length = m_to_idx(1.0 - 0.3 * difficulty)
    platform_width = m_to_idx(np.random.uniform(0.6, 1.2))
    platform_height_min = 0.0 + 0.15 * difficulty
    platform_height_max = 0.2 + 0.25 * difficulty
    gap_length = m_to_idx(0.2 + 0.5 * difficulty)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, mid_y, height):
        half_width = platform_width // 2
        end_x = start_x + platform_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[start_x:end_x, y1:y2] = height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Create staggered elevated platforms
    cur_x = spawn_length
    for i in range(6):  # Set up 6 platforms
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        add_platform(cur_x, mid_y + dy, platform_height)

        # Place goal in the center of each platform
        goals[i+1] = [cur_x + platform_length / 2 + dx, mid_y + dy]

        # Add gap
        cur_x += platform_length + gap_length + dx

    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    return height_field, goals