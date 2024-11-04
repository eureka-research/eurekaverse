import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Successive climbing platforms and narrow paths with moderate height variability for balanced navigation."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform dimensions based on difficulty
    platform_length = 1.0 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.2)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.15 + 0.3 * difficulty
    narrow_path_width = 0.3 + 0.2 * difficulty
    narrow_path_width = m_to_idx(narrow_path_width)
    gap_length = 0.2 + 0.4 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height_variability=False):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        if height_variability:
            platform_height += np.random.normal(0, 0.02, size=x2-x1).cumsum() * difficulty
        height_field[x1:x2, y1:y2] = platform_height

    def add_narrow_path(start_x, end_x, mid_y):
        half_width = narrow_path_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        path_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = path_height

    # Initial flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(3):  # Three main platforms with gaps
        # Add platform
        dx = np.random.randint(-m_to_idx(0.1), m_to_idx(0.1))
        add_platform(cur_x, cur_x + platform_length + dx, mid_y, height_variability=True)
        
        # Add narrow path and set goal
        if i < 2:
            cur_x += platform_length + dx
            add_narrow_path(cur_x, cur_x + m_to_idx(0.8), mid_y)
            cur_x += gap_length
            goals[i+1] = [cur_x - gap_length // 2, mid_y]
        else:
            goals[i+1] = [cur_x + platform_length / 2, mid_y]
        cur_x += platform_length + dx + gap_length
    
    # Final safe platform and goal
    add_platform(cur_x, cur_x + m_to_idx(1.0), mid_y)
    goals[7] = [cur_x + m_to_idx(0.5), mid_y]
    
    height_field[cur_x:, :] = 0

    return height_field, goals