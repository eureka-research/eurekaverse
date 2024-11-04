import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Combines varied-height platforms with narrow bridges to test balance and stepping accuracy."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Parameters for platforms and bridges
    platform_length = m_to_idx(0.8)
    bridge_length = m_to_idx(0.6) + m_to_idx(0.4 * difficulty)
    total_length = platform_length + bridge_length
    platform_width = m_to_idx(1.0)
    bridge_width = m_to_idx(0.4) - m_to_idx(0.2 * difficulty)
    platform_height_min, platform_height_max = 0.05 + 0.15 * difficulty, 0.1 + 0.25 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, length, width, height, mid_y):
        half_width = width // 2
        height_field[start_x:start_x+length, mid_y-half_width:mid_y+half_width] = height

    def add_bridge(start_x, length, width, mid_y):
        half_width = width // 2
        height_field[start_x:start_x+length, mid_y-half_width:mid_y+half_width] = 0.0

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Create varied height platforms with narrow bridges
    cur_x = spawn_length
    for i in range(7):
        platform_height = np.random.uniform(platform_height_min, platform_height_max)

        # Add platform
        add_platform(cur_x, platform_length, platform_width, platform_height, mid_y)
        goals[i+1] = [cur_x + platform_length // 2, mid_y]

        # Add connecting bridge
        cur_x += platform_length
        add_bridge(cur_x, bridge_length, bridge_width, mid_y)
        
        # Continue to the next platform
        cur_x += bridge_length

    # Fill the rest of the terrain to flat ground
    height_field[cur_x:, :] = 0
    goals[-1] = [m_to_idx(length) - m_to_idx(0.5), mid_y]

    return height_field, goals