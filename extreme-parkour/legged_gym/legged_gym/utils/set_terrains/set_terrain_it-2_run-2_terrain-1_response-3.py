import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Narrow beams, varying width platforms, and slopes to test balance, precision, and incline traversal."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define the size parameters based on difficulty
    min_beam_width = 0.4 + 0.1 * difficulty
    max_beam_width = 1.0 - 0.2 * difficulty
    min_platform_width = 1.0 + 0.2 * difficulty
    max_platform_width = 2.0 - 0.2 * difficulty
    min_height = 0.1 * difficulty
    max_height = 0.5 * difficulty
    gap_min = 0.2
    gap_max = 1.0

    mid_y = m_to_idx(width / 2)

    def add_beam_or_platform(start_x, end_x, mid_y, platform_width, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    for i in range(6):  # Set up 6 obstacles
        # Determine if this is a beam, wide platform, or inclined ramp
        if i % 2 == 0:  # Use beams for even indices
            platform_width = np.random.uniform(min_beam_width, max_beam_width)
        else:  # Use wide platforms for odd indices
            platform_width = np.random.uniform(min_platform_width, max_platform_width)

        platform_length = 1.0 + 0.4 * difficulty
        platform_length = m_to_idx(platform_length)
        platform_height = np.random.uniform(min_height, max_height)
        
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        add_beam_or_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, m_to_idx(platform_width), platform_height)

        # Place a goal at each obstacle
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Create a gap between platforms
        gap_length = np.random.uniform(gap_min, gap_max) * difficulty + 0.1
        gap_length = m_to_idx(gap_length)

        cur_x += platform_length + dx + gap_length

    # Add final goal behind the last platform, filling in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals