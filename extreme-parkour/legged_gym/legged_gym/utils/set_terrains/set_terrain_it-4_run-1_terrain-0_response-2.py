import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Moving platforms and larger gaps for the robot to jump across and balance on."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions
    platform_length_min, platform_length_max = 0.8, 1.0
    platform_width_min, platform_width_max = 0.8, 1.2
    platform_height_min, platform_height_max = 0.2 + 0.3 * difficulty, 0.5 + 0.3 * difficulty
    gap_length_min, gap_length_max = 0.3 + 0.2 * difficulty, 1.0 + 0.3 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, length, mid_y):
        platform_width = np.random.uniform(platform_width_min, platform_width_max)
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        half_width = m_to_idx(platform_width) // 2
        x1, x2 = start_x, start_x + m_to_idx(length)
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = platform_height

    def add_moving_platform(start_x, length, mid_y, direction):
        platform_width = np.random.uniform(platform_width_min, platform_width_max)
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        half_width = m_to_idx(platform_width) // 2
        x1, x2 = start_x, start_x + m_to_idx(length)
        y1, y2 = mid_y - half_width, mid_y + half_width
        
        if direction > 0:
            slope = np.linspace(0, platform_height, x2 - x1)
        else:
            slope = np.linspace(platform_height, 0, x2 - x1)
        
        slope = slope[:, None]  # Add a dimension to broadcast
        height_field[x1:x2, y1:y2] = slope

    dx_min, dx_max = 0.0, 0.3
    dx_min, dx_max = m_to_idx([dx_min, dx_max])
    dy_min, dy_max = 0.0, 0.3
    dy_min, dy_max = m_to_idx([dy_min, dy_max])

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2.0)
    height_field[:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Initial platform
    cur_x = spawn_length
    add_platform(cur_x, platform_length_min, mid_y)
    goals[1] = [cur_x + m_to_idx(platform_length_min)/2, mid_y]
    cur_x += m_to_idx(platform_length_min)
    
    for i in range(2, 7):
        platform_length = np.random.uniform(platform_length_min, platform_length_max)
        gap_length = np.random.uniform(gap_length_min, gap_length_max)
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        if i % 2 == 0:
            add_platform(cur_x + dx, platform_length, mid_y + dy)
        else:
            direction = 1 if (i // 2) % 2 == 0 else -1
            add_moving_platform(cur_x + dx, platform_length, mid_y + dy, direction)
        
        goals[i] = [cur_x + m_to_idx(platform_length)/2 + dx, mid_y + dy]
        cur_x += m_to_idx(platform_length) + gap_length + dx

    # Add final goal beyond the last platform
    final_goal_x = cur_x + m_to_idx(platform_length_min)
    goals[7] = [final_goal_x, mid_y]
    height_field[cur_x:final_goal_x, :] = 0

    return height_field, goals