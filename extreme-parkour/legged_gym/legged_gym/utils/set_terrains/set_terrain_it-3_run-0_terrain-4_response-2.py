import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Staggered platforms and ramps with varying heights for the quadruped to balance, climb, and jump across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and ramp dimensions
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.6, 1.0)  # Slightly narrow platform widths
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 * difficulty + 0.1, 0.35 * difficulty + 0.2
    ramp_height_min, ramp_height_max = 0.2 * difficulty + 0.1, 0.4 * difficulty + 0.2
    gap_length = 0.2 + 0.6 * difficulty  # Moderately challenging gap lengths
    gap_length = m_to_idx(gap_length)
    
    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_ramp(start_x, end_x, mid_y, direction, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slant = np.linspace(0, height, num=x2-x1)[::direction]
        height_field[x1:x2, y1:y2] = np.broadcast_to(slant[:, None], (x2-x1, y2-y1))
    
    mid_y = m_to_idx(width) // 2
    dx_min, dx_max = m_to_idx(-0.1), m_to_idx(0.1)
    dy_shift = m_to_idx(0.2)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    height_field[spawn_length:, :] = -1.0  # Pit area
    
    cur_x = spawn_length
    direction = 1

    for i in range(6):
        dx = np.random.randint(dx_min, dx_max)
        dy = dy_shift if i % 2 == 0 else -dy_shift
        height = np.random.uniform(platform_height_min, platform_height_max if i % 2 == 0 else ramp_height_max)

        if i % 2 == 0:  # Add platforms
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, height)
        else:  # Add ramps
            add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, direction, height)
            direction *= -1  # Alternate ramp direction

        goals[i+1] = [cur_x + (platform_length + dx) // 2, mid_y + dy]

        cur_x += platform_length + dx + gap_length

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals