import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Combination of raised platforms, narrow beams, and sloped surfaces for balance, precision, and incline traversal."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform and slope dimensions
    platform_length = 1.0 - 0.3 * difficulty  # Platform length
    platform_length = m_to_idx(platform_length)
    narrow_platform_width = np.random.uniform(0.4, 0.6)
    narrow_platform_width = m_to_idx(narrow_platform_width)
    wide_platform_width = np.random.uniform(1.0, 1.6)
    wide_platform_width = m_to_idx(wide_platform_width)
    platform_height_min, platform_height_max = 0.2 + 0.3 * difficulty, 0.5 + 0.5 * difficulty
    gap_length = 0.1 + 0.7 * difficulty  # Gap length between platforms
    gap_length = m_to_idx(gap_length)
    slope_length = m_to_idx(1.0)
    slope_height_min, slope_height_max = 0.2 + 0.3 * difficulty, 0.5 + 0.5 * difficulty

    mid_y = m_to_idx(width / 2)

    def add_platform(start_x, end_x, mid_y, platform_width):
        """Add a platform at specified coordinates with a given width."""
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_slope(start_x, end_x, mid_y, platform_width, direction):
        """Add a slope at specified coordinates with a given width and direction for the incline."""
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slope_height = np.random.uniform(slope_height_min, slope_height_max)
        slant = np.linspace(0, slope_height, num=y2-y1)[::direction]
        slant = slant[None, :]  # Add a dimension for broadcasting to x
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    height_field[spawn_length:, :] = -1.0  # Pit

    cur_x = spawn_length
    obstacles = [
        {"type": "platform", "width": wide_platform_width},
        {"type": "slope", "width": narrow_platform_width, "direction": 1},
        {"type": "platform", "width": narrow_platform_width},
        {"type": "slope", "width": wide_platform_width, "direction": -1},
        {"type": "platform", "width": wide_platform_width},
        {"type": "slope", "width": narrow_platform_width, "direction": 1}
    ]

    for i, obstacle in enumerate(obstacles):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        if obstacle["type"] == "platform":
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, obstacle["width"])
        elif obstacle["type"] == "slope":
            add_slope(cur_x, cur_x + slope_length + dx, mid_y + dy, obstacle["width"], obstacle["direction"])

        goals[i+1] = [cur_x + (platform_length + dx) / 2 if obstacle["type"] == "platform" else cur_x + (slope_length + dx) / 2, mid_y + dy]

        cur_x += platform_length + dx + gap_length if obstacle["type"] == "platform" else slope_length + dx + gap_length
    
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals