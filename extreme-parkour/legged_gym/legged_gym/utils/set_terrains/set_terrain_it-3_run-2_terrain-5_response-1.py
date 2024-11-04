import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Zigzag raised platforms with varying heights for the robot to navigate and climb."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Dimensions for platforms
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.6)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.2 * difficulty, 0.1 + 0.3 * difficulty
    gap_length = 0.1 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    def add_platform(start_x, end_x, start_y, end_y):
        height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[start_x:end_x, start_y:end_y] = height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    mid_y = m_to_idx(width) // 2

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Setup platforms in a zigzag pattern
    cur_x = spawn_length
    for i in range(6):  # Set up 6 platforms
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        y_offset = (i % 2) * m_to_idx(3) - m_to_idx(1.5)  # Alternate between offsets on the y-axis
        start_y = mid_y + y_offset
        end_y = start_y + platform_width
        
        add_platform(cur_x, cur_x + platform_length + dx, start_y, end_y)

        # Put goal in the center of the platform
        goals[i + 1] = [cur_x + (platform_length + dx) // 2, (start_y + end_y) // 2]

        cur_x += platform_length + dx + gap_length

    # Add final goal behind the last platform and set a flat terrain
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals