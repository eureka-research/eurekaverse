import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Alternating steps and staggered floating platforms for the quadruped to coordinate and balance across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up step and platform dimensions
    platform_length = 0.8 + 0.4 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.9, 1.2)
    platform_width = m_to_idx(platform_width)
    step_height = 0.1 + 0.1 * difficulty
    gap_length_min = 0.05 + 0.45 * difficulty
    gap_length_max = 0.1 + 0.55 * difficulty

    step_height = m_to_idx(step_height)
    gap_length_min = m_to_idx(gap_length_min)
    gap_length_max = m_to_idx(gap_length_max)

    mid_y = m_to_idx(width) // 2  # Center line of the field

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = 0.0, 0.2
    dy_min, dy_max = 0.0, 0.4  # Staggered steps

    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0.0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at spawn

    # Current x position to start adding obstacles
    cur_x = spawn_length

    for i in range(7):  # Create 7 obstacles
        # Calculate dimensions and position for the current platform
        dx = np.random.randint(dx_min - dx_max // 2, dx_max)
        dy_shift = np.random.randint(dy_min, dy_max)
        height = np.random.uniform(step_height, step_height * 1.5)  # Randomized height

        if i % 2 == 0:  # Even index, add staggered platform
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy_shift, height)
            goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy_shift]

        else:  # Odd index, add slightly increased gap
            add_platform(cur_x, cur_x + platform_length + dx, mid_y - dy_shift, height)
            goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y - dy_shift]

        gap_length = np.random.randint(gap_length_min - gap_length_max // 2, gap_length_max)
        cur_x += platform_length + dx + gap_length

    # Final goal behind the last platform, fill in the remaining gap
    height_field[cur_x:, :] = 0.0
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    return height_field, goals