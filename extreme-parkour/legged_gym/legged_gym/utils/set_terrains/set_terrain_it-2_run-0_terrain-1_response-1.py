import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Alternating high and low platforms traversing a pit, testing the robot's ability to adapt to varying vertical heights."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform settings
    platform_length = 0.8 - 0.2 * difficulty  # meters, dependent on difficulty
    platform_width = 0.9 + 0.4 * random.random()  # between 0.9 and 1.3 meters
    platform_height_low = 0.1 + 0.15 * difficulty  # meters
    platform_height_high = 0.3 + 0.25 * difficulty  # meters
    gap_length = 0.2 + 0.6 * difficulty  # meters

    # Convert to quantized indices
    platform_length_idx = m_to_idx(platform_length)
    platform_width_idx = m_to_idx(platform_width)
    platform_height_low_idx = platform_height_low / field_resolution
    platform_height_high_idx = platform_height_high / field_resolution
    gap_length_idx = m_to_idx(gap_length)

    mid_y = m_to_idx(width / 2)

    def add_platform(start_x, end_x, y_center, height):
        half_width = platform_width_idx // 2
        x1, x2 = start_x, end_x
        y1, y2 = y_center - half_width, y_center + half_width
        height_field[x1:x2, y1:y2] = height

    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0  # Flat ground for spawn area
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal in the middle of spawn area

    # Create a pit
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    for i in range(6):
        platform_height = platform_height_high_idx if i % 2 == 0 else platform_height_low_idx
        add_platform(cur_x, cur_x + platform_length_idx, mid_y, platform_height)
        goals[i+1] = [cur_x + platform_length_idx / 2, mid_y]
        cur_x += platform_length_idx + gap_length_idx    
    
    # Final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals