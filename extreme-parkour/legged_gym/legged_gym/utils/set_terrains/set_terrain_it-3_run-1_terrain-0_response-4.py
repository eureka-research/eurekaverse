import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Platform and narrow path with gaps and slight turns for the robot to balance, jump, and navigate through."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # General parameters
    platform_length = 0.8 - 0.2 * difficulty  # Shorter platforms
    platform_length = m_to_idx(platform_length)
    platform_width = 0.6 + 0.4 * difficulty  # Narrower platforms
    platform_width = m_to_idx(platform_width)
    platform_height = np.linspace(0.1 + 0.2 * difficulty, 0.4 * difficulty, num=8)  # Wider height range for higher difficulty
    gap_length = m_to_idx(0.2 + 0.5 * difficulty)  # Wider gaps

    # Initial settings
    spawn_length = m_to_idx(2)
    mid_y = m_to_idx(width / 2)
    cur_x = spawn_length
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    height_field[:spawn_length, :] = 0

    def add_platform(start_x, platform_length, platform_width, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, start_x + platform_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    for i in range(7):
        # Platforms with gaps
        plat_height = platform_height[i % len(platform_height)]
        dy_max = min(platform_width // 2, m_to_idx(width) - (platform_width // 2))
        dy = random.randint(-dy_max, dy_max)
        cur_y = mid_y + dy
        
        add_platform(cur_x, platform_length, platform_width, cur_y, plat_height)
        goals[i + 1] = [cur_x + platform_length // 2, cur_y]

        cur_x += platform_length + gap_length

    # Final goal after last platform
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    height_field[cur_x:, :] = 0

    return height_field, goals