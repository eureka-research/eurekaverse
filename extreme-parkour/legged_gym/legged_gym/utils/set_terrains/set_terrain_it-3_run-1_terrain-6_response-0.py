import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Multiple sideways-facing ramps, narrow platforms, and steps to test balance, climbing, and navigation."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform and obstacle dimensions
    platform_length = 1.0 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.2)  # Narrower platforms
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.3 * difficulty, 0.1 + 0.4 * difficulty
    ramp_height_min, ramp_height_max = 0.0 + 0.3 * difficulty, 0.2 + 0.5 * difficulty
    step_height = 0.15 + 0.3 * difficulty
    gap_length = 0.2 + 0.5 * difficulty

    mid_y = m_to_idx(width) // 2
    step_height = m_to_idx(step_height)
    gap_length = m_to_idx(gap_length)

    def add_platform(start_x, length, width, height, center_y):
        half_width = width // 2
        height_field[start_x:start_x+length, center_y-half_width:center_y+half_width] = height

    def add_ramp(start_x, length, width, height, direction, center_y):
        half_width = width // 2
        if direction == 'right':
            slant = np.linspace(0, height, num=length)
        else:  # left
            slant = np.linspace(height, 0, num=length)
        slant = slant[:, np.newaxis]  # Add a dimension for broadcasting to y
        height_field[start_x:start_x+length, center_y-half_width:center_y+half_width] = slant

    def add_steps(start_x, length, step_height, center_y):
        for x in range(start_x, start_x+length):
            height_field[x, center_y-step_height:center_y+step_height] = x % 2 * step_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.0, 0.4  # Dy polarity alternates comparatively
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Spawn area setup
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Pit for generated terrain
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    for i in range(7):
        if i % 2 == 0:
            # Alternating between platforms and ramps/steps
            if i == 6:  # Last obstacle as steps
                length = platform_length
                add_steps(cur_x, length, step_height, mid_y)
            else:
                length = platform_length + np.random.randint(dx_min, dx_max)
                add_platform(cur_x, length, platform_width, np.random.uniform(platform_height_min, platform_height_max), mid_y)

            goals[i+1] = [cur_x + length // 2, mid_y]
            cur_x += length + gap_length
        else:
            length = platform_length + np.random.randint(dx_min, dx_max)
            direction = 'right' if i % 2 == 1 else 'left'
            add_ramp(cur_x, length, platform_width, np.random.uniform(ramp_height_min, ramp_height_max), direction, mid_y)

            goals[i+1] = [cur_x + length // 2, mid_y]
            cur_x += length + gap_length

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals