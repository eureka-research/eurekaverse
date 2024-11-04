import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Combines platforms, steps, and inclined/sloped ramps for an increased navigation challenge."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and ramp dimensions
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.4, 1.0)  # Narrower width for increased difficulty
    platform_width = m_to_idx(platform_width)
    
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.2 + 0.3 * difficulty
    ramp_height_min, ramp_height_max = 0.1 + 0.5 * difficulty, 0.2 + 0.6 * difficulty
    step_height_min, step_height_max = 0.1 + 0.3 * difficulty, 0.15 + 0.35 * difficulty
    gap_length = 0.3 + 0.5 * difficulty  # Increase the gap length slightly
    gap_length = m_to_idx(gap_length)
    
    mid_y = m_to_idx(width) // 2  # Centralize along y-axis
    
    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_ramp(start_x, end_x, mid_y, direction):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        slant = np.linspace(0, ramp_height, num=x2-x1)[:, None]
        if direction < 0:
            slant = np.flip(slant)
        height_field[x1:x2, y1:y2] = slant

    def add_steps(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        step_height = np.random.uniform(step_height_min, step_height_max)
        height_field[x1:x1 + m_to_idx(0.2), y1:y2] = step_height  # first step
        height_field[x1 + m_to_idx(0.2):x1 + m_to_idx(0.4), y1:y2] = step_height * 2  # second step
        height_field[x1 + m_to_idx(0.4):x2, y1:y2] = step_height * 3  # third step

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at spawn

    cur_x = spawn_length
    for i in range(6):
        obstacle_type = i % 3
        
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        if obstacle_type == 0:  # Add regular platform
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        
        elif obstacle_type == 1:  # Add sloped ramp
            direction = (-1) ** (i // 2)  # Alternate direction
            add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, direction)
            goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        else:  # Add steps
            add_steps(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        cur_x += platform_length + dx + gap_length

    # Final goal behind the last obstacle, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals