import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Mixed obstacles with raised platforms, inclined slopes, and wider gaps to challenge the robot's climbing and balancing skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (is_instance(m, list) or is_instance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set platform dimensions based on difficulty
    platform_length = 1.2 - 0.4 * difficulty  # Varies with difficulty
    platform_width = np.random.uniform(1.0, 1.6)  # Random within range
    platform_height_min = 0.2 + 0.3 * difficulty  # Increase with difficulty
    platform_height_max = 0.5 + 0.4 * difficulty
    gap_length = 0.2 + 0.6 * difficulty  # Increase with difficulty
    slope_length = np.random.uniform(1.0, 2.0) - 0.5 * difficulty  # Length of slopes
    slope_angle = 10 + 20 * difficulty  # Increase angle with difficulty

    platform_length = m_to_idx(platform_length)
    platform_width = m_to_idx(platform_width)
    gap_length = m_to_idx(gap_length)
    slope_length = m_to_idx(slope_length)
    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, start_x + platform_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height
        return (x1 + x2) // 2, mid_y

    def add_slope(start_x, mid_y, upward=True):
        half_width = platform_width // 2
        x1, x2 = start_x, start_x + slope_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        slope_height = slope_length * np.tan(np.deg2rad(slope_angle))
        slope_height = slope_height if upward else -slope_height
        slope_range = np.linspace(0, slope_height, x2 - x1)
        for i in range(slope_range.size):
            height_field[x1 + i, y1:y2] = slope_range[i]
        return (x1 + x2) // 2, mid_y

    # Set spawn area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length // 2, mid_y]

    cur_x = spawn_length

    for i in range(6):
        if i % 2 == 0:
            # Alternate between platform and slope
            cx, cy = add_platform(cur_x, mid_y)
        else:
            direction = True if i % 4 == 1 else False  # Alternate slope direction
            cx, cy = add_slope(cur_x, mid_y, direction)
        
        cur_x = cx + gap_length
        goals[i + 1] = [cx, cy]

    # Final goal
    goals[-1] = [cur_x, mid_y]
    return height_field, goals
