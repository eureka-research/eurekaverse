import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Obstacle course with platforms, short ramps, and mild gaps for the robot to balance, climb, and jump across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and ramp dimensions
    platform_length = 1.0
    platform_length = m_to_idx(platform_length)
    platform_width = m_to_idx(np.random.uniform(0.9, 1.2))
    platform_height_min, platform_height_max = 0.0 + 0.1 * difficulty, 0.2 + 0.2 * difficulty
    gap_length = m_to_idx(0.1 + 0.1 * difficulty)

    ramp_length = platform_length // 2
    ramp_height_min, ramp_height_max = 0.2, 0.3 + 0.2 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_ramp(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_slope = np.linspace(0, height, num=end_x - start_x)
        height_field[x1:x2, y1:y2] = ramp_slope[:, np.newaxis]

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0.0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    for i in range(6):  # Creating a mix of platforms and ramps
        if i % 2 == 0:
            add_platform(cur_x, cur_x + platform_length, mid_y)
            goals[i + 1] = [cur_x + platform_length // 2, mid_y]
            cur_x += platform_length + gap_length

        else:
            ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
            add_ramp(cur_x, cur_x + ramp_length, mid_y, ramp_height)
            goals[i + 1] = [cur_x + ramp_length // 2, mid_y]
            cur_x += ramp_length + gap_length

    # Add final goal behind the last element and fill rest with flat terrain
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0.0

    return height_field, goals