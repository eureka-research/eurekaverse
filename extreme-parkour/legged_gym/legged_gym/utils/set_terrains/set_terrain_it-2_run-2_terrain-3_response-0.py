import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Alternating high steps and low platforms for the robot to jump across and climb."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set dimensions for high steps and low platforms
    high_step_height_min, high_step_height_max = 0.15 + 0.1 * difficulty, 0.25 + 0.2 * difficulty
    low_platform_height_min, low_platform_height_max = 0.0, 0.1 * difficulty
    step_length, platform_length = 0.8 + 0.2 * difficulty, 1.2 - 0.2 * difficulty
    step_length, platform_length = m_to_idx(step_length), m_to_idx(platform_length)
    gap_length = 0.2 + 0.2 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_step(start_x, height):
        x1, x2 = start_x, start_x + step_length
        y1, y2 = mid_y - m_to_idx(0.64), mid_y + m_to_idx(0.64)  # Width set to 1.28 meters
        height_field[x1:x2, y1:y2] = height

    def add_platform(start_x, height):
        x1, x2 = start_x, start_x + platform_length
        y1, y2 = mid_y - m_to_idx(1.0), mid_y + m_to_idx(1.0)  # Width set to 2 meters
        height_field[x1:x2, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0.0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    for i in range(3):  # Create 3 high steps
        high_step_height = np.random.uniform(high_step_height_min, high_step_height_max)
        low_platform_height = np.random.uniform(low_platform_height_min, low_platform_height_max)
        
        # Add alternating high step and low platform
        add_step(cur_x, high_step_height)
        goals[2 * i + 1] = [cur_x + step_length // 2, mid_y]
        cur_x += step_length + gap_length
        
        add_platform(cur_x, low_platform_height)
        goals[2 * i + 2] = [cur_x + platform_length // 2, mid_y]
        cur_x += platform_length + gap_length

    # Final low platform with goal
    add_platform(cur_x, low_platform_height_min)
    goals[7] = [cur_x + platform_length // 2, mid_y]

    return height_field, goals