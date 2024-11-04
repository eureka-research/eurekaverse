import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Varied-height platforms and wider gaps for the robot to climb and jump across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions
    base_height = 0.1
    height_increment = 0.1 * difficulty
    platform_length = 0.8  # Platform length in meters
    platform_length = m_to_idx(platform_length)
    platform_width = 0.6  # Platform width in meters
    platform_width = m_to_idx(platform_width)
    gap_length_min = 0.3
    gap_length_max = 0.6 * difficulty  # Increased gap length for higher difficulty
    gap_length_min = m_to_idx(gap_length_min)
    gap_length_max = m_to_idx(gap_length_max)
    
    mid_y = m_to_idx(width) // 2
    spawn_length = m_to_idx(2)

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    # Set spawn area to flat ground
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    current_x = spawn_length
    for i in range(4):  # Half the goals (4) will be placed on platforms
        platform_height = base_height + i * height_increment
        add_platform(current_x, current_x + platform_length, mid_y, platform_height)
        goals[i+1] = [current_x + platform_length // 2, mid_y]
        gap_length = np.random.randint(gap_length_min, gap_length_max)
        current_x += platform_length + gap_length

    for i in range(4, 7):  # The remaining goals will be on narrow bridges and ramps
        platform_height = base_height + (i - 3) * height_increment
        add_platform(current_x, current_x + platform_length, mid_y, platform_height)
        goals[i+1] = [current_x + platform_length // 2, mid_y]

        # Add narrow bridge
        bridge_length = platform_length
        bridge_mid_y = mid_y + m_to_idx((0.5 - difficulty) * 0.3) * ((-1) ** i)  # Zigzag pattern for bridges
        add_platform(current_x + platform_length, current_x + platform_length + bridge_length, bridge_mid_y, platform_height)
        goals[i+2] = [current_x + platform_length + bridge_length // 2, bridge_mid_y]

        gap_length = np.random.randint(gap_length_min, gap_length_max)
        current_x += platform_length + bridge_length + gap_length

    # Add final goal at the end
    goals[-1] = [current_x + m_to_idx(0.5), mid_y]
    height_field[current_x:, :] = 0

    return height_field, goals