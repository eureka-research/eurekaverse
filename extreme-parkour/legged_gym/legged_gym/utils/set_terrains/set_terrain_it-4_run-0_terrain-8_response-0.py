import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Combination of steps, platforms, and side-inclines to test balance, climbing, and maneuvering skills."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and step dimensions
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.2)  # Slightly narrow platform widths
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 * difficulty + 0.1, 0.25 * difficulty + 0.15
    step_height = np.random.uniform(0.05, 0.15) * difficulty
    incline_height_min, incline_height_max = 0.2 * difficulty, 0.3 * difficulty
    gap_length = 0.2 + 0.6 * difficulty  # Gaps for more challenge
    gap_length = m_to_idx(gap_length)
    
    mid_y = m_to_idx(width) // 2
    
    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_steps(start_x, end_x, mid_y, number_of_steps, direction):
        single_step_length = (end_x - start_x) // number_of_steps
        step_height_diff = np.linspace(0, step_height * number_of_steps, num=number_of_steps)
        for step in range(number_of_steps):
            x1 = start_x + step * single_step_length
            x2 = x1 + single_step_length
            y1 = mid_y - (platform_width // 2)
            y2 = mid_y + (platform_width // 2)
            height_field[x1:x2, y1:y2] = step_height_diff[step] if direction == 'up' else step_height_diff[number_of_steps-step-1]

    def add_incline_slope(start_x, end_x, mid_y, direction, max_height):
        half_width = platform_width // 2
        slope_length = end_x - start_x
        incline = np.linspace(0, max_height, num=slope_length)[::direction]
        height_field[start_x:end_x, mid_y - half_width:mid_y + half_width] = np.broadcast_to(incline[:, None], (slope_length, platform_width))

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_shift = m_to_idx(0.2)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]
    
    cur_x = spawn_length
    features = [('platform', add_platform), ('steps', add_steps), ('incline', add_incline_slope)]
    np.random.shuffle(features)
    
    for i in range(6):
        dx = np.random.randint(dx_min, dx_max)
        dy = dy_shift if i % 2 == 0 else -dy_shift
        
        feature_type, feature_func = features[i % len(features)]
        
        if feature_type == 'platform':
            feature_func(cur_x, cur_x + platform_length + dx, mid_y + dy)
        elif feature_type == 'steps':
            feature_func(cur_x, cur_x + platform_length + dx, mid_y + dy, 4, 'up' if np.random.rand() > 0.5 else 'down')
        elif feature_type == 'incline':
            feature_func(cur_x, cur_x + platform_length + dx, mid_y + dy, 1 if np.random.rand() > 0.5 else -1, platform_height_max)

        goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        cur_x += platform_length + dx + gap_length

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals