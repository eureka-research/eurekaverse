
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
    """Mixed obstacles including wide platforms, uneven stepping stones, and gentle slopes for agility and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform parameters
    platform_width = np.random.uniform(1.2, 1.8)
    platform_width = m_to_idx(platform_width)
    platform_length = 1.5 - 0.5 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_height_min, platform_height_max = 0.1 * difficulty, 0.3 * difficulty

    # Stepping stone parameters
    stepping_stone_size = 0.5
    stepping_stone_size = m_to_idx(stepping_stone_size)
    stepping_stone_height_min, stepping_stone_height_max = 0.05 * difficulty, 0.2 * difficulty

    # Slope parameters
    slope_width = platform_width
    slope_length = 1.5 - 0.5 * difficulty
    slope_length = m_to_idx(slope_length)
    slope_height_min, slope_height_max = 0.1 * difficulty, 0.25 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_stepping_stone(mid_x, mid_y, height):
        half_size = stepping_stone_size // 2
        x1, x2 = mid_x - half_size, mid_x + half_size
        y1, y2 = mid_y - half_size, mid_y + half_size
        height_field[x1:x2, y1:y2] = height

    def add_slope(start_x, end_x, mid_y, height):
        half_width = slope_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slope = np.linspace(0, height, num=x2-x1)[:, None]  # Creating gradual slope
        height_field[x1:x2, y1:y2] = slope

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # First goal at the end of the flat area
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    dx_min, dx_max = m_to_idx(-0.1), m_to_idx(0.1)
    dy_min, dy_max = m_to_idx(-0.4), m_to_idx(0.4)

    # Add first wide platform
    add_platform(cur_x, cur_x + platform_length, mid_y, np.random.uniform(platform_height_min, platform_height_max))
    goals[1] = [cur_x + platform_length // 2, mid_y]
    cur_x += platform_length + m_to_idx(0.5)

    # Add series of stepping stones
    for i in range(2, 6):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_stepping_stone(cur_x + dx, mid_y + dy, np.random.uniform(stepping_stone_height_min, stepping_stone_height_max))
        goals[i] = [cur_x + dx, mid_y + dy]
        cur_x += stepping_stone_size + m_to_idx(0.5)

    # Add final slope
    slope_height = np.random.uniform(slope_height_min, slope_height_max)
    add_slope(cur_x, cur_x + slope_length, mid_y, slope_height)
    goals[-2] = [cur_x + slope_length // 2, mid_y]
    cur_x += slope_length + m_to_idx(0.5)

    # Last goal at the end
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0  # Ensure no further obstacles

    return height_field, goals

def set_terrain_1(length, width, field_resolution, difficulty):
    """Challenging mix of narrow beams, staggered platforms, and angled ramps for testing balance and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up obstacle dimensions
    beam_length = 1.0 - 0.2 * difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = np.random.uniform(0.4, 0.5)  # Narrow beams
    beam_width = m_to_idx(beam_width)
    platform_length = 1.2 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.6, 0.7)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 * difficulty, 0.4 * difficulty
    ramp_height_min, ramp_height_max = 0.2 * difficulty, 0.5 * difficulty
    gap_length = 0.2 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, y_mid):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = y_mid - half_width, y_mid + half_width
        beam_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = beam_height

    def add_platform(start_x, end_x, y_mid):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = y_mid - half_width, y_mid + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_ramp(start_x, end_x, y_mid, height_start, height_end):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = y_mid - half_width, y_mid + half_width
        for x in range(x1, x2):
            height_field[x, y1:y2] = np.linspace(height_start, height_end, num=x2 - x1)[x - x1]

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Start the pattern of beam -> platform -> ramp
    cur_x = spawn_length
    for i in range(2):
        # Add a beam
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_beam(cur_x, cur_x + beam_length + dx, mid_y + dy)
        goals[i * 3 + 1] = [cur_x + (beam_length + dx) / 2, mid_y + dy]
        cur_x += beam_length + dx + gap_length
        
        # Add a platform
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
        goals[i * 3 + 2] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

        # Add a ramp
        height_start = np.random.uniform(ramp_height_min, ramp_height_max)
        height_end = np.random.uniform(ramp_height_min, ramp_height_max)
        add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, height_start, height_end)
        goals[i * 3 + 3] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

    # Add final goal behind the last obstacle
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_2(length, width, field_resolution, difficulty):
    """Alternating high and low platforms with variable gaps to challenge climbing and jumping skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    
    platform_length = 0.8 - 0.2 * difficulty  # Shorter to increase frequency of platforms
    platform_length = m_to_idx(platform_length)
    platform_width_min, platform_width_max = 0.8, 1.2
    gap_length_min, gap_length_max = 0.5 + 0.3 * difficulty, 1.0 + 0.6 * difficulty
    gap_length_min, gap_length_max = m_to_idx(gap_length_min), m_to_idx(gap_length_max)
    platform_height_min, platform_height_max = 0.2, 0.3 + 0.2 * difficulty  # Higher platforms

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        width = np.random.uniform(platform_width_min, platform_width_max)
        width = m_to_idx(width)
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length // 2, mid_y]
    
    cur_x = spawn_length
    platform_heights = [np.random.uniform(platform_height_min, platform_height_max) if i % 2 == 0 else 0 for i in range(8)]

    for i in range(7):  # Set up different types of platforms
        gap_length = np.random.randint(gap_length_min, gap_length_max)
        platform_end = cur_x + platform_length
        add_platform(cur_x, platform_end, mid_y, platform_heights[i])
        goals[i + 1] = [cur_x + platform_length // 2, mid_y]
        cur_x = platform_end + gap_length

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_3(length, width, field_resolution, difficulty):
    """Combination of staircases, ramps, and small gaps to test climbing and jumping skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform, staircase, and ramp dimensions
    platform_length = 1.0 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.2, 1.6)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.2 + 0.4 * difficulty
    
    ramp_length = 1.2 - 0.3 * difficulty
    ramp_length = m_to_idx(ramp_length)
    ramp_width = platform_width
    ramp_height = 0.2 + 0.4 * difficulty

    gap_length = 0.4 + 0.3 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_ramp(start_x, end_x, mid_y, direction):
        half_width = ramp_width // 2
        height = np.linspace(0, ramp_height, end_x - start_x)
        if direction == 'down':
            height = height[::-1]
        for i in range(mid_y - half_width, mid_y + half_width):
            height_field[start_x:end_x, i] = height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length

    # Create mixed obstacles
    for i in range(6):
        # Randomly decide the obstacle type
        obstacle_type = np.random.choice(['platform', 'ramp_up', 'ramp_down'])

        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        if obstacle_type == 'platform':
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
            cur_x += platform_length + dx + gap_length
        elif obstacle_type == 'ramp_up':
            add_ramp(cur_x, cur_x + ramp_length + dx, mid_y + dy, 'up')
            goals[i + 1] = [cur_x + (ramp_length + dx) / 2, mid_y + dy]
            cur_x += ramp_length + dx + gap_length
        elif obstacle_type == 'ramp_down':
            add_ramp(cur_x, cur_x + ramp_length + dx, mid_y + dy, 'down')
            goals[i + 1] = [cur_x + (ramp_length + dx) / 2, mid_y + dy]
            cur_x += ramp_length + dx + gap_length

    # Add final goal behind the last obstacle
    goals[7] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_4(length, width, field_resolution, difficulty):
    """Courses that combine narrow steps, long gaps, and complex slopes to test climbing, jumping, and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 1.0
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.2 + 0.25 * difficulty, 0.3 + 0.35 * difficulty
    gap_length = 0.4 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)
    slope_length = 1.0 + 0.5 * difficulty
    slope_length = m_to_idx(slope_length)

    mid_y = m_to_idx(width) // 2    

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_slope(start_x, mid_y, length, height, direction=1):
        half_width = platform_width // 2
        x1, x2 = start_x, start_x + length
        y1, y2 = mid_y - half_width, mid_y + half_width
        slope = np.linspace(0, height, x2 - x1)[::direction]
        slope = slope[:, None]
        height_field[x1:x2, y1:y2] += slope

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    # Sequence of Platforms
    for i in range(3):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        height = np.random.uniform(platform_height_min, platform_height_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, height)
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length
    
    # Slopes
    for i in range(3, 7):
        height = np.random.uniform(platform_height_min, platform_height_max)
        direction = np.random.choice([-1, 1])
        add_slope(cur_x, mid_y, slope_length, height, direction)
        goals[i+1] = [cur_x + slope_length // 2, mid_y]
        cur_x += slope_length + gap_length

    # Ending platform
    add_platform(cur_x, cur_x + platform_length, mid_y, 0)
    goals[-1] = [cur_x + platform_length / 2, mid_y]

    return height_field, goals

def set_terrain_5(length, width, field_resolution, difficulty):
    """Combination of platforms and ramps to traverse a pit for the robot to climb on and jump across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define dimensions and properties of platforms and ramps
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.2)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.2 * difficulty, 0.1 + 0.3 * difficulty
    gap_length = 0.2 + 0.5 * difficulty
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
        ramp_height = np.random.uniform(platform_height_min, platform_height_max)
        slant = np.linspace(0, ramp_height, num=x2-x1)
        slant = slant[::direction]
        slant = slant[:, None]  # Add a dimension for broadcasting to y
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy = m_to_idx(0.4)  # Consistent y offset

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Set remaining area to be a pit
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    for i in range(4):  # Set up 4 platforms
        dx = np.random.randint(dx_min, dx_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y)

        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y]

        cur_x += platform_length + dx + gap_length

    for i in range(4, 7):  # Set up 3 ramps
        dx = np.random.randint(dx_min, dx_max)
        direction = (-1) ** i  # Alternate left and right ramps
        add_ramp(cur_x, cur_x + platform_length + dx, mid_y, direction)

        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y]

        cur_x += platform_length + dx + gap_length
    
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_6(length, width, field_resolution, difficulty):
    """Angular platforms and tilted steps to challenge the robot's adaptability and agility."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and angular step dimensions
    platform_length = 1.2 - 0.4 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.2)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.3 * difficulty, 0.1 + 0.4 * difficulty
    step_height_min, step_height_max = 0.1 + 0.5 * difficulty, 0.2 + 0.6 * difficulty
    gap_length = 0.2 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_step(start_x, end_x, mid_y, direction):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        step_height = np.random.uniform(step_height_min, step_height_max)
        slant = np.linspace(0, step_height, num=y2-y1)[::direction]
        slant = slant[None, :]  # Add a dimension for broadcasting to x
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.05, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.0, 0.4  # Polarity of dy will alternate instead of being random
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Set remaining area to be a pit
    # We do this to force the robot to jump from platform to platform
    # Otherwise, the robot can just jump down and climb back up
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    for i in range(6):  # Set up 6 platforms and steps
        if i % 2 == 0:
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)

            # Put goal in the center of the platform
            goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        else:
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)
            direction = (-1) ** i  # Alternate left and right steps
            dy = dy * direction  # Alternate positive and negative y offsets
            add_step(cur_x, cur_x + platform_length + dx, mid_y + dy, direction)

            # Put goal in the center of the step
            goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        
        # Add gap
        cur_x += platform_length + dx + gap_length
    
    # Add final goal behind the last obstacle, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_7(length, width, field_resolution, difficulty):
    """Platforms of varied heights connected by narrow bridges, with gaps for jumping."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform dimensions
    platform_length = 1.0 - 0.3 * difficulty 
    platform_length = m_to_idx(platform_length)
    platform_width = 1.0
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1, 0.4 * difficulty

    # Bridge dimensions
    bridge_length = 1.2 - 0.2 * difficulty 
    bridge_length = m_to_idx(bridge_length)
    bridge_width = 0.4
    bridge_width = m_to_idx(bridge_width)
    bridge_height = -0.1  # Bridges may have some small descent/upward angle

    # Gap dimensions
    gap_length = 0.2 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_bridge(start_x, end_x, mid_y, height):
        half_width = bridge_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slant = np.linspace(height, height + bridge_height, x2 - x1)
        height_field[x1:x2, y1:y2] = slant[:, None]

    cur_x = m_to_idx(2)  # Ensure clearing the spawn area
    height_field[0:cur_x, :] = 0

    # First goal at spawn area
    goals[0] = [m_to_idx(1), mid_y]

    for i in range(4):
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)
        goals[i + 1] = [cur_x + platform_length // 2, mid_y]
        cur_x += platform_length + gap_length

        bridge_height = np.random.uniform(-0.2, 0.2)
        add_bridge(cur_x, cur_x + bridge_length, mid_y, bridge_height)
        goals[i + 1] = [cur_x + bridge_length // 2, mid_y]
        cur_x += bridge_length + gap_length

    # Final set of platforms and goal
    final_platform_height = np.random.uniform(platform_height_min, platform_height_max)
    add_platform(cur_x, cur_x + platform_length, mid_y, final_platform_height)
    goals[6] = [cur_x + platform_length // 2, mid_y]
    cur_x += platform_length + gap_length

    # Last goal after traversing platforms and bridges
    goals[7] = [cur_x + m_to_idx(1), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_8(length, width, field_resolution, difficulty):
    """Complex terrain with varied ramps and platforms to test advanced agility and precise movements."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and ramp dimensions
    platform_length = 0.8 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.5, 0.8)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.15 + 0.3 * difficulty
    ramp_height_min, ramp_height_max = 0.2 + 0.3 * difficulty, 0.25 + 0.4 * difficulty
    gap_length = 0.2 + 0.5 * difficulty
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

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.5, 0.5
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Add varied platforms and ramps, introduce complexity
    cur_x = spawn_length
    for i in range(6):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        obstacle_type = np.random.choice(['platform', 'ramp'])
        direction = np.random.choice([-1, 1])

        if obstacle_type == 'platform':
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        else:
            add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, direction)
            goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        
        # Add gap
        cur_x += platform_length + dx + gap_length
    
    # Add final goal behind the last obstacle, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_9(length, width, field_resolution, difficulty):
    """A challenging crisscross path with overlapping beams and platforms to promote agility, balance, and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define properties for beams and platforms
    beam_length = 0.6 + 0.4 * difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = 0.4 + 0.2 * difficulty
    beam_width = m_to_idx(beam_width)
    platform_length = 1.0 + 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 1.0 + 0.4 * difficulty
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.2 + 0.2 * difficulty, 0.4 + 0.2 * difficulty

    gap_length = 0.4 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, start_y, end_x, end_y):
        """Adds a beam to the terrain."""
        beam_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[start_x:end_x, start_y:end_y] = beam_height

    def add_platform(start_x, end_x, mid_y, height):
        """Adds a platform to the terrain."""
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    # Set up spawning area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Create a sequence of beams and platforms
    cur_x = spawn_length
    for i in range(1, 8):
        is_platform = i % 2 == 1  # Alternate between platforms and beams
        if is_platform:
            platform_height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)
            goals[i] = [cur_x + platform_length // 2, mid_y]
            cur_x += platform_length + gap_length
        else:
            add_beam(cur_x, mid_y - beam_width // 2, cur_x + beam_length, mid_y + beam_width // 2)
            goals[i] = [cur_x + beam_length // 2, mid_y]
            cur_x += beam_length + gap_length

    # Finalize terrain by leveling the rest to flat ground
    height_field[cur_x:, :] = 0

    return height_field, goals

# INSERT TERRAIN FUNCTION DEFINITIONS HERE
