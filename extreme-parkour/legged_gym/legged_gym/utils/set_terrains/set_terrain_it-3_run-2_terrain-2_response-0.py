import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Complex course with staggered elevated platforms and sideways facing ramps to challenge balance, precision, and incline traversal."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions
    platform_length = 0.8 + 0.4 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.2 + 0.2 * difficulty)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.3 + 0.5 * difficulty
    gap_length = 0.2 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_ramp(start_x, end_x, mid_y, direction, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.linspace(0, height, x2 - x1)[::direction]
        ramp_height = ramp_height[:, None]  # Broadcasting for y-axis width
        height_field[x1:x2, y1:y2] = ramp_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Set remaining area to potential pits to enforce the robot to stay on platforms
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    for i in range(6):  # Set up platforms and ramps
        if i % 2 == 0:  # Platforms at even indices
            platform_height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)
            height = platform_height
        else:  # Ramps at odd indices
            ramp_height = np.random.uniform(platform_height_min, platform_height_max)
            direction = 1 if i % 4 == 1 else -1  # Just alternating the direction
            add_ramp(cur_x, cur_x + platform_length, mid_y, direction, ramp_height)
            height = ramp_height

        # Place goals in the middle of each platform or ramp
        goals[i+1] = [cur_x + platform_length / 2, mid_y]

        # Add gap
        cur_x += platform_length + gap_length

    # Add final goal behind the last platform/ramp, fill in remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals