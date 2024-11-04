import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Series of slanted ramps combined with stepping platforms and narrow passages for balance, climbing, and navigation."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up obstacle dimensions
    platform_length = 0.8 + 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.5, 1.0)
    platform_width = m_to_idx(platform_width)
    platform_height_range = [0.0 + 0.2 * difficulty, 0.05 + 0.4 * difficulty]
    ramp_height_range = [0.0 + 0.3 * difficulty, 0.1 + 0.5 * difficulty]
    narrow_passage_width = np.random.uniform(0.5, 0.7)
    narrow_passage_width = m_to_idx(narrow_passage_width)
    gap_length = 0.1 + 0.8 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2
    
    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(*platform_height_range)
        height_field[x1:x2, y1:y2] = platform_height

    def add_ramp(start_x, end_x, mid_y, direction):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(*ramp_height_range)
        slant = np.linspace(0, ramp_height, num=y2 - y1)[::direction]  # Slope direction
        slant = slant[None, :]  # Add a dimension for broadcasting to x
        height_field[x1:x2, y1:y2] = slant

    def add_narrow_passage(start_x, end_x, passage_y, height):
        half_width = narrow_passage_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = passage_y - half_width, passage_y + half_width
        height_field[x1:x2, y1:y2] = height
    
    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.0, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Set remaining area to be a pit
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    for i in range(6):
        if i % 2 == 0:  # Alternate between platforms and ramps
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        else:
            dx = np.random.randint(dx_min, dx_max)
            direction_bt1 = (-1) ** i  # Alternate direction
            dy = np.random.randint(dy_min, dy_max) * direction_bt1
            add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, direction_bt1)
            goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        cur_x += platform_length + dx + gap_length

    # Add final goal behind the last obstacle, filling in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals