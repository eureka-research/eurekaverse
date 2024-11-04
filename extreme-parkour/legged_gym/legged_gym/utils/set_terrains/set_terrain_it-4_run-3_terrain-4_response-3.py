import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Combination of elevated platforms, staggered stairs, and ramps to enhance robot's agility."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.2)  # Slightly narrow platform
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.25 * difficulty, 0.15 + 0.35 * difficulty
    gap_length = 0.2 + 0.8 * difficulty
    gap_length = m_to_idx(gap_length)
    step_height = 0.1 + 0.2 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_staggered_steps(start_x, mid_y, steps, step_height):
        x = start_x
        direction = 1
        for i in range(steps):
            x1, x2 = x, x + m_to_idx(0.5)
            y1, y2 = mid_y - m_to_idx(platform_width / 2.0), mid_y + m_to_idx(platform_width / 2.0)
            height_field[x1:x2, y1:y2] = i * step_height
            x += m_to_idx(0.5)
            direction *= -1

        return x

    def add_ramp(start_x, end_x, mid_y, direction):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(0.15, 0.3)
        slant = np.linspace(0, ramp_height, num=y2-y1)[::direction]
        slant = slant[None, :]  # Add a dimension for broadcasting to x
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.0, 0.4  # Polarity of dy will alternate instead of being random
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Set first platform
    cur_x = spawn_length
    dx = np.random.randint(dx_min, dx_max)
    dy = np.random.randint(dy_min, dy_max)
    add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
    goals[1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
    cur_x += platform_length + dx + gap_length

    # Add staggered steps nicely increasing difficulty
    cur_x = add_staggered_steps(cur_x, mid_y, 4, step_height) + gap_length
    goals[2] = [cur_x - gap_length / 2, mid_y]

    # Add ramp
    dx = np.random.randint(dx_min, dx_max)
    dy = 0  # Ensure this isn't imbalanced sideways
    add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, 1)
    goals[3] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
    cur_x += platform_length + dx + gap_length

    # Raise platform
    dx = np.random.randint(dx_min, dx_max)
    dy = np.random.randint(dy_min, dy_max)
    add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
    goals[4] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
    cur_x += platform_length + dx + gap_length

    # Add another staggered step platform
    cur_x = add_staggered_steps(cur_x, mid_y, 3, step_height * 0.5) + gap_length
    goals[5] = [cur_x - gap_length / 2, mid_y]

    # Add another ramp with reverse direction
    dx = np.random.randint(dx_min, dx_max)
    dy = 0  # Ensure this isn't imbalanced sideways
    add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, -1)
    goals[6] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
    cur_x += platform_length + dx + gap_length

    # Set final goal behind the last obstacle
    goals[7] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals