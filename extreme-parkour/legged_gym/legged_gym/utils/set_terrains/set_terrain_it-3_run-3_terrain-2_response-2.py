import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Multiple elevated platforms and narrow bridges with variable heights and gaps to challenge the quadruped's agility, stability, and jumping abilities."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length_base = 1.0
    platform_length_variation = 0.2 * difficulty
    platform_length = m_to_idx(platform_length_base + platform_length_variation)

    platform_width_base = 1.0
    platform_width_variation = 0.2 * difficulty
    platform_width = m_to_idx(np.random.uniform(platform_width_base - platform_width_variation, platform_width_base + platform_width_variation))
    
    platform_height_min = 0.1 * difficulty
    platform_height_max = 0.4 * difficulty
    gap_length_base = 0.2
    gap_length_variation = 0.3 * difficulty
    gap_length = m_to_idx(gap_length_base + gap_length_variation)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_narrow_bridge(start_x, end_x, mid_y):
        narrow_width = m_to_idx(0.4 + 0.4 * difficulty)
        half_width = narrow_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        bridge_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = bridge_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_variation = m_to_idx(0.3)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Set remaining area to be a pit
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    for i in range(6):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(-dy_variation, dy_variation)

        # Alternate between platforms and narrow bridges
        if i % 2 == 0:
            platform_height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height)
            goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        else:
            add_narrow_bridge(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        cur_x += platform_length + dx + gap_length

    # Add final goal behind the last obstacle, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals