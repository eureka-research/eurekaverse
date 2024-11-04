import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """High platforms, varying height steps, and challenging ramps for the robot to climb, balance, and jump across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up obstacle dimensions
    platform_height = 0.3 + 0.5 * difficulty  # Increase max height
    platform_length = m_to_idx(1.0)
    platform_width = m_to_idx(np.random.uniform(0.8, 1.2))  # Narrower platforms
    step_height_min, step_height_max = 0.1 + 0.2 * difficulty, 0.15 + 0.25 * difficulty
    ramp_height = 0.5 + 0.7 * difficulty  # Higher ramps
    gap_length = m_to_idx(0.2 + 0.6 * difficulty)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_ramp(start_x, end_x, mid_y, height, direction):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slant = np.linspace(0, height, num=x2-x1)[::direction]
        slant = slant[:, None]  # Add a dimension for broadcasting to y
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -m_to_idx(0.1), m_to_idx(0.1)
    dy_min, dy_max = -m_to_idx(0.3), m_to_idx(0.3)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y] 

    # Initial pitch for difficult pit traversal
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length

    # Add high platforms and goals
    add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)
    cur_x += platform_length + gap_length
    goals[1] = [(cur_x - gap_length + cur_x) // 2, mid_y]

    # Add varying height steps and goals
    step_count = 3
    for i in range(1, step_count + 1):
        height = np.random.uniform(step_height_min, step_height_max)
        add_platform(cur_x, cur_x + platform_length, mid_y, height)
        goals[i + 1] = [cur_x + platform_length // 2, mid_y]
        cur_x += platform_length + gap_length

    # Add ramps and goals
    ramp_count = 2
    for i in range(step_count + 1, step_count + 1 + ramp_count):
        height = ramp_height
        direction = (-1) ** i  # Alternate ramps
        add_ramp(cur_x, cur_x + platform_length, mid_y, height, direction)
        goals[i + 1] = [cur_x + platform_length // 2, mid_y]
        cur_x += platform_length + gap_length

    # Add final platform and final goal
    add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)
    goals[7] = [cur_x + platform_length // 2, mid_y]
    height_field[cur_x + platform_length:, :] = 0

    goals[7] = [cur_x + m_to_idx(1.0), mid_y]
    
    return height_field, goals