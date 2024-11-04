import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Advanced jumping and balancing challenge with varied heights and narrow paths."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Function to set up platform dimensions
    platform_length = 0.8 * (1.0 - 0.3 * difficulty)
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.6, 1.0)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.2 * difficulty, 0.5 * difficulty
    gap_length = 0.3 + 0.7 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, width, height, random_height=False):
        """Adds a platform to the height field."""
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        if random_height:
            height_field[x1:x2, y1:y2] = np.random.uniform(height[0], height[1])
        else:
            height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at spawn

    # Set remaining area to be a pit
    for i in range(spawn_length, m_to_idx(length)):
        height_field[i, :] = -1.0

    # Alternating between platforms and narrow beams to add more challenge
    cur_x = spawn_length
    for i in range(6):  # Combination of six different obstacles
        is_platform = (i % 2 == 0)
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        obstacle_width = np.random.uniform(0.4, platform_width) if not is_platform else platform_width
        obstacle_width = m_to_idx(obstacle_width)
        height = np.random.uniform(platform_height_min, platform_height_max)
        
        if is_platform:
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, obstacle_width, height, random_height=True)
            goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
            cur_x += platform_length + dx + gap_length
        else:
            add_platform(cur_x, cur_x + platform_length // 2 + dx, mid_y + dy, obstacle_width, height)
            goals[i + 1] = [cur_x + (platform_length // 2 + dx) / 2, mid_y + dy]
            cur_x += platform_length // 2 + dx + gap_length
    
    # Add final goal behind the last obstacle, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals