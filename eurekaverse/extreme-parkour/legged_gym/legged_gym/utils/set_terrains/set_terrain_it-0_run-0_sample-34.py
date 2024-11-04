import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Set of various ramps and elevated pathways requiring the robot to navigate up and down inclines."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up ramp dimensions and incline based on difficulty
    ramp_length = 1.5 - 0.4 * difficulty  # make ramps longer for lower difficulty
    ramp_length = m_to_idx(ramp_length)
    ramp_width = 2.0  # constant width for ramps
    ramp_width = m_to_idx(ramp_width)
    ramp_height_min, ramp_height_max = 0.1, 0.2 + 0.4 * difficulty  # variable ramp height based on difficulty

    mid_y = m_to_idx(width // 2)

    def add_ramp(start_x, end_x, mid_y, orientation='up'):
        half_width = ramp_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.linspace(0, np.random.uniform(ramp_height_min, ramp_height_max), x2 - x1)
        
        if orientation == 'down':
            ramp_height = np.flip(ramp_height)

        height_field[x1:x2, y1:y2] = ramp_height[:, np.newaxis]

    dx_min, dx_max = -0.2, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.5, 0.5
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at spawn

    cur_x = spawn_length
    for i in range(4):  # Set up 4 ramps
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        ramp_orientation = 'up' if i % 2 == 0 else 'down'
        add_ramp(cur_x, cur_x + ramp_length + dx, mid_y + dy, orientation=ramp_orientation)

        # Put goal at the end of each ramp
        goals[i+1] = [cur_x + ramp_length // 2, mid_y + dy]

        cur_x += ramp_length + dx
    
    # Following set of elevated platforms after the ramps
    platform_length = 1.0 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 1.0  # constant width for platforms
    platform_width = m_to_idx(platform_width)
    platform_height = 0.2 + 0.5 * difficulty 

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = platform_height

    for i in range(3):  # Set up 3 platforms
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)

        # Put goal at the center of each platform
        goals[4+i] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        cur_x += platform_length + dx
    
    # Add final goal at the end of the course
    goals[-1] = [cur_x + m_to_idx(1.0), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals