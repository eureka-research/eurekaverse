import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Slanted ramps and narrow pathways for the robot to balance, navigate, and climb, increasing difficulty."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform and ramp variables with increased complexity
    platform_length = max(0.5, 1.2 - 0.6 * difficulty)
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.4, 1.0)  # Make some narrow paths
    platform_width = m_to_idx(platform_width)
    ramp_height_min, ramp_height_max = 0.3 + 0.4 * difficulty, 0.5 + 0.7 * difficulty
    gap_length = 0.2 + 0.9 * difficulty  # Increase gap length for hardness
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_ramp(start_x, end_x, mid_y, direction, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slant = np.linspace(0, height, y2-y1)[::direction]
        slant = slant[None, :]  # Broadcasting for x-dim
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.0, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Set first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Set a flat path for initial learning
    height_field[spawn_length:, :] = -0.1

    cur_x = spawn_length
    for i in range(6):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        direction = 1 if i % 2 == 0 else -1  # Alternate directions
        if i % 3 == 0:  # Add ramps every 3rd platform to mix climbing and balance
            ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
            add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, direction, ramp_height)
            goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
            cur_x += platform_length + dx + gap_length
        else:
            platform_height = np.random.uniform(ramp_height_min, ramp_height_max) / 2
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height)
            goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
            cur_x += platform_length + dx + gap_length
        
    # Add final goal at the end of last platform, fill the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals