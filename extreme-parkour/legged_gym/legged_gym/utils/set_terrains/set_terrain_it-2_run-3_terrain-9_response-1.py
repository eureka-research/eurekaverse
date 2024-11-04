import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Mixed obstacle course with ramps, platforms, and staggered steps for varied training."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Ramp and platform parameters based on difficulty
    ramp_length = 1.0  # meters
    platform_width_min = 1.0 - 0.5 * difficulty  # meters
    platform_width_max = 1.5 - 0.5 * difficulty  # meters
    platform_height_min = 0.1 * difficulty  # meters
    platform_height_max = 0.5 * difficulty  # meters
    gap_length_min = 0.2  # meters, minimum gap
    gap_length_max = 0.7 * difficulty  # meters, maximum gap

    mid_y = m_to_idx(width) // 2

    def create_ramp(start_x, end_x, start_height, end_height, mid_y):
        """Creates a ramp between start_x and end_x with given start and end heights."""
        ramp_slope = (end_height - start_height) / (end_x - start_x)
        ramp_width = m_to_idx(platform_width_min)
        half_width = ramp_width // 2
        for x in range(start_x, end_x):
            for y in range(mid_y - half_width, mid_y + half_width):
                height_field[x, y] = start_height + ramp_slope * (x - start_x)

    def create_platform(start_x, end_x, height, mid_y):
        """Creates a platform between start_x and end_x at a given height."""
        platform_width = np.random.uniform(platform_width_min, platform_width_max)
        half_width = m_to_idx(platform_width) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def create_staggered_steps(start_x, mid_y, num_steps=3):
        """Creates staggered steps for the quadruped to navigate."""
        step_length = m_to_idx(0.3)
        step_height = m_to_idx(0.1)
        half_width = m_to_idx(0.5) // 2  # Narrow steps
        for i in range(num_steps):
            step_x = start_x + i * step_length
            step_y = mid_y + (-1) ** i * half_width  # Alternate left and right steps
            for x in range(step_x, step_x + step_length):
                for y in range(step_y - half_width, step_y + half_width):
                    height_field[x, y] = i * step_height

    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]
    cur_x = spawn_length

    for i in range(1, 8):
        obstacle_choice = random.choice(['ramp', 'platform', 'steps'])
        start_height = random.uniform(platform_height_min, platform_height_max)
        end_height = random.uniform(platform_height_min, platform_height_max)
        length = m_to_idx(random.uniform(0.8, 1.2))
        
        if obstacle_choice == 'ramp':
            create_ramp(cur_x, cur_x + length, start_height, end_height, mid_y)
        elif obstacle_choice == 'platform':
            create_platform(cur_x, cur_x + length, start_height, mid_y)
        elif obstacle_choice == 'steps':
            create_staggered_steps(cur_x, mid_y)

        goals[i] = [cur_x + length // 2, mid_y]
        cur_x += length + m_to_idx(random.uniform(gap_length_min, gap_length_max))

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals