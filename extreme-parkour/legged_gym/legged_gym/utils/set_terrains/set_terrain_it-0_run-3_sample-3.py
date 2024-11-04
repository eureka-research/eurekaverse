import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Series of stepping stone platforms of varying heights for the robot to jump across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    def add_platform(start_x, start_y, platform_width, platform_length, platform_height):
        end_x = start_x + m_to_idx(platform_length)
        end_y = start_y + m_to_idx(platform_width)
        height_field[start_x:end_x, start_y:end_y] = platform_height

    # Convert sizes to indices
    course_length = m_to_idx(length)
    course_width = m_to_idx(width)
    quadruped_length = m_to_idx(0.645)
    quadruped_width = m_to_idx(0.28)

    # Initial spawn area
    height_field[0:m_to_idx(2), :] = 0
    goals[0] = [m_to_idx(1), course_width // 2]

    # Initial platform properties
    platform_length = 0.8 - 0.2 * difficulty
    platform_width = 0.5
    platform_height_min = 0.2 * difficulty
    platform_height_max = platform_height_min + 0.1
    num_platforms = 7

    cur_x = m_to_idx(2)
    platform_gap = 0.2
    platform_gap_idx = m_to_idx(platform_gap)

    for i in range(num_platforms):
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        platform_y = np.random.randint(quadruped_width, course_width - quadruped_width)
        
        add_platform(cur_x, platform_y, platform_width, platform_length, platform_height)
        
        # Set goal position on platform
        goals[i+1] = [cur_x + m_to_idx(platform_length) // 2, platform_y + m_to_idx(platform_width) // 2]

        # Prepare for next platform
        cur_x += m_to_idx(platform_length) + platform_gap_idx
        platform_height_min += 0.05
        platform_height_max += 0.05
        
        # Adjust heights for increasing difficulty
        if i < num_platforms - 1:
            height_field[cur_x:cur_x + platform_gap_idx, :] = 0

    # Final goal
    goals[-1] = [min(cur_x + m_to_idx(platform_length) // 2, course_length - 1), course_width // 2]

    return height_field, goals