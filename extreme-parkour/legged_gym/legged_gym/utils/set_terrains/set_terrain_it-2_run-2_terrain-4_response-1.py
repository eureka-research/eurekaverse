import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Urban-inspired course with dynamic platforms, walls, and ramps to test agility and decision-making."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Ramp, wall, and platform configurations
    # We introduce a mix of fixed and "dynamic" platforms
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width_min = 1.0
    platform_width_max = 1.5
    platform_width_min = m_to_idx(platform_width_min)
    platform_width_max = m_to_idx(platform_width_max)
    wall_height_min, wall_height_max = 0.25, 0.5
    gap_length = 0.1 + 0.7 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, width, height):
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_wall(start_x, end_x, height):
        width = m_to_idx(0.3)
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_ramp(start_x, end_x, height):
        ramp_width = np.random.uniform(platform_width_min, platform_width_max)
        ramp_width = m_to_idx(ramp_width)
        half_width = ramp_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slant = np.linspace(0, height, num=y2-y1)
        slant = slant[None, :]  # Add a dimension for broadcasting to x
        height_field[x1:x2, y1:y2] = slant

    # Reset for next obstacle to use in goals placement
    dx_min, dx_max = -0.2, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    # Add a series of walls
    for i in range(2):
        wall_height = np.random.uniform(wall_height_min, wall_height_max)
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_wall(cur_x, cur_x + platform_length + dx, wall_height)
        goals[i+1] = [cur_x + (platform_length + dx) // 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

    # Add a series of ramps
    for i in range(2):
        ramp_height = np.random.uniform(wall_height_min, wall_height_max)
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_ramp(cur_x, cur_x + platform_length + dx, ramp_height)
        goals[i+3] = [cur_x + (platform_length + dx) // 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

    # Add a series of platforms with variable heights
    for i in range(2):
        platform_height = np.random.uniform(wall_height_min, wall_height_max)
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        platform_width = np.random.uniform(platform_width_min, platform_width_max)
        platform_width = m_to_idx(platform_width)
        add_platform(cur_x, cur_x + platform_length + dx, platform_width, platform_height)
        goals[i+5] = [cur_x + (platform_length + dx) // 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals