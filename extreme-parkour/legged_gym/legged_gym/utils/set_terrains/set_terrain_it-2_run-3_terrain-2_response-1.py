import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Alternating steps and narrow bridges for the robot to navigate carefully and climb across a series of challenging obstacles."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define platform and step dimensions
    platform_length = 1.0 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.5)  
    platform_width = m_to_idx(platform_width)
    step_height_min, step_height_max = 0.1 * difficulty, 0.4 * difficulty
    gap_length = 0.1 + 0.4 * difficulty  
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(step_height_min, step_height_max)
        height_field[x1:x2, y1:y2] = platform_height
    
    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Initialize path with a series of steps and platforms
    cur_x = spawn_length
    step_width = 0.3 - 0.1 * difficulty  # narrower steps if more difficult
    step_width = m_to_idx(step_width)
    for i in range(6):  # Set up 6 alternating steps and platforms
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        if i % 2 == 0:  # Create step
            height = np.random.uniform(step_height_min, step_height_max)
            half_width = platform_width // 2
            x1, x2 = cur_x, cur_x + step_width
            y1, y2 = mid_y - half_width, mid_y + half_width
            height_field[x1:x2, y1:y2] = height
            cur_x += step_width
        else:  # Create platform
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
            cur_x += platform_length + dx

        # Put goal in the center of the step/platform
        goals[i+1] = [cur_x - step_width / 2, mid_y + dy]
        
        # Add gap if necessary
        if i != 5:
            cur_x += gap_length
    
    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals