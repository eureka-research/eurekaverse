import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Series of staircases and platforms for the quadruped to ascend and descend, testing climbing and descending skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    stair_height_step = 0.1 + 0.15 * difficulty
    stair_height_step = np.clip(stair_height_step, 0.1, 0.25)  # Clamp the height step to reasonable values
    stair_height_step = m_to_idx(stair_height_step)

    mid_y = m_to_idx(width) // 2
    stair_width = m_to_idx(1.0)
    platform_width = m_to_idx(1.0)
    platform_length = m_to_idx(1.0)
    
    def add_staircase(start_x, stair_length):
        """Adds a staircase to the height_field array."""
        for i in range(stair_length):
            height_field[start_x + i, mid_y - stair_width // 2 : mid_y + stair_width // 2] = i * stair_height_step

    def add_platform(start_x, end_x):
        """Adds a flat platform to the height_field array."""
        height_field[start_x:end_x, mid_y - platform_width // 2 : mid_y + platform_width // 2] = end_x * stair_height_step

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    
    # First goal near the robot start
    goals[0] = [spawn_length, mid_y]

    cur_x = spawn_length

    for i in range(4):
        staircase_length = m_to_idx(2.0)  # Each staircase spans 2 meters
        platform_end_x = cur_x + staircase_length + platform_length
        add_staircase(cur_x, staircase_length)
        add_platform(cur_x + staircase_length, platform_end_x)

        goals[i*2 + 1] = [cur_x + staircase_length // 2, mid_y]  # Mid stair goal
        goals[i*2 + 2] = [platform_end_x - platform_length // 2, mid_y]  # Mid platform goal

        # Prepare the next staircase start point
        cur_x = platform_end_x

    # Ensure that the last point is a goal point
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    return height_field, goals