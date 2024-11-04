
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
    """Obstacle course with varying height stepping stones for the quadruped to navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Terrain parameters
    step_length = np.random.uniform(0.4, 0.64)
    step_length = m_to_idx(step_length)
    step_width = np.random.uniform(0.8, 1.4)
    step_width = m_to_idx(step_width)
    step_height_min = 0.05 * difficulty
    step_height_max = 0.25 + 0.5 * difficulty
    gap_length = 0.2 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)
    
    mid_y = m_to_idx(width) // 2

    def add_step(start_x, end_x, mid_y):
        half_width = step_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        step_height = np.random.uniform(step_height_min, step_height_max)
        height_field[x1:x2, y1:y2] = step_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Add stepping stones
    cur_x = spawn_length
    for i in range(6):  # Create 6 stepping stones
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_step(cur_x, cur_x + step_length + dx, mid_y + dy)

        # Place goals at the center of each step
        goals[i+1] = [cur_x + (step_length + dx) / 2, mid_y + dy]

        # Add gap between stepping stones
        cur_x += step_length + dx + gap_length
    
    # Place last goal beyond the final step
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_1(length, width, field_resolution, difficulty):
    """Narrow ledges and flat platforms to test balancing and precise navigation skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Dimensions of the ledges and platforms
    ledge_width = 0.4 + 0.2 * difficulty  # Narrower ledges for higher difficulty
    ledge_width = m_to_idx(ledge_width)
    platform_width = 1.5
    platform_width = m_to_idx(platform_width)
    ledge_height_min, ledge_height_max = 0.1, 0.3 + 0.2 * difficulty
    platform_length = 1.0 + 0.5 * difficulty
    platform_length = m_to_idx(platform_length)
    gap_length = 0.5 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2
    spawn_length = m_to_idx(2)
    
    def add_ledge(start_x, end_x, mid_y):
        half_width = ledge_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ledge_height = np.random.uniform(ledge_height_min, ledge_height_max)
        height_field[x1:x2, y1:y2] = ledge_height

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = 0

    # Number of ledges and platforms
    num_obstacles = 5
    ledge_length = (m_to_idx(length) - spawn_length - (num_obstacles - 1) * (platform_length + gap_length)) // num_obstacles

    # Set spawn area to flat ground
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(num_obstacles):
        dx_min, dx_max = -0.1, 0.1
        dy_min, dy_max = -0.3, 0.3
        dx = np.random.randint(m_to_idx(dx_min), m_to_idx(dx_max))
        dy = np.random.randint(m_to_idx(dy_min), m_to_idx(dy_max))

        add_ledge(cur_x, cur_x + ledge_length, mid_y + dy)
        cur_x += ledge_length

        if i < num_obstacles - 1:
            add_platform(cur_x, cur_x + platform_length, mid_y + dy)
            goals[i+1] = [cur_x + platform_length // 2, mid_y + dy]
            cur_x += platform_length + gap_length

    # Final goal behind the last ledge
    height_field[cur_x:, :] = 0
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    return height_field, goals

def set_terrain_2(length, width, field_resolution, difficulty):
    """Stepping stones across water for the robot to navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Dimensions and properties of the stepping stones
    stone_length = 0.4 + 0.2 * (1 - difficulty)  # 0.4 to 0.6 meters, becoming larger as difficulty decreases
    stone_width = stone_length  # Square stepping stones
    stone_height_min = 0.1 + 0.1 * difficulty  # The height of the stones increases with difficulty
    stone_height_max = 0.15 + 0.15 * difficulty

    gap_length_min = 0.6 - 0.2 * difficulty  # Gap lengths vary based on difficulty
    gap_length_max = 0.8 - 0.2 * difficulty

    stone_length = m_to_idx(stone_length)
    stone_width = m_to_idx(stone_width)
    gap_length_min = m_to_idx(gap_length_min)
    gap_length_max = m_to_idx(gap_length_max)
    
    mid_y = m_to_idx(width) // 2

    def add_stone(center_x, center_y):
        half_length = stone_length // 2
        half_width = stone_width // 2
        x1, x2 = center_x - half_length, center_x + half_length
        y1, y2 = center_y - half_width, center_y + half_width
        stone_height = np.random.uniform(stone_height_min, stone_height_max)
        height_field[x1:x2, y1:y2] = stone_height

    # Set the initial flat area for spawning
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(6):  # Set up 6 stepping stones
        dy = np.random.randint(-m_to_idx(0.5), m_to_idx(0.5))  # Random y-offset for added complexity
        gap_length = np.random.randint(gap_length_min, gap_length_max)
        
        cur_x += gap_length
        add_stone(cur_x, mid_y + dy)
        goals[i + 1] = [cur_x, mid_y + dy]

    # Last segment is a flat area leading up to the final goal
    final_gap_length = m_to_idx(1.0)
    cur_x += final_gap_length
    height_field[cur_x:, :] = 0
    goals[7] = [cur_x + m_to_idx(0.5), mid_y]
    
    return height_field, goals

def set_terrain_3(length, width, field_resolution, difficulty):
    """Varied height platforms with alternating ramps and jumps for the robot to navigate and climb."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Parameters
    platform_length_base = 1.2 - 0.5 * difficulty
    platform_length = m_to_idx(platform_length_base)
    platform_width_min = 1.0
    platform_width_max = 1.2 + 0.5 * difficulty
    platform_width = m_to_idx(np.random.uniform(platform_width_min, platform_width_max))
    platform_height_range = (0.15 * difficulty, 0.4 * difficulty)
    gap_length_range = (0.2 * difficulty, 0.4 + 0.5 * difficulty)
    
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
        ramp_height = height
        slant = np.linspace(0, ramp_height, num=y2-y1)[::direction]
        slant = slant[None, :]  # Add a dimension for broadcasting to x
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.1, 0.15
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    direction = 1  # Alternating ramps
    for i in range(7):
        platform_height = np.random.uniform(*platform_height_range)
        dx = np.random.randint(dx_min, dx_max)
        dy = direction * np.random.randint(dy_min, dy_max)
        
        # Alternate between adding ramps and flat platforms
        if i % 2 == 0:
            add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, direction, platform_height)
        else:
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height)

        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Add gap between platforms
        gap_length = np.random.uniform(*gap_length_range)
        cur_x += platform_length + dx + m_to_idx(gap_length)

        # Alternate ramp direction
        direction *= -1
    
    # Add final goal after the last obstacle
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_4(length, width, field_resolution, difficulty):
    """Narrow platforms and varying heights requiring precise navigation and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and dimension characteristics
    platform_length = 0.8 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.6, 0.8)  # Narrower platforms
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 * difficulty, 0.4 * difficulty
    gap_length = 0.2 + 0.4 * difficulty
    gap_length = m_to_idx(gap_length)
    
    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, start_y, platform_height):
        y1, y2 = start_y, start_y + platform_width
        height_field[start_x:end_x, y1:y2] = platform_height

    # Starting flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]
    
    cur_x = spawn_length

    # Creating platforms
    for i in range(7):
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        
        # Introduce turning at intermediate goals
        if i % 2 == 0:
            dy = np.random.randint(-m_to_idx(1.0), m_to_idx(1.0))
        else:
            dy = 0

        add_platform(cur_x, cur_x + platform_length, mid_y + dy, platform_height)
        
        # Place goal in the middle of the platform
        goals[i + 1] = [cur_x + platform_length // 2, mid_y + dy + platform_width // 2]
        
        # Update cur_x for next platform, including the gap
        cur_x += platform_length + gap_length

    # Fill remaining space behind the last platform with flat ground
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_5(length, width, field_resolution, difficulty):
    """Higher platforms, angled ramps, and various gap sizes to challenge climbing, jumping, and balancing."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Parameters for obstacles
    platform_length = m_to_idx(1.0 - 0.3 * difficulty)
    platform_width = m_to_idx(np.random.uniform(1.0, 1.4))
    platform_height_range = (0.2 * difficulty, 0.5 * difficulty)
    ramp_height_range = (0.4 * difficulty, 0.6 * difficulty)
    wide_gap_length = m_to_idx(0.8 * difficulty)
    narrow_gap_length = m_to_idx(0.4)
    ramp_length = platform_length
    
    mid_y = m_to_idx(width) // 2  # Centerline in y-axis

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_ramp(start_x, end_x, mid_y, height, slope_up=True):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.linspace(0, height, num=x2-x1)
        if not slope_up:
            ramp_height = ramp_height[::-1]
        ramp_height = ramp_height[:, None]  # Add axis for broadcasting
        height_field[x1:x2, y1:y2] = ramp_height

    start_x = m_to_idx(2)
    height_field[:start_x, :] = 0  # Flat spawn area
    goals[0] = [start_x - m_to_idx(0.5), mid_y]  # First goal at the end of spawn area

    current_x = start_x
    for i in range(6):  # Creating 6 challenging segments

        # Add a platform
        platform_height = np.random.uniform(*platform_height_range)
        add_platform(current_x, current_x + platform_length, mid_y, platform_height)
        goals[i+1] = [current_x + platform_length // 2, mid_y]

        current_x += platform_length

        if i % 2 == 0:
            # Follow with a ramp
            ramp_height = np.random.uniform(*ramp_height_range)
            add_ramp(current_x, current_x + ramp_length, mid_y, ramp_height, slope_up=(i % 4 == 0))
            goals[i+2] = [current_x + ramp_length // 2, mid_y]
            current_x += ramp_length
        else:
            # Follow with a gap
            gap_length = wide_gap_length if i % 3 == 0 else narrow_gap_length
            goals[i+2] = [current_x + gap_length // 2, mid_y] if i < 5 else [current_x, mid_y]
            current_x += gap_length

    # Final goal, end after the last obstacle
    goals[-1] = [m_to_idx(length) - m_to_idx(0.5), mid_y]

    return height_field, goals

def set_terrain_6(length, width, field_resolution, difficulty):
    """Multiple platforms and sideways-facing ramps traversing pitfalls for climbing and agility."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and ramp dimensions
    platform_length = 1.2 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.9, 1.2)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 * difficulty, 0.4 * difficulty
    ramp_height_min, ramp_height_max = 0.2 * difficulty, 0.5 * difficulty
    gap_length = 0.2 + 0.6 * difficulty
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
        slant = np.linspace(0, ramp_height, num=y2-y1)[::direction]
        slant = slant[None, :]  # Add a dimension for broadcasting to x
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.05, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3  # Reduced range for better control
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Set remaining area to be a pit
    height_field[spawn_length:, :] = -1.0

    # Add first platform
    cur_x = spawn_length
    dx = np.random.randint(dx_min, dx_max)
    dy = np.random.randint(dy_min, dy_max)
    add_platform(cur_x, cur_x + platform_length, mid_y + dy)
    goals[1] = [cur_x + platform_length / 2, mid_y + dy]
    cur_x += platform_length + gap_length

    for i in range(1, 6):  # Set up alternating platforms and ramps
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        direction = (-1) ** i  # Alternate left and right ramps
        dy = dy * direction  # Alternate positive and negative y offsets

        if i % 2 == 0:  # Add a platform
            add_platform(cur_x, cur_x + platform_length, mid_y + dy)
        else:  # Add a ramp
            add_ramp(cur_x, cur_x + platform_length, mid_y + dy, direction)

        # Set goal in the center of the platform/ramp
        goals[i+1] = [cur_x + platform_length / 2, mid_y + dy]

        # Add gap
        cur_x += platform_length + dx + gap_length

    # Add final goal behind the last ramp, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_7(length, width, field_resolution, difficulty):
    """Series of varied-height platforms and ramps connected by gaps for climbing and jumping."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and ramp dimensions
    platform_length = 1.0 - 0.4 * difficulty    # More challenging with shorter platforms
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.5, 1.0)  # Narrower platforms to increase difficulty
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.3 * difficulty, 0.2 + 0.35 * difficulty
    gap_length = 0.2 + 0.6 * difficulty  # Slightly larger gaps
    gap_length = m_to_idx(gap_length)
    ramp_length = np.random.uniform(0.6, 1.2)
    ramp_length = m_to_idx(ramp_length)

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
        slant = np.linspace(0, ramp_height, num=x2-x1)[::direction]
        slant = slant[:, None]  # Add a dimension for broadcasting to y
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.1, 0.1  # Additional slight randomness to platform placement
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.2, 0.6  # Increased lateral movement for more dynamic challenge
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    for i in range(3):
        # Place platform
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)

        # Put goal in the center of the platform
        goals[i * 2 + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        cur_x += platform_length + dx + gap_length

        # Place ramp
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        direction = 1 if i % 2 == 0 else -1  # Alternate slope direction
        add_ramp(cur_x, cur_x + ramp_length + dx, mid_y + dy, direction)

        # Put goal in the middle of the ramp
        goals[i * 2 + 2] = [cur_x + (ramp_length + dx) / 2, mid_y + dy]

        cur_x += ramp_length + dx
        cur_x += gap_length
    
    # Add final goal behind the last structure
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_8(length, width, field_resolution, difficulty):
    """Elevated narrow pathways and low steps testing the quadruped's precision and balance."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]
    
    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    
    # Dimensions of narrow paths
    narrow_path_width = m_to_idx(0.4)  # Minimum width of path is 0.4 meters
    elevated_height_min, elevated_height_max = 0.05 + 0.15 * difficulty, 0.10 + 0.30 * difficulty  # Heights vary based on difficulty
    
    mid_y = m_to_idx(width // 2)
    terrain_length = m_to_idx(length)
    
    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    
    # Put the first goal at the spawn area
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]
    
    cur_x = spawn_length
    dy_min, dy_max = -0.2, 0.2  # Adding some randomness to the path's y-coordinate
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)
    
    for i in range(1, 8):
        path_length = m_to_idx(1.2 + 1.0 * difficulty)  # Path length increases with difficulty
        dx = np.random.randint(dy_min, dy_max)
        
        y1 = mid_y - (narrow_path_width // 2) + dx
        y2 = y1 + narrow_path_width
        path_height = np.random.uniform(elevated_height_min, elevated_height_max)
        
        if y1 < 0:
            y1, y2 = 0, narrow_path_width
        elif y2 >= height_field.shape[1]:
            y2 = height_field.shape[1]
            y1 = y2 - narrow_path_width
        
        height_field[cur_x:cur_x + path_length, y1:y2] = path_height
        
        # Place goal in the center of the path
        goals[i] = [cur_x + path_length // 2, mid_y + dx]
        
        # Move to the next starting point
        cur_x += path_length + m_to_idx(0.4)  # Adding small horizontal gaps between paths
    
    return height_field, goals

def set_terrain_9(length, width, field_resolution, difficulty):
    """Incline and decline traversal with varying steepness for the quadruped robot."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Constants
    ramp_length_base = 1.0  # Base length of each ramp in meters
    ramp_height_base = 0.1  # Base height of incline/decline in meters
    max_ramp_height_variation = 0.3 * difficulty  # Ramp height based on difficulty
    flat_length = 0.6  # Length of flat sections between ramps in meters

    ramp_length = m_to_idx(ramp_length_base)
    flat_length_idx = m_to_idx(flat_length)
    mid_y = m_to_idx(width) // 2  # Middle of the field's width

    def add_ramp(start_x, height_change):
        """Add an incline or decline to the height field."""
        end_x = start_x + ramp_length
        incline = np.linspace(0, height_change, ramp_length)
        height_field[start_x:end_x, :] += incline[:, np.newaxis]

    # Place the quadruped's spawn area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # Place the first goal at the end of the spawn area
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Initialize current x position
    cur_x = spawn_length

    for i in range(6):
        # Calculate the height change for the ramp
        height_change = ramp_height_base + np.random.uniform(0, max_ramp_height_variation)

        # Add incline ramp
        add_ramp(cur_x, height_change)
        cur_x += ramp_length
        
        # Add flat section
        height_field[cur_x:cur_x + flat_length_idx, :] += height_change
        cur_x += flat_length_idx

        goals[i+1] = [cur_x - flat_length_idx // 2, mid_y]

        # Add decline ramp
        add_ramp(cur_x, -height_change)
        cur_x += ramp_length
        
    # Place the final flat area and goal
    height_field[cur_x:, :] = 0
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    return height_field, goals

# INSERT TERRAIN FUNCTION DEFINITIONS HERE
