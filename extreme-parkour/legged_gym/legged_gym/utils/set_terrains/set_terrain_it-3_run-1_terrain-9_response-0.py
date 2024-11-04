import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Stepped platforms and narrow bridges for the robot to climb and balance across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set platform and bridge dimensions
    platform_length = m_to_idx(1.0 - 0.3 * difficulty)
    platform_width = m_to_idx(np.random.uniform(0.5, 1.0))
    platform_height_min, platform_height_max = 0.1 * difficulty, 0.4 * difficulty
    gap_length = m_to_idx(0.3 + 0.5 * difficulty)
    bridge_width = m_to_idx(0.3 - 0.1 * difficulty)
    bridge_length = m_to_idx(1.5 + 0.5 * difficulty)
    
    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_bridge(start_x, end_x, mid_y):
        half_width = bridge_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = np.random.uniform(0.2, 0.4) * difficulty

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Set remaining area to pit-like terrain to ensure robot doesn't cheat by avoiding obstacles
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    for i in range(6):
        if i % 2 == 0:  # Add platforms
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)
            height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, height)
            goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
            cur_x += platform_length + dx + gap_length
        else: # Add bridges
            add_bridge(cur_x, cur_x + bridge_length, mid_y)
            goals[i+1] = [cur_x + bridge_length / 2, mid_y]
            cur_x += bridge_length + gap_length
    
    # Add final goal behind the last obstacle, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals