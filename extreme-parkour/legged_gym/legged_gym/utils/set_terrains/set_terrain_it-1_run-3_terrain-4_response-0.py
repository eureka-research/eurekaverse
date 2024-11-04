import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Alternating steps and raised platforms for the quadruped to navigate and climb."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform and step dimensions
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.5)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1, 0.3
    step_height_min, step_height_max = 0.1 + 0.4 * difficulty, 0.2 + 0.6 * difficulty
    gap_length = 0.2 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width / 2)

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_step(start_x, end_x, mid_y, step_height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = step_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # First goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Set remaining area to a pit
    height_field[spawn_length:, :] = -0.5

    cur_x = spawn_length
    for i in range(3):  # Set up 3 alternating platforms and steps
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        # Add platform
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
        
        # Place a goal on each platform
        goals[i * 2 + 1] = [cur_x + (platform_length + dx) // 2, mid_y + dy]

        # Add gap
        cur_x += platform_length + dx + gap_length
        
        # Add step
        step_height = np.random.uniform(step_height_min, step_height_max)
        add_step(cur_x, cur_x + platform_length + dx, mid_y + dy, step_height)
        
        # Place a goal on each step
        goals[i * 2 + 2] = [cur_x + (platform_length + dx) // 2, mid_y + dy]

        # Add gap
        cur_x += platform_length + dx + gap_length

    # Add final goal
    final_gap = m_to_idx(1.0)
    goals[-1] = [cur_x + final_gap / 2, mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals