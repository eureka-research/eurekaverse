import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Complex elevated and uneven terrain for enhanced difficulty, testing the robot's balance and climbing abilities."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define the size parameters based on difficulty
    min_platform_width = 0.6 + 0.1 * difficulty
    max_platform_width = 1.2 - 0.1 * difficulty
    min_height = 0.1 * difficulty
    max_height = 0.5 * difficulty
    min_gap = 0.2
    max_gap = 0.8 + 0.2 * difficulty

    mid_y = m_to_idx(width / 2)

    def add_platform_or_slope(start_x, end_x, mid_y, platform_width, height, incline=False):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        if incline:
            slope = np.linspace(0, height, num=x2-x1)[:, None]
            height_field[x1:x2, y1:y2] = np.broadcast_to(slope, (x2-x1, y2-y1))
        else:
            height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    for i in range(6):  # Set up 6 obstacles
        platform_width = np.random.uniform(min_platform_width, max_platform_width)
        platform_width = m_to_idx(platform_width)
        platform_length = 1.0 + 0.4 * difficulty
        platform_length = m_to_idx(platform_length)
        platform_height = np.random.uniform(min_height, max_height)

        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        # Randomly decide if the obstacle is an inclined ramp or flat platform
        incline = np.random.rand() > 0.5

        add_platform_or_slope(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_width, platform_height, incline)

        # Place a goal at each obstacle
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Create a gap between platforms
        gap_length = np.random.uniform(min_gap, max_gap) * difficulty + 0.2
        gap_length = m_to_idx(gap_length)

        cur_x += platform_length + dx + gap_length

    # Add final goal behind the last platform, filling in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals