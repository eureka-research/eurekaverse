import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Series of slopes and alternating narrow platforms, testing the robot's ability to traverse changing elevations and gaps."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.0)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.15 * difficulty, 0.3 * difficulty
    slope_height_min, slope_height_max = 0.1, 0.5 * difficulty
    gap_length = 0.1 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)
    mid_y = m_to_idx(width) // 2

    def create_slope(start_x, end_x, mid_y, slope_height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = np.linspace(0, slope_height, x2 - x1).reshape(-1, 1)

    def create_narrow_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 4
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    # Create Slopes and Platforms
    for i in range(7):
        slope_height = np.random.uniform(slope_height_min, slope_height_max)
        create_slope(cur_x, cur_x + platform_length, mid_y, slope_height)
        cur_x += platform_length
        goals[i + 1] = [cur_x - m_to_idx(0.5), mid_y]
        
        if i % 2 == 0:  # Every other goal introduces a narrow platform
            height = np.random.uniform(platform_height_min, platform_height_max)
            create_narrow_platform(cur_x, cur_x + platform_length, mid_y, height)
            cur_x += platform_length + gap_length

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals