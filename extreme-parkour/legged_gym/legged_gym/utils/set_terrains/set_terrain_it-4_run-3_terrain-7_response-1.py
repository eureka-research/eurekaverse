import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """A complex mix of narrow bridges, raising platforms with varied heights, longer gaps, and sideways ramps to test balance, climbing, incline navigation, and jumping capabilities."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length = m_to_idx(1.0 - 0.3 * difficulty)
    platform_width = m_to_idx(np.random.uniform(0.6, 1.0))  # Width of 0.6 to 1.0 meters
    platform_height = np.random.uniform(0.1, 0.4 * difficulty)  # Slightly raised platforms
    gap_length = m_to_idx(1.0 * difficulty)  # Larger gaps
    
    mid_y = m_to_idx(width) // 2

    def add_narrow_bridge(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = platform_height

    def add_raising_platform(start_x, end_x, mid_y):
        half_width = m_to_idx(1.0) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_heights = np.linspace(0, platform_height, y2 - y1)
        height_field[x1:x2, y1:y2] = platform_heights[None, :]

    def add_sideways_ramp(start_x, end_x, height, mid_y, direction):
        half_width = m_to_idx(1.2) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_heights = np.linspace(0, height, y2 - y1) if direction == 'left' else np.linspace(height, 0, y2 - y1)
        height_field[x1:x2, y1:y2] = ramp_heights[None, :]

    dx_min, dx_max = -0.1, 0.1  # Minor longitudinal offset
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4  # Lateral shift
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    dx = np.random.randint(dx_min, dx_max)
    dy = np.random.randint(dy_min, dy_max)

    add_narrow_bridge(cur_x, cur_x + platform_length, mid_y + dy)
    goals[1] = [cur_x + platform_length // 2, mid_y + dy]
    cur_x += platform_length + gap_length

    for i in range(2, 5):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_raising_platform(cur_x, cur_x + platform_length, mid_y + dy)
        goals[i] = [cur_x + platform_length // 2, mid_y + dy]
        cur_x += platform_length + gap_length

    add_narrow_bridge(cur_x, cur_x + platform_length, mid_y)
    goals[5] = [cur_x + platform_length // 2, mid_y]
    cur_x += platform_length + gap_length

    add_sideways_ramp(cur_x, cur_x + platform_length, platform_height, mid_y, 'left')
    goals[6] = [cur_x + platform_length // 2, mid_y]
    cur_x += platform_length + gap_length

    add_sideways_ramp(cur_x, cur_x + platform_length, platform_height, mid_y, 'right')
    goals[7] = [cur_x + platform_length // 2, mid_y]

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals