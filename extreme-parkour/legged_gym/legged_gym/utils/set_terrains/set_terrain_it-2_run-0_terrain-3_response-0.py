import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Staggered platforms and inclined surfaces mimicking a naturally rough terrain for the robot to climb and navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions
    platform_length_min = 0.8  # Minimum platform length
    platform_length_max = 1.5  # Maximum platform length
    platform_width_min = 0.6  # Minimum platform width
    platform_width_max = 1.4  # Maximum platform width
    platform_height_min, platform_height_max = 0.0 + 0.2 * difficulty, 0.05 + 0.5 * difficulty

    gap_length = 0.4 + 0.5 * difficulty  # Increasing gap length for higher difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_staggered_platform(start_x, mid_y, height_range):
        platform_length = np.random.uniform(platform_length_min, platform_length_max)
        platform_width = np.random.uniform(platform_width_min, platform_width_max)
        platform_length = m_to_idx(platform_length)
        platform_width = m_to_idx(platform_width)
        
        half_width = platform_width // 2

        x1, x2 = start_x, start_x + platform_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(height_range[0], height_range[1])
        height_field[x1:x2, y1:y2] = platform_height

        return x1 + (x2 - x1) // 2, mid_y

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    height_range = (platform_height_min, platform_height_max)

    # Add first set of staggered platforms
    for i in range(3):
        cx, cy = add_staggered_platform(cur_x, mid_y + np.random.uniform(-0.3, 0.3), height_range)
        goals[i + 1] = [cx, cy]
        cur_x += m_to_idx(np.random.uniform(platform_length_min, platform_length_max)) + gap_length

    # Add an inclined ramp
    ramp_length = m_to_idx(2.0)
    ramp_height_max = 0.5 + 0.5 * difficulty  # Ramp height increases with difficulty
    half_ramp_width = m_to_idx(1.0) // 2
    ramp_height = np.linspace(0, ramp_height_max, ramp_length)
    height_field[cur_x:cur_x + ramp_length, mid_y - half_ramp_width:mid_y + half_ramp_width] = ramp_height[:, np.newaxis]
    cur_x += ramp_length + gap_length
    goals[4] = [cur_x - ramp_length // 2, mid_y]

    # Add another set of staggered platforms
    for i in range(3):
        cx, cy = add_staggered_platform(cur_x, mid_y + np.random.uniform(-0.3, 0.3), height_range)
        goals[i + 5] = [cx, cy]
        cur_x += m_to_idx(np.random.uniform(platform_length_min, platform_length_max)) + gap_length

    # Final goal behind the last platform
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals