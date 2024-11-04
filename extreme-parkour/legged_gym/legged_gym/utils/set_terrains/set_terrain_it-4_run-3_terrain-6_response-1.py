import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Varying-height platforms and shallow inclines for balancing and moderate climbing."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length = 1.0 - 0.1 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 0.8
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.1 * difficulty, 0.15 + 0.2 * difficulty
    incline_length = 0.5 + 0.2 * difficulty
    incline_length = m_to_idx(incline_length)
    gap_length = 0.3 + 0.4 * difficulty  # Adjust gap length for difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_incline(start_x, end_x, mid_y, height, direction):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        incline = np.linspace(0, height, num=x2-x1)[::direction]
        incline = incline[:, None]  # Add a dimension for broadcasting to y
        height_field[x1:x2, y1:y2] = incline

    dx_range = m_to_idx([0.0, 0.2])
    dy_range = m_to_idx([0.0, 0.4])
    dy_offset_direction = (-1) ** np.arange(6)  # Alternate slope directions

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    for i in range(5):  # Set up 5 platforms and inclines
        dx = np.random.randint(*dx_range)
        dy = np.random.randint(*dy_range) * dy_offset_direction[i]

        if i % 2 == 0:
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        else:
            height = np.random.uniform(platform_height_min, platform_height_max)
            add_incline(cur_x, cur_x + incline_length + dx, mid_y + dy, height, (-1) ** i)
            goals[i+1] = [cur_x + (incline_length + dx) / 2, mid_y + dy]

        cur_x += platform_length + incline_length + dx + gap_length if i % 2 != 0 else platform_length + dx + gap_length

    # Add final goal behind the last platform/incline, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals