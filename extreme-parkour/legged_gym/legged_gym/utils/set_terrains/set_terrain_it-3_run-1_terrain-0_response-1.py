import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Combination of varying height platforms and narrow bridges with gaps, to test the quadruped's balance and agility."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length = 1.0 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    gap_length = 0.3 + 0.8 * difficulty
    gap_length = m_to_idx(gap_length)
    platform_width_variation_factor = 0.4 + 0.6 * difficulty
    platform_width = np.random.uniform(0.5, 1.0)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.05 + 0.2 * difficulty, 0.15 + 0.4 * difficulty

    bridge_width_min, bridge_width_max = 0.2, 0.4 + 0.4 * difficulty
    bridge_width_min, bridge_width_max = m_to_idx(bridge_width_min), m_to_idx(bridge_width_max)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, width, height):
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = -0.1, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Initialize the starting platform
    cur_x = spawn_length
    for i in range(6):  # Create 6 platforms/bridges with gaps in between
        if i % 2 == 0:
            # Platforms of varying heights and width
            platform_width = np.random.uniform(platform_width_variation_factor, platform_width * 1.2)
            platform_width = m_to_idx(platform_width)
            platform_height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, cur_x + platform_length, mid_y, platform_width, platform_height)
            goals[i+1] = [cur_x + platform_length // 2, mid_y]
            cur_x += platform_length + gap_length
        else:
            # Narrow bridges of varying width
            bridge_width = np.random.uniform(bridge_width_min, bridge_width_max)
            add_platform(cur_x, cur_x + platform_length, mid_y, bridge_width, platform_height)
            goals[i+1] = [cur_x + platform_length // 2, mid_y]
            cur_x += platform_length + gap_length

    # Add final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals