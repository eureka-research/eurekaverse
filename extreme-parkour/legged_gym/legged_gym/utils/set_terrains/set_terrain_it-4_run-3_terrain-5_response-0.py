import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """A blend of curved inclines and varied-width platforms to navigate carefully and balance across obstacles."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform and incline dimensions
    platform_length_base = 1.0 - 0.2 * difficulty
    platform_width_range = (1.0, 1.6)
    platform_height_min, platform_height_max = 0.1, 0.5 * difficulty
    incline_length = 1.0 - 0.2 * difficulty
    incline_length = m_to_idx(incline_length)
    gap_length_base = 0.1 + 0.4 * difficulty
    mid_y = m_to_idx(width) // 2

    def add_platform_segment(start_x, width_range, height_range):
        half_width = m_to_idx(np.random.uniform(*width_range)) // 2
        x1, x2 = start_x, start_x + m_to_idx(platform_length_base)
        y_center = mid_y + np.random.randint(-m_to_idx(0.5), m_to_idx(0.5))
        y1, y2 = y_center - half_width, y_center + half_width
        platform_height = np.random.uniform(*height_range)
        height_field[x1:x2, y1:y2] = platform_height
        return x2, y_center

    def add_incline(start_x, direction):
        half_width = m_to_idx(platform_width_range[0]) // 2
        x1, x2 = start_x, start_x + incline_length
        if direction > 0:
            slant = np.linspace(0, difficulty * 0.5, num=x2-x1)[:, None]
        else:
            slant = np.linspace(difficulty * 0.5, 0, num=x2-x1)[:, None]
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] += slant

    x_start = m_to_idx(2)
    goals[0] = [x_start - m_to_idx(0.5), mid_y]

    # Setting platforms with variations
    for i in range(4):
        x_start, y_center = add_platform_segment(x_start, platform_width_range, (platform_height_min, platform_height_max))
        goals[i+1] = [x_start - m_to_idx(platform_length_base / 2), y_center]
        x_start += m_to_idx(gap_length_base)
    
    # Adding an incline path
    add_incline(x_start, direction=1)
    goals[5] = [x_start + incline_length // 2, mid_y]

    x_start += incline_length + m_to_idx(gap_length_base)

    # Setting remaining varied-height platforms
    for i in range(2):
        x_start, y_center = add_platform_segment(x_start, platform_width_range, (platform_height_min, platform_height_max))
        goals[6+i] = [x_start - m_to_idx(platform_length_base / 2), y_center]
        x_start += m_to_idx(gap_length_base)

    # Final goal and reset terrain to flat toward the end.
    goals[7] = [x_start + m_to_idx(0.5), mid_y]
    height_field[x_start:, :] = 0

    return height_field, goals