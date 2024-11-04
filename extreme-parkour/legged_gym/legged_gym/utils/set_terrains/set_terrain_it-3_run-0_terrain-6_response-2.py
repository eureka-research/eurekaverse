import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Combination of ramps, narrow passages, and platforms for the robot to navigate, climb, and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Parameters for different obstacles
    platform_width = np.random.uniform(1.0, 1.2)
    platform_width = m_to_idx(platform_width)
    platform_length = 1.0 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_height_min, platform_height_max = 0.1 + 0.1 * difficulty, 0.4 + 0.5 * difficulty
    ramp_height_min, ramp_height_max = 0.1 * difficulty, 0.5 * difficulty
    gap_length = 0.2 + 0.8 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_ramp(start_x, end_x, mid_y, direction, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slant = np.linspace(0, height, num=x2 - x1)[::direction]
        slant = slant[:, None]  # Add a dimension for broadcasting to y-axis
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.0, 0.4  # Polarity of dy will alternate
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Alternate between ramps and platforms
    cur_x = spawn_length
    for i in range(6):  # Set up 6 obstacles
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max) * (-1) ** i
        obstacle_length = platform_length + dx
        height = np.random.uniform(platform_height_min, platform_height_max) if i % 2 == 1 else np.random.uniform(ramp_height_min, ramp_height_max)
        
        if i % 2 == 0:
            # Add ramp
            add_ramp(cur_x, cur_x + obstacle_length, mid_y + dy, (-1) ** i, height)
        else:
            # Add platform
            add_platform(cur_x, cur_x + obstacle_length, mid_y + dy, height)

        goals[i+1] = [cur_x + obstacle_length / 2, mid_y + dy]

        cur_x += obstacle_length + gap_length

    # Add final goal behind the last obstacle, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals