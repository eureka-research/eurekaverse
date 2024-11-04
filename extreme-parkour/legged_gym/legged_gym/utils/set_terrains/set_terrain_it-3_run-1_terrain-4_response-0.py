import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Complex varied obstacles: stepping stones, ramps, and staggered platforms with larger height differences and gaps to challenge the quadruped's jumping, climbing, and balancing skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up dimension parameters
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width_min = 0.4
    platform_width_max = 1.5
    platform_height_min, platform_height_max = 0.1 + 0.3 * difficulty, 0.4 + 0.5 * difficulty
    gap_length_min, gap_length_max = 0.2, 0.8
    gap_length_min, gap_length_max = m_to_idx(gap_length_min), m_to_idx(gap_length_max)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, center_y, height):
        half_width = (np.random.uniform(platform_width_min, platform_width_max) * (1 - 0.3 * difficulty)).clip(0.4, 1.5) / 2
        half_width = m_to_idx(half_width)
        x1, x2 = start_x, end_x
        y1, y2 = center_y - half_width, center_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_ramp(start_x, end_x, center_y, direction, height):
        half_width = (np.random.uniform(platform_width_min, platform_width_max) * (1 - 0.3 * difficulty)).clip(0.4, 1.5) / 2
        half_width = m_to_idx(half_width)
        x1, x2 = start_x, end_x
        y1, y2 = center_y - half_width, center_y + half_width
        ramp_height = np.linspace(0, height, num=y2-y1)[::direction]
        ramp_height = ramp_height[None, :]  # Add a dimension for broadcasting to x
        height_field[x1:x2, y1:y2] = ramp_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.0, 0.4  # Set y offset range
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Set remaining area to be a pit with platform obstacles to force navigation through them
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    for i in range(3):  # Set up alternating platforms and ramps
        # Platform
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        height = np.random.uniform(platform_height_min, platform_height_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, height)
        
        if i < 2:
            goals[i*2+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        else:
            goals[6] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        cur_x += platform_length + dx + np.random.randint(gap_length_min, gap_length_max)
        
        # Ramp
        height = np.random.uniform(platform_height_min, platform_height_max)
        direction = (-1) ** (i + 1)  # Alternating left and right ramps
        add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, direction, height)
        
        goals[i*2+2] = [cur_x + (platform_length + dx) / 2, mid_y + dy * direction]

        cur_x += platform_length + dx + np.random.randint(gap_length_min, gap_length_max)

    # Add final platform before the end goal
    dx = np.random.randint(dx_min, dx_max)
    dy = np.random.randint(dy_min, dy_max)
    height = np.random.uniform(platform_height_min, platform_height_max)
    add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, height)
    goals[7] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

    height_field[cur_x:, :] = 0  # Final flat ground leading to the end

    return height_field, goals