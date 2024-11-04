import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Alternating stepping stones and inclined ramps traversing a pit for the robot to climb on and jump across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and ramp dimensions
    platform_length = 1.0 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.3)  # Slightly narrower platforms
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.2 * difficulty, 0.3 + 0.2 * difficulty

    ramp_length = 1.0 - 0.2 * difficulty
    ramp_length = m_to_idx(ramp_length)
    ramp_height_min, ramp_height_max = 0.15 + 0.1 * difficulty, 0.35 + 0.2 * difficulty

    gap_length = 0.5 + 0.5 * difficulty  # Balanced gap length
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(center_x, center_y):
        half_length = platform_length // 2
        half_width = platform_width // 2
        x1, x2 = center_x - half_length, center_x + half_length
        y1, y2 = center_y - half_width, center_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_ramp(center_x, center_y, direction):
        half_length = ramp_length // 2
        half_width = platform_width // 2
        x1, x2 = center_x - half_length, center_x + half_length
        y1, y2 = center_y - half_width, center_y + half_width
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        
        if direction == 'up':
            slant = np.linspace(0, ramp_height, num=x2-x1)
        else:
            slant = np.linspace(ramp_height, 0, num=x2-x1)
        
        slant = slant[:, None]  # Add a dimension for broadcasting to y
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Set remaining area to be a pit
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length + gap_length
    for i in range(3):  # Set up 3 stepping stones
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x + dx, mid_y + dy)

        # Put goal in the center of the platform
        goals[i+1] = [cur_x + dx, mid_y + dy]

        # Add gap
        cur_x += platform_length + dx + gap_length

    for i in range(4, 7):  # Set up 3 ramps
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        direction = 'up' if i % 2 == 0 else 'down'
        add_ramp(cur_x + dx, mid_y + dy, direction)

        # Put goal in the center of the ramp
        goals[i] = [cur_x + dx, mid_y + dy]

        # Add gap
        cur_x += ramp_length + dx + gap_length
    
    # Final goal behind the last ramp, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals