import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Alternating side-to-side platforms with gaps for the quadruped to navigate by balancing and jumping."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions
    platform_length = 1.0 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 0.8  # Fixed platform width to ensure fairness
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.2 + 0.3 * difficulty
    gap_length = 0.2 + 0.4 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, mid_y, width, height):
        half_width = width // 2
        x1, x2 = start_x, start_x + platform_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dx_offset = np.random.randint(dx_min, dx_max)

    def add_gap_platforms(init_x, mid_y, num_goals_left):
        cur_x = init_x
        direction = 1
        goal_counter = 1

        while goal_counter <= num_goals_left:
            dx = np.random.randint(dx_min, dx_max) + direction * dx_offset
            platform_height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, mid_y, platform_width, platform_height)

            # Place goal in the center of the platform
            goals[goal_counter] = [cur_x + platform_length // 2, mid_y]
            cur_x += platform_length + gap_length
            goal_counter += 1

            # Alternate side steps
            direction *= -1

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Add a series of alternating platforms
    add_gap_platforms(spawn_length, mid_y, 7)

    # Add final goal behind the last platform
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals