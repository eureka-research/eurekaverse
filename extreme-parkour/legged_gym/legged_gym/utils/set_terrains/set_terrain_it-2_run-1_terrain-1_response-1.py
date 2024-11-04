import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Elevated platforms with tilt and varying heights requiring precision and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform parameters
    base_length = 1.0
    base_width = 0.9
    base_height = 0.3
    
    platform_length = base_length - 0.4 * difficulty
    platform_width = base_width - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = m_to_idx(platform_width)
    height_min = base_height + 0.2 * difficulty
    height_max = base_height + 0.4 * difficulty

    gap_min = 0.2
    gap_max = 0.7
    gap_length = gap_min + (gap_max - gap_min) * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width / 2)

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_tilted_platform(start_x, end_x, mid_y, height, tilt):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slant = np.linspace(0, tilt, num=(y2-y1))[None, :]
        height_field[x1:x2, y1:y2] = height + slant

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # First goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Set remaining area to pit
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length

    for i in range(6):  # Set up 6 platforms
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        platform_height = np.random.uniform(height_min, height_max)
        if i % 2 == 0:
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height)
        else:
            tilt = np.random.uniform(0.05, 0.15) * difficulty
            add_tilted_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height, tilt)

        # Goal in center of each platform
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += platform_length + dx + gap_length

    # Final goal behind last obstacle
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals