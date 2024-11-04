import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Series of stepped platforms, hills, and valleys to test the quadruped's ability to navigate uneven terrain."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length = 1.0
    platform_length = m_to_idx(platform_length)
    platform_width = 1.5
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.3 * difficulty, 0.1 + 0.4 * difficulty

    hill_length = 1.0
    hill_length = m_to_idx(hill_length)
    hill_height = 0.1 + 0.4 * difficulty
    hill_height = m_to_idx(hill_height)

    valley_length = 1.0
    valley_length = m_to_idx(valley_length)
    valley_depth = -0.1 - 0.4 * difficulty
    valley_depth = m_to_idx(valley_depth)

    spawn_zone = m_to_idx(2)
    mid_y = m_to_idx(width // 2)

    # Set spawn area to flat ground
    height_field[0:spawn_zone, :] = 0
    goals[0] = [spawn_zone - m_to_idx(0.5), mid_y]

    def create_platform(start_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, start_x + platform_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def create_hill(start_x, mid_y, height):
        x1, x2 = start_x, start_x + hill_length
        half_width = platform_width // 2
        for x in range(x1, x2):
            current_height = height * (x - x1) / (x2 - x1)
            y1, y2 = mid_y - half_width, mid_y + half_width
            height_field[x, y1:y2] = current_height

    def create_valley(start_x, mid_y, depth):
        x1, x2 = start_x, start_x + valley_length
        half_width = platform_width // 2
        for x in range(x1, x2):
            current_depth = depth * (x - x1) / (x2 - x1)
            y1, y2 = mid_y - half_width, mid_y + half_width
            height_field[x, y1:y2] = current_depth
    
    cur_x = spawn_zone
    for i in range(7):
        if i % 2 == 0:  # Place platforms
            platform_height = np.random.uniform(platform_height_min, platform_height_max)
            create_platform(cur_x, mid_y, platform_height)
            cur_x += platform_length
        elif i % 2 == 1:  # Place hills and valleys
            if random.choice([True, False]):
                create_hill(cur_x, mid_y, hill_height)
                cur_x += hill_length
            else:
                create_valley(cur_x, mid_y, valley_depth)
                cur_x += valley_length
        
        goals[i + 1] = [cur_x - m_to_idx(0.5), mid_y]

    return height_field, goals