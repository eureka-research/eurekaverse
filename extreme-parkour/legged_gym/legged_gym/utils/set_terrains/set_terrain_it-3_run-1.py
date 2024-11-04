
import numpy as np
import random

def set_terrain(terrain, variation, difficulty):
    terrain_fns = [
        set_terrain_0,
        set_terrain_1,
        set_terrain_2,
        set_terrain_3,
        set_terrain_4,
        set_terrain_5,
        set_terrain_6,
        set_terrain_7,
        set_terrain_8,
        set_terrain_9,
        # INSERT TERRAIN FUNCTIONS HERE
    ]
    idx = int(variation * len(terrain_fns))
    height_field, goals = terrain_fns[idx](terrain.width * terrain.horizontal_scale, terrain.length * terrain.horizontal_scale, terrain.horizontal_scale, difficulty)
    terrain.height_field_raw = (height_field / terrain.vertical_scale).astype(np.int16)
    terrain.goals = goals
    return idx

def set_terrain_0(length, width, field_resolution, difficulty):
    """Combination of platforms, gaps, ramps, and uneven terrains testing multidimensional navigation skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform dimensions
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.6)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.2 * difficulty, 0.05 + 0.25 * difficulty
    uneven_terrain_height_var = 0.1 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_ramp(start_x, end_x, mid_y, is_uphill):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slope_height = np.linspace(0.0, 0.3 * difficulty if is_uphill else -0.3 * difficulty, num=x2-x1)
        slope_height = slope_height[:, None]  # add dimension for broadcasting
        height_field[x1:x2, y1:y2] = slope_height

    def add_uneven_terrain(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        for i in range(x1, x2):
            for j in range(y1, y2):
                height_field[i, j] = np.random.uniform(-uneven_terrain_height_var, uneven_terrain_height_var)

    gap_length = 0.1 + 0.5 * difficulty  # Balanced gap length
    gap_length = m_to_idx(gap_length)

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(3):  # First 3 platforms
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

    for i in range(3, 5):  # Next 2 ramps
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, is_uphill=i % 2 == 0)
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

    for i in range(5, 7):  # Last 2 uneven terrains
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_uneven_terrain(cur_x, cur_x + platform_length + dx, mid_y + dy)
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_1(length, width, field_resolution, difficulty):
    """Stepped platforms with varying heights and alternating clear sections for the robot to climb and jump across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        if isinstance(m, (list, tuple)):
            return [round(i / field_resolution) for i in m]
        else:
            return np.round(m / field_resolution).astype(np.int16)

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length = 0.9 - 0.2 * difficulty  # Slightly shorter platforms with higher difficulty
    platform_length = m_to_idx(platform_length)
    
    platform_height_min, platform_height_max = 0.1 + 0.3 * difficulty, 0.2 + 0.5 * difficulty
    platform_width = np.random.uniform(1.2, 1.6)  # Increase minimum width
    platform_width = m_to_idx(platform_width)
    
    gap_length = 0.4 + 0.8 * difficulty  # Slightly wider gaps for harder difficulty
    gap_length = m_to_idx(gap_length)
    
    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    dx_min, dx_max = -0.08, 0.08
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  
    
    cur_x = spawn_length

    for i in range(6):  # Set up 6 platforms
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max) * ((-1) ** i)  # Alternate directions
        
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
        
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        
        cur_x += platform_length + dx + gap_length

    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_2(length, width, field_resolution, difficulty):
    """Combination of varied ramps, narrow bridges, and staggered platforms for increased challenge in climbing, balancing, and jumping."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Constants for obstacle dimensions
    platform_length = m_to_idx(1.0 - 0.2 * difficulty)
    platform_height = 0.2 * difficulty
    bridge_width = m_to_idx(0.4 * difficulty + 0.6)
    ramp_height = 0.25 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        y1, y2 = mid_y - m_to_idx(0.5), mid_y + m_to_idx(0.5)
        height_field[start_x:end_x, y1:y2] = height
    
    def add_ramp(start_x, end_x, mid_y, slope, direction):
        y1, y2 = mid_y - (slope * (end_x - start_x) // 2), mid_y + (slope * (end_x - start_x) // 2)
        if direction == 'up':
            height = np.linspace(0, ramp_height, end_x - start_x)
        else:
            height = np.linspace(ramp_height, 0, end_x - start_x)
        height_field[start_x:end_x, y1:y2] = height[:, None]

    def add_bridge(start_x, end_x, mid_y, width_idx):
        y1, y2 = mid_y - width_idx // 2, mid_y + width_idx // 2
        height_field[start_x:end_x, y1:y2] = platform_height

    def add_staggered_steps(start_x, end_x, mid_y):
        for i in range(start_x, end_x, m_to_idx(0.5)):
            step_height = np.random.uniform(0, platform_height)
            height_field[i:i + m_to_idx(0.5), mid_y - m_to_idx(0.25):mid_y + m_to_idx(0.25)] = step_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    obstacles = [
        {'type': 'platform', 'length': platform_length, 'height': platform_height},
        {'type': 'ramp', 'slope': 1, 'direction': 'up', 'length': platform_length},
        {'type': 'bridge', 'width': bridge_width, 'length': platform_length},
        {'type': 'steps', 'length': platform_length},
        {'type': 'ramp', 'slope': 1, 'direction': 'down', 'length': platform_length},
        {'type': 'platform', 'length': platform_length, 'height': platform_height}
    ]

    for i, obs in enumerate(obstacles, 1):
        if obs['type'] == 'platform':
            add_platform(cur_x, cur_x + obs['length'], mid_y, obs['height'])
        elif obs['type'] == 'ramp':
            add_ramp(cur_x, cur_x + obs['length'], mid_y, obs['slope'], obs['direction'])
        elif obs['type'] == 'bridge':
            add_bridge(cur_x, cur_x + obs['length'], mid_y, obs['width'])
        elif obs['type'] == 'steps':
            add_staggered_steps(cur_x, cur_x + obs['length'], mid_y)
        
        goals[i] = [cur_x + obs['length'] // 2, mid_y]
        cur_x += obs['length'] + m_to_idx(0.4 * difficulty)

    # Fill remaining area beyond the last obstacle and place final goal
    if cur_x < m_to_idx(length) - m_to_idx(1):
        add_platform(cur_x, m_to_idx(length), mid_y, 0)
    goals[-1] = [m_to_idx(11.5), mid_y]

    return height_field, goals

def set_terrain_3(length, width, field_resolution, difficulty):
    """Complex elevated and uneven terrain for enhanced difficulty, testing the robot's balance and climbing abilities."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define the size parameters based on difficulty
    min_platform_width = 0.6 + 0.1 * difficulty
    max_platform_width = 1.2 - 0.1 * difficulty
    min_height = 0.1 * difficulty
    max_height = 0.5 * difficulty
    min_gap = 0.2
    max_gap = 0.8 + 0.2 * difficulty

    mid_y = m_to_idx(width / 2)

    def add_platform_or_slope(start_x, end_x, mid_y, platform_width, height, incline=False):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        if incline:
            slope = np.linspace(0, height, num=x2-x1)[:, None]
            height_field[x1:x2, y1:y2] = np.broadcast_to(slope, (x2-x1, y2-y1))
        else:
            height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    for i in range(6):  # Set up 6 obstacles
        platform_width = np.random.uniform(min_platform_width, max_platform_width)
        platform_width = m_to_idx(platform_width)
        platform_length = 1.0 + 0.4 * difficulty
        platform_length = m_to_idx(platform_length)
        platform_height = np.random.uniform(min_height, max_height)

        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        # Randomly decide if the obstacle is an inclined ramp or flat platform
        incline = np.random.rand() > 0.5

        add_platform_or_slope(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_width, platform_height, incline)

        # Place a goal at each obstacle
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Create a gap between platforms
        gap_length = np.random.uniform(min_gap, max_gap) * difficulty + 0.2
        gap_length = m_to_idx(gap_length)

        cur_x += platform_length + dx + gap_length

    # Add final goal behind the last platform, filling in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_4(length, width, field_resolution, difficulty):
    """Combined staggered steps, narrow and wide platforms, and ramps for varied navigation challenges."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Dimensions for diverse and moderately challenging obstacles
    platform_length = 1.5 - 0.4 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width_low, platform_width_high = 1.0, 1.6
    platform_height_min, platform_height_max = 0.3 + 0.2 * difficulty, 0.5 + 0.3 * difficulty
    ramp_height_min, ramp_height_max = 0.2 + 0.3 * difficulty, 0.5 + 0.4 * difficulty
    gap_length = 0.3 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, is_ramp=False):
        half_width = np.random.uniform(platform_width_low, platform_width_high)
        half_width = m_to_idx(half_width) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        if is_ramp:
            direction = np.random.choice([-1, 1])
            ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
            slant = np.linspace(0, ramp_height, num=y2-y1)[::direction]
            slant = slant[None, :]  # Add a dimension for broadcasting to x
            height_field[x1:x2, y1:y2] = slant
        else:
            platform_height = np.random.uniform(platform_height_min, platform_height_max)
            height_field[x1:x2, y1:y2] = platform_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Place the first goal near the spawn area
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]
    
    # Creating a variety of obstacles
    cur_x = spawn_length
    dy_min, dy_max = -0.5, 0.5  # Promoting diverse stepping
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    for i in range(6):  # Set up 6 obstacles with alternating platforms and ramps
        dx = np.random.randint(-1, 2)  # Small random variance in x-direction positioning
        dy = np.random.randint(dy_min, dy_max)  # Small random variance in y-direction positioning
        if i % 2 == 0:  # Even index, place a platform
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        else:  # Odd index, place a ramp
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, is_ramp=True)
            goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        cur_x += platform_length + dx + gap_length

    # Add final goal behind the last obstacle
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0  # Fill the remaining terrain with flat ground

    return height_field, goals

def set_terrain_5(length, width, field_resolution, difficulty):
    """Wide uneven terrain and smooth ramps to test balance and elevation traversal."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions
    platform_length = 1.5 - 0.4 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 2.0)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.05 + 0.1 * difficulty, 0.3 + 0.2 * difficulty
    gap_length = 0.3 + 0.3 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_ramp(start_x, end_x, mid_y, height_start, height_end):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        for x in range(x1, x2):
            height_progress = height_start + (height_end - height_start) * ((x - x1) / (x2 - x1))
            height_field[x, y1:y2] = height_progress

    dx_min, dx_max = -0.2, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.1, 0.1
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    current_height = 0
    for i in range(5):  # Set up 5 wide uneven platforms
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        next_height = np.random.uniform(platform_height_min, platform_height_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, next_height)

        # Put goal in the center of the platform
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Smooth ramp
        cur_x_ramp_start = cur_x + platform_length + dx
        cur_x_ramp_end = cur_x_ramp_start + m_to_idx(0.5 * difficulty)
        add_ramp(cur_x_ramp_start, cur_x_ramp_end, mid_y + dy, current_height, next_height)
        current_height = next_height

        # Add gap
        cur_x = cur_x_ramp_end + gap_length

    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_6(length, width, field_resolution, difficulty):
    """Combination of staggered steps, variable-height platforms, and safe landing zones for the quadruped."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Adjusted obstacle dimensions
    platform_length = 1.0 - 0.2 * difficulty  # Slightly longer platforms
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.2)  # Increase platform width
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.15 * difficulty, 0.30 * difficulty
    gap_length = 0.1 + 0.4 * difficulty  # Minimized gap length
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, length, width, height, mid_y):
        half_width = width // 2
        height_field[start_x:start_x+length, mid_y-half_width:mid_y+half_width] = height

    def add_ramp(start_x, end_x, mid_y, direction, min_height, max_height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(min_height, max_height)
        slant = np.linspace(0, ramp_height, num=y2-y1)[::direction]
        height_field[x1:x2, y1:y2] = slant
    
    dx = m_to_idx(-0.1)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Flat ground at start
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Remaining area set to low height to allow navigation onto platforms
    height_field[spawn_length:, :] = -1.0

    # First platform
    cur_x = spawn_length
    dy = np.random.randint(dy_min, dy_max)
    add_platform(cur_x, platform_length, platform_width, np.random.uniform(platform_height_min, platform_height_max), mid_y + dy)
    goals[1] = [cur_x + platform_length // 2, mid_y + dy]

    cur_x += platform_length + gap_length
    for i in range(1, 6):
        dy = np.random.randint(dy_min, dy_max)
        if i % 2 == 0:
            add_platform(cur_x, platform_length, platform_width, np.random.uniform(platform_height_min, platform_height_max), mid_y + dy)
        else:
            add_ramp(cur_x, cur_x + platform_length, mid_y + dy, (-1) ** i, platform_height_min, platform_height_max)
        
        goals[i+1] = [cur_x + platform_length // 2, mid_y + dy]
        cur_x += platform_length + gap_length
    
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_7(length, width, field_resolution, difficulty):
    """Obstacle course with staggered platforms, ramps, and gaps requiring the quadruped to balance, climb, and jump effectively."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length = m_to_idx(1.0 - 0.2 * difficulty)
    platform_width = m_to_idx(np.random.uniform(0.8, 1.2))
    platform_height_min, platform_height_max = 0.1 * difficulty, 0.3 * difficulty
    ramp_length = m_to_idx(0.5)  # keeping ramps shorter
    ramp_height_min, ramp_height_max = 0.2, 0.4 + 0.3 * difficulty
    gap_length = m_to_idx(0.3 + 0.5 * difficulty)  # Increase gap length

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_ramp(start_x, end_x, mid_y, height, direction):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slope = np.linspace(0, height, num=end_x-start_x)
        if direction > 0:
            height_field[x1:x2, y1:y2] = slope[:, np.newaxis]
        else:
            height_field[x1:x2, y1:y2] = slope[::-1, np.newaxis]

    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0.0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    for i in range(4):  # Create 4 main sections: 2 platforms and 2 ramps
        height = np.random.uniform(platform_height_min, platform_height_max)
        if i % 2 == 0:  # Add platforms on even iterations
            add_platform(cur_x, cur_x + platform_length, mid_y, height)
            goals[i + 1] = [cur_x + platform_length // 2, mid_y]
            cur_x += platform_length + gap_length
        else:  # Add ramps on odd iterations
            ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
            direction = 1 if i % 4 == 1 else -1
            add_ramp(cur_x, cur_x + ramp_length, mid_y, ramp_height, direction)
            goals[i + 1] = [cur_x + ramp_length // 2, mid_y]
            cur_x += ramp_length + gap_length

    final_height = np.random.uniform(platform_height_min, platform_height_max)
    add_platform(cur_x, cur_x + platform_length, mid_y, final_height)
    goals[5] = [cur_x + platform_length // 2, mid_y]
    cur_x += platform_length

    for i in range(2):  # add some simple stepping obstacles
        height = np.random.uniform(platform_height_min, platform_height_max)
        dx = m_to_idx(0.3 * (i + 1))
        dy = m_to_idx(0.5 * (i + 1))
        add_platform(cur_x + dx, cur_x + dx + platform_length, mid_y + dy, height)
        goals[6 + i] = [cur_x + dx + platform_length // 2, mid_y + dy]
        cur_x += platform_length + gap_length

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0.0

    return height_field, goals

def set_terrain_8(length, width, field_resolution, difficulty):
    """Staggered platforms and varying-height ramps for the robot to climb and jump across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and ramp dimensions
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.4)  # Uniform platform width
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.05 + 0.2 * difficulty, 0.1 + 0.3 * difficulty
    ramp_height_min, ramp_height_max = 0.1 + 0.3 * difficulty, 0.2 + 0.6 * difficulty
    gap_length = 0.1 + 0.5 * difficulty  # Decreased gap length for feasibility
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_ramp(start_x, end_x, mid_y, direction):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        slant = np.linspace(0, ramp_height, num=x2-x1)[::direction]
        slant = slant[:, None]  # Add a dimension for broadcasting to y
        height_field[x1:x2, y1:y2] = slant

    # Polarity of dy will alternate instead of being random
    dx_min, dx_max = m_to_idx(-0.1), m_to_idx(0.1)
    dy_min = m_to_idx(-0.3)
    dy_max = m_to_idx(0.3)
    
    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Use a mix of platforms and ramps
    cur_x = spawn_length
    for i in range(6):
        dx = np.random.randint(dx_min, dx_max)
        dy = (i % 2) * np.random.randint(dy_min, dy_max) * (1 if i % 2 == 0 else -1)

        if i % 2 == 0:  # Add platform
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
        else:  # Add ramp
            direction = (-1) ** (i+1)
            add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, direction)

        goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

    # Add final goal behind the last obstacle, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_9(length, width, field_resolution, difficulty):
    """Combination of narrow walkways, descending steps, and angled ramps to test balance, climbing, and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up dimensions for features
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    walkway_length = m_to_idx(0.8 - 0.3 * difficulty)
    walkway_width = m_to_idx(0.35 if difficulty > 0.4 else 0.5)
    ramp_length = m_to_idx(1.0 - 0.3 * difficulty)
    gap_length = m_to_idx(0.2 + 0.5 * difficulty)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        height = np.random.uniform(0.15 * difficulty, 0.4 * difficulty)
        half_width = m_to_idx(0.5) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_walkway(start_x, end_x, mid_y):
        height = np.random.uniform(0.1 * difficulty, 0.3 * difficulty)
        half_width = walkway_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_ramp(start_x, end_x, mid_y, direction):
        height = np.random.uniform(0.2 * difficulty, 0.45 * difficulty)
        half_width = m_to_idx(0.5) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slope = np.linspace(0, height, num=x2 - x1)[::direction]
        height_field[x1:x2, y1:y2] = slope[:, None]

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Set up the starting platform
    cur_x = spawn_length
    dx = np.random.randint(dx_min, dx_max)
    dy = np.random.randint(dy_min, dy_max)
    add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
    goals[1] = [cur_x + (platform_length + dx) // 2, mid_y + dy]
    cur_x += platform_length + dx + gap_length

    # Add a narrow walkway
    dx = np.random.randint(dx_min, dx_max)
    add_walkway(cur_x, cur_x + walkway_length + dx, mid_y)
    goals[2] = [cur_x + (walkway_length + dx) // 2, mid_y]
    cur_x += walkway_length + dx + gap_length

    # Add an alternating height ramp sequence
    for i in range(3, 6):
        dx = np.random.randint(dx_min, dx_max)
        ramp_dir = 1 if i % 2 == 0 else -1
        add_ramp(cur_x, cur_x + ramp_length + dx, mid_y, ramp_dir)
        goals[i] = [cur_x + (ramp_length + dx) // 2, mid_y]
        cur_x += ramp_length + dx + gap_length

    # Add final goal at the end
    goals[6] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

# INSERT TERRAIN FUNCTION DEFINITIONS HERE
