import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Combination of ramps, beams, and platforms with varied heights and lateral movements for advanced parkour."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define obstacle dimensions
    beam_width = 0.4
    beam_length = 2.0 - (0.5 * difficulty)
    beam_width = m_to_idx(beam_width)
    beam_length = m_to_idx(beam_length)

    platform_height_min = 0.1 + 0.4 * difficulty
    platform_height_max = 0.3 + 0.7 * difficulty
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.0)
    platform_width = m_to_idx(platform_width)
    gap_length = 0.2 + 0.8 * difficulty
    gap_length = m_to_idx(gap_length)

    ramp_length = 1.0 - 0.3 * difficulty
    ramp_length = m_to_idx(ramp_length)
    ramp_height_min, ramp_height_max = 0.1 + 0.5 * difficulty, 0.3 + 0.5 * difficulty
    ramp_width = platform_width

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, mid_y):
        """Adds a narrow beam."""
        half_width = beam_width // 2
        x1, x2 = start_x, start_x + beam_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = platform_height_min
        return (x1 + x2) // 2, mid_y

    def add_platform(start_x, mid_y):
        """Adds a raised platform with random height."""
        half_width = platform_width // 2
        x1, x2 = start_x, start_x + platform_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height
        return (x1 + x2) // 2, mid_y

    def add_ramp(start_x, mid_y, direction):
        """Adds an inclined ramp."""
        half_width = ramp_width // 2
        x1, x2 = start_x, start_x + ramp_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        ramp_height_line = np.linspace(0, ramp_height, num=(x2-x1))[:, None]
        height_field[x1:x2, y1:y2] = ramp_height_line * (1 if direction == 'up' else -1)
        return (x1 + x2) // 2, mid_y

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[:spawn_length, :] = 0
    # Set the first goal
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Set remaining area to be a pit forcing quadruped to jump from platform to platform
    height_field[spawn_length:, :] = -1.0

    # Initialize position tracking variables
    cur_x = spawn_length
    for i in range(6):
        if i % 3 == 0:
            cx, cy = add_beam(cur_x, mid_y)
        elif i % 3 == 1:
            offset = np.random.randint(-m_to_idx(0.4), m_to_idx(0.4))
            dir_ramp = 'up' if i % 2 == 0 else 'down'
            cx, cy = add_ramp(cur_x, mid_y + offset, dir_ramp)
        else:
            offset = np.random.randint(-m_to_idx(0.4), m_to_idx(0.4))
            cx, cy = add_platform(cur_x, mid_y + offset)

        goals[i + 1] = [cx, cy]  # Place goal at the obstacle center
        
        # Move to next obstacle position
        cur_x += platform_length + gap_length

    # Set the final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals