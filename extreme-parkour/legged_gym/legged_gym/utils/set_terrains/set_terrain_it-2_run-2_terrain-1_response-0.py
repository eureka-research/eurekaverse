import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Alternating slopes and platforms with varying heights and gaps for the robot to navigate and jump across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up obstacle dimensions
    platform_length = 1.0 - 0.3 * difficulty  # Longer platform for more jumps
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.2)  # Moderate width for tighter jumps
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.2 * difficulty, 0.5 * difficulty  # Taller platforms
    slope_height_min, slope_height_max = 0.2 * difficulty, 0.6 * difficulty
    gap_length = 0.3 + 1.0 * difficulty  # Larger gaps
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_slope(start_x, end_x, mid_y, height, direction):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slope = np.linspace(0, height, num=x2-x1)[::direction]
        slope = slope[:, None]  # Add a dimension for broadcasting to y
        height_field[x1:x2, y1:y2] = slope

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Set remaining area to be a pit
    height_field[spawn_length:, :] = -0.5  # Making the pit shallower than before for safety

    cur_x = spawn_length

    num_obstacles = 7  # Increase the number of obstacles
    for i in range(num_obstacles):
        if i % 2 == 0:
            # Add platform
            platform_height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)
            goals[i + 1] = [cur_x + platform_length / 2, mid_y]
            cur_x += platform_length + gap_length
        else:
            # Add slope
            slope_height = np.random.uniform(slope_height_min, slope_height_max)
            direction = 1 if np.random.rand() > 0.5 else -1  # Randomize slope direction
            add_slope(cur_x, cur_x + platform_length, mid_y, slope_height, direction)
            goals[i + 1] = [cur_x + platform_length / 2, mid_y]
            cur_x += platform_length + gap_length

    # Add final goal behind the last obstacle, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals