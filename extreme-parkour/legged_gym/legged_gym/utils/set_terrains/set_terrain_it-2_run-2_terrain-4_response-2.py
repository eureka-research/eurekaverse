import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Mixed obstacles include taller steps, varied gaps, and angled platforms for increased difficulty."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Setup platform dimensions with increased complexity
    platform_length = 0.8 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 0.6 - 0.1 * difficulty
    platform_width = m_to_idx(platform_width)
    platform_height_base = 0.15
    platform_height_var = 0.15 * difficulty
    gap_length_min = 0.2
    gap_length_max = 0.5 + 0.5 * difficulty
    gap_length_min = m_to_idx(gap_length_min)
    gap_length_max = m_to_idx(gap_length_max)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, height, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_step(start_x, end_x, height):
        step_width = m_to_idx(0.4)
        half_width = step_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)
    
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    current_x = spawn_length
    num_obstacles = 7  # Increase number of obstacles

    for i in range(num_obstacles):
        platform_height = platform_height_base + np.random.uniform(0, platform_height_var)
        add_platform(current_x, current_x + platform_length, platform_height, mid_y)
        goals[i+1] = [current_x + platform_length // 2, mid_y]

        gap_length = random.randint(gap_length_min, gap_length_max)
        current_x += platform_length + gap_length

    # Filling in the remaining part
    height_field[current_x:, :] = 0
    goals[-1] = [m_to_idx(length - 0.5), mid_y]

    return height_field, goals