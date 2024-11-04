import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Platforms of varied heights connected by narrow bridges, with gaps for jumping."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform dimensions
    platform_length = 1.0 - 0.3 * difficulty 
    platform_length = m_to_idx(platform_length)
    platform_width = 1.0
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1, 0.4 * difficulty

    # Bridge dimensions
    bridge_length = 1.2 - 0.2 * difficulty 
    bridge_length = m_to_idx(bridge_length)
    bridge_width = 0.4
    bridge_width = m_to_idx(bridge_width)
    bridge_height = -0.1  # Bridges may have some small descent/upward angle

    # Gap dimensions
    gap_length = 0.2 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_bridge(start_x, end_x, mid_y, height):
        half_width = bridge_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slant = np.linspace(height, height + bridge_height, x2 - x1)
        height_field[x1:x2, y1:y2] = slant[:, None]

    cur_x = m_to_idx(2)  # Ensure clearing the spawn area
    height_field[0:cur_x, :] = 0

    # First goal at spawn area
    goals[0] = [m_to_idx(1), mid_y]

    for i in range(4):
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)
        goals[i + 1] = [cur_x + platform_length // 2, mid_y]
        cur_x += platform_length + gap_length

        bridge_height = np.random.uniform(-0.2, 0.2)
        add_bridge(cur_x, cur_x + bridge_length, mid_y, bridge_height)
        goals[i + 1] = [cur_x + bridge_length // 2, mid_y]
        cur_x += bridge_length + gap_length

    # Final set of platforms and goal
    final_platform_height = np.random.uniform(platform_height_min, platform_height_max)
    add_platform(cur_x, cur_x + platform_length, mid_y, final_platform_height)
    goals[6] = [cur_x + platform_length // 2, mid_y]
    cur_x += platform_length + gap_length

    # Last goal after traversing platforms and bridges
    goals[7] = [cur_x + m_to_idx(1), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals