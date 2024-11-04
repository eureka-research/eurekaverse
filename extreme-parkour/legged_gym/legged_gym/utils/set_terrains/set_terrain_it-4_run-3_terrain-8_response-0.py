import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Mixed terrain with stepping stones, gaps, and varying height platforms for the quadruped to navigate."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Terrain and obstacle parameters
    step_length = 0.4
    step_length_idx = m_to_idx(step_length)
    step_width = 0.4 + 0.2 * difficulty
    step_width_idx = m_to_idx(step_width)
    step_height_min, step_height_max = 0.1, 0.25 + 0.2 * difficulty
    gap_length = 0.2 + 0.5 * difficulty
    gap_length_idx = m_to_idx(gap_length)

    platform_length = 0.8 - 0.2 * difficulty
    platform_length_idx = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.2)
    platform_width_idx = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.05 + 0.2 * difficulty, 0.1 + 0.3 * difficulty
    
    mid_y = m_to_idx(width) // 2

    def add_step(start_x, mid_y):
        half_width = step_width_idx // 2
        x1 = start_x
        x2 = start_x + step_length_idx
        y1 = mid_y - half_width
        y2 = mid_y + half_width
        step_height = np.random.uniform(step_height_min, step_height_max)
        height_field[x1:x2, y1:y2] = step_height

    def add_gap(start_x, mid_y):
        half_width = step_width_idx // 2
        x1 = start_x
        x2 = start_x + gap_length_idx
        y1 = mid_y - half_width
        y2 = mid_y + half_width
        height_field[x1:x2, y1:y2] = -0.2
    
    def add_platform(start_x, mid_y):
        half_width = platform_width_idx // 2
        x1 = start_x
        x2 = start_x + platform_length_idx
        y1 = mid_y - half_width
        y2 = mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]
    
    cur_x = spawn_length

    # Add a series of steps, gaps, and platforms
    for i in range(3):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_step(cur_x, mid_y + dy)
        goals[i + 1] = [cur_x + step_length_idx // 2, mid_y + dy]
        cur_x += step_length_idx + dx + gap_length_idx
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_gap(cur_x, mid_y + dy)
        cur_x += gap_length_idx + dx
    
    for i in range(3):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, mid_y + dy)
        goals[4 + i] = [cur_x + platform_length_idx // 2, mid_y + dy]
        cur_x += platform_length_idx + dx + gap_length_idx

    # Add final goal behind the last platform
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals