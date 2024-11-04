
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
        set_terrain_10,
        set_terrain_11,
        set_terrain_12,
        set_terrain_13,
        set_terrain_14,
        set_terrain_15,
        set_terrain_16,
        set_terrain_17,
        set_terrain_18,
        set_terrain_19,
        set_terrain_20,
        set_terrain_21,
        set_terrain_22,
        set_terrain_23,
        set_terrain_24,
        set_terrain_25,
        set_terrain_26,
        set_terrain_27,
        set_terrain_28,
        set_terrain_29,
        set_terrain_30,
        set_terrain_31,
        set_terrain_32,
        set_terrain_33,
        set_terrain_34,
        set_terrain_35,
        set_terrain_36,
        set_terrain_37,
        set_terrain_38,
        set_terrain_39,
        # INSERT TERRAIN FUNCTIONS HERE
    ]
    idx = int(variation * len(terrain_fns))
    height_field, goals = terrain_fns[idx](terrain.width * terrain.horizontal_scale, terrain.length * terrain.horizontal_scale, terrain.horizontal_scale, difficulty)
    terrain.height_field_raw = (height_field / terrain.vertical_scale).astype(np.int16)
    terrain.goals = goals
    return idx

def set_terrain_0(length, width, field_resolution, difficulty):
    """Staggered steps of varying heights for the robot to climb and traverse."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set the dimensions of the staggered steps
    step_length_base = 1.0  # Base length of each step in meters
    step_width_base = 1.2   # Base width of each step in meters
    
    step_length_variation = 0.3 * difficulty  # The more difficult, the more variation in length
    step_height_min, step_height_max = 0.15 * difficulty, 0.3 * difficulty

    step_length = m_to_idx(step_length_base - step_length_variation)
    step_width = m_to_idx(step_width_base)
    mid_y = m_to_idx(width) // 2

    def add_step(start_x, end_x, height, mid_y):
        half_width = step_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = -0.5, 0.5
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    for i in range(6):  # Set up 6 steps
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        step_height = np.random.uniform(step_height_min, step_height_max)
        add_step(cur_x, cur_x + step_length + dx, step_height, mid_y + dy)

        # Put goal in the center of the step
        goals[i+1] = [cur_x + (step_length + dx) / 2, mid_y + dy]

        # Prepare for the next step
        cur_x += step_length + dx
    
    # Add final goal behind the last step, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_1(length, width, field_resolution, difficulty):
    """Complex course with narrow beams, sideways-facing ramps, and platforms for balance, climbing, and navigation."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Course parameters
    beam_width = m_to_idx(0.4 - 0.2 * difficulty)
    platform_length = m_to_idx(1.0)
    gap_length = m_to_idx(0.5 + 0.3 * difficulty)
    ramp_length = m_to_idx(1.5 - 0.5 * difficulty)

    mid_y = m_to_idx(width / 2)

    def add_beam(start_x, end_x, mid_y):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = np.random.uniform(0.1 * difficulty, 0.4 * difficulty)

    def add_ramp(start_x, end_x, mid_y, direction):
        half_width = m_to_idx(0.5)
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(0.2, 0.6) * difficulty
        slant = np.linspace(0, ramp_height, num=end_x - start_x)[::direction]  # Create gradient
        height_field[x1:x2, y1:y2] = slant[:, None]

    def add_platform(start_x, end_x, mid_y):
        half_width = m_to_idx(0.6)
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = np.random.uniform(0.2 * difficulty, 0.5 * difficulty)

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    obstacle_types = [add_beam, add_ramp, add_platform]
    for i in range(7):
        obstacle = obstacle_types[i % 3]
        dx = np.random.randint(dx_min, dx_max)
        dy = (i % 2) * np.random.randint(dy_min, dy_max)  # Alternating y-offset roughly

        if obstacle == add_ramp:
            direction = 1 if i % 4 < 2 else -1  # Alternate ramp directions
            obstacle(cur_x, cur_x + ramp_length + dx, mid_y + dy, direction)
            goals[i+1] = [cur_x + m_to_idx(0.75) + dx // 2, mid_y + dy]
            cur_x += ramp_length + dx + gap_length
        else:
            obstacle(cur_x, cur_x + platform_length, mid_y + dy)
            goals[i+1] = [cur_x + platform_length // 2, mid_y + dy]
            cur_x += platform_length + gap_length

    goals[-1] = [cur_x - m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_2(length, width, field_resolution, difficulty):
    """Combines varied-height platforms, angled ramps, and small jumps to test balance, climbing, and jumping abilities."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Setup parameters for the platform and gap dimensions
    platform_length_min = 0.8 - 0.2 * difficulty
    platform_length_max = 1.2 - 0.1 * difficulty
    platform_width = np.random.uniform(0.4, 0.6)  # Narrower platforms
    platform_height_min, platform_height_max = 0.1 + 0.3 * difficulty, 0.2 + 0.4 * difficulty
    gap_length_min = 0.3 + 0.3 * difficulty
    gap_length_max = 0.5 + 0.5 * difficulty

    platform_length_min, platform_length_max = m_to_idx([platform_length_min, platform_length_max])
    platform_width = m_to_idx(platform_width)
    gap_length_min, gap_length_max = m_to_idx([gap_length_min, gap_length_max])
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
        slant = np.linspace(0, height, num=x2 - x1)[::direction]
        for i in range(y1, y2):
            height_field[x1:x2, i] = slant

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at the spawn point

    cur_x = spawn_length

    for i in range(5):  # We are going to set up 5 platforms and 2 angled ramps
        platform_length = np.random.randint(platform_length_min, platform_length_max)
        platform_height = np.random.uniform(platform_height_min, platform_height_max)

        # Create Platform
        add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)
        goals[i+1] = [cur_x + platform_length // 2, mid_y]

        # Add gap before the next platform
        cur_x += platform_length + np.random.randint(gap_length_min, gap_length_max)

    # Add ramps to increase complexity
    for i in range(5, 7):
        ramp_length = np.random.randint(platform_length_min, platform_length_max)
        ramp_height = np.random.uniform(platform_height_min, platform_height_max)

        # Alternating ramps
        direction = -1 if i % 2 == 0 else 1
        add_ramp(cur_x, cur_x + ramp_length, mid_y, ramp_height, direction)
        goals[i+1] = [cur_x + ramp_length // 2, mid_y]

        cur_x += ramp_length + np.random.randint(gap_length_min, gap_length_max)

    # Final goal just behind the last ramp/platform
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0  # Ensure flat ground after the last obstacle

    return height_field, goals

def set_terrain_3(length, width, field_resolution, difficulty):
    """Multiple elevated platforms and narrow bridges with variable heights and gaps to challenge the quadruped's agility, stability, and jumping abilities."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length_base = 1.0
    platform_length_variation = 0.2 * difficulty
    platform_length = m_to_idx(platform_length_base + platform_length_variation)

    platform_width_base = 1.0
    platform_width_variation = 0.2 * difficulty
    platform_width = m_to_idx(np.random.uniform(platform_width_base - platform_width_variation, platform_width_base + platform_width_variation))
    
    platform_height_min = 0.1 * difficulty
    platform_height_max = 0.4 * difficulty
    gap_length_base = 0.2
    gap_length_variation = 0.3 * difficulty
    gap_length = m_to_idx(gap_length_base + gap_length_variation)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_narrow_bridge(start_x, end_x, mid_y):
        narrow_width = m_to_idx(0.4 + 0.4 * difficulty)
        half_width = narrow_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        bridge_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = bridge_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_variation = m_to_idx(0.3)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Set remaining area to be a pit
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    for i in range(6):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(-dy_variation, dy_variation)

        # Alternate between platforms and narrow bridges
        if i % 2 == 0:
            platform_height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height)
            goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        else:
            add_narrow_bridge(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        cur_x += platform_length + dx + gap_length

    # Add final goal behind the last obstacle, fill in the remaining gap
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
    """Multiple elevated platforms and sideways ramps for the robot to climb, descend and jump across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and ramp dimensions
    platform_length_min = 0.8
    platform_length_max = 1.5
    platform_height_min = 0.1 + 0.2 * difficulty
    platform_height_max = 0.3 + 0.4 * difficulty
    ramp_length = 1.0
    ramp_height = 0.15 + 0.35 * difficulty

    platform_length_min = m_to_idx(platform_length_min)
    platform_length_max = m_to_idx(platform_length_max)
    ramp_length = m_to_idx(ramp_length)
    
    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = m_to_idx(1.2) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_ramp(start_x, end_x, mid_y):
        half_width = m_to_idx(1.0) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_slope = np.linspace(0, ramp_height, num=x2-x1)
        height_field[x1:x2, y1:y2] = ramp_slope[:, None]

    dx_min, dx_max = m_to_idx([-0.1, 0.2])
    dy_min, dy_max = m_to_idx([-0.4, 0.4])
    gap_min, gap_max = m_to_idx([0.2, 0.7])
    
    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    for i in range(3):
        dx, dy = np.random.randint(dx_min, dx_max), np.random.randint(dy_min, dy_max)
        gap = np.random.randint(gap_min, gap_max)

        # Add an elevated platform
        platform_length = np.random.randint(platform_length_min, platform_length_max)
        add_platform(cur_x, cur_x + platform_length, mid_y + dy)
        goals[i + 1] = [(cur_x + platform_length) / 2, mid_y + dy]  # Center of the platform
        cur_x += platform_length + gap

        # Add a sideways ramp
        dx, dy = np.random.randint(dx_min, dx_max), np.random.randint(dy_min, dy_max)
        add_ramp(cur_x, cur_x + ramp_length, mid_y + dy)
        goals[i + 4] = [cur_x + (ramp_length // 2), mid_y + dy]  # Center of the ramp
        cur_x += ramp_length + gap

    # Add a final goal behind the last ramp, filling in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_6(length, width, field_resolution, difficulty):
    """Ramps, narrow passages, and elevated platforms to simulate urban challenges."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    mid_y = m_to_idx(width) // 2

    # Set first goal at the spawn point
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Define ramp and passage parameters
    ramp_length = max(1.0, 1.5 - 0.5 * difficulty)  # Decrease ramp length with difficulty
    ramp_length = m_to_idx(ramp_length)
    ramp_height = np.linspace(0, 0.25 + 0.35 * difficulty, ramp_length)  # Incline increases with difficulty
    
    narrow_passage_width = np.random.uniform(0.4, 0.5) + difficulty * 0.3  # Make narrower with higher difficulty
    narrow_passage_width = m_to_idx(narrow_passage_width)

    # Platform parameters
    platform_height = 0.2 + 0.2 * difficulty
    platform_length = m_to_idx(1.0)
    platform_width = m_to_idx(1.0)

    def add_ramp(start_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, start_x + ramp_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = ramp_height[:, np.newaxis]

    def add_passage(start_x, mid_y):
        half_width = narrow_passage_width // 2
        x1, x2 = start_x, start_x + platform_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height_field[x1 - 1, y1]  # Continue from the previous height

    def add_platform(start_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, start_x + platform_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = platform_height

    # Initialize current x position just after spawn area
    cur_x = spawn_length

    # Add ramp
    add_ramp(cur_x, mid_y)
    goals[1] = [cur_x + ramp_length // 2, mid_y]  # Middle of the first ramp
    cur_x += ramp_length
    
    # Add passage
    add_passage(cur_x, mid_y)
    goals[2] = [cur_x + platform_length // 2, mid_y]  # Middle of the narrow passage
    cur_x += platform_length

    # Add platform
    add_platform(cur_x, mid_y)
    goals[3] = [cur_x + platform_length // 2, mid_y]  # Middle of the platform
    cur_x += platform_length

    for i in range(4, 8):
        if i % 2 == 0:
            # Alternate between ramp and platform
            add_ramp(cur_x, mid_y)
            goals[i] = [cur_x + ramp_length // 2, mid_y]
            cur_x += ramp_length
        else:
            add_platform(cur_x, mid_y)
            goals[i] = [cur_x + platform_length // 2, mid_y]
            cur_x += platform_length

    return height_field, goals

def set_terrain_7(length, width, field_resolution, difficulty):
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

def set_terrain_8(length, width, field_resolution, difficulty):
    """Series of staggered stairs for the quadruped to climb up and down."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Convert terrain dimensions to grid indices
    terrain_length = m_to_idx(length)
    terrain_width = m_to_idx(width)

    # Quadruped's center starting point
    start_x = m_to_idx(2)
    start_y = terrain_width // 2
    
    # Initial goal at start position
    goals[0] = [start_x - m_to_idx(0.5), start_y]

    # Define stair dimensions based on difficulty
    stair_width = 1.0 - 0.3 * difficulty  # decrease with difficulty
    stair_width = m_to_idx(stair_width)

    stair_height_min = 0.1 * difficulty  # increase with difficulty
    stair_height_max = 0.3 * difficulty  # increase with difficulty
    stair_length = 1.2  # fixed length of 1.2 meters
    stair_length = m_to_idx(stair_length)
    
    cur_x = start_x

    def add_stair(x, y, width, length, height):
        """Add a stair with given dimensions to the height_field."""
        half_width = width // 2
        x1, x2 = x, x + length
        y1, y2 = y - half_width, y + half_width
        height_field[x1:x2, y1:y2] += height

    for i in range(7):  # 7 sets of stairs
        stair_height = np.random.uniform(stair_height_min, stair_height_max)
        add_stair(cur_x, start_y, stair_width, stair_length, stair_height)

        # Place the goal in the center of the stair
        goals[i + 1] = [cur_x + stair_length // 2, start_y]

        # Move to the next stair position
        cur_x += stair_length

        # Adding a small gap with random width between stairs for added difficulty
        gap = np.random.uniform(0.1, 0.4) * difficulty
        gap = m_to_idx(gap)
        cur_x += gap

    # Final goal at the end of the terrain
    goals[-1] = [cur_x + m_to_idx(0.5), start_y]

    return height_field, goals

def set_terrain_9(length, width, field_resolution, difficulty):
    """Narrow bridges and elevated platforms to test balance and navigation at varying heights."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform and bridge sizes
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.2)
    platform_width = m_to_idx(platform_width)
    bridge_length_min, bridge_length_max = 2.0 - 0.8 * difficulty, 2.5 - 0.8 * difficulty
    bridge_length_min = m_to_idx(bridge_length_min)
    bridge_length_max = m_to_idx(bridge_length_max)
    bridge_width_min, bridge_width_max = 0.5, 0.6
    bridge_width_min = m_to_idx(bridge_width_min)
    bridge_width_max = m_to_idx(bridge_width_max)
    gap_length = 0.1 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)

    platform_height_min, platform_height_max = 0.2, 0.5 + 0.3 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_platform(center_x, center_y):
        half_length = platform_length // 2
        half_width = platform_width // 2
        x1, x2 = center_x - half_length, center_x + half_length
        y1, y2 = center_y - half_width, center_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height
    
    def add_bridge(start_x, end_x, center_y):
        half_width = random.randint(bridge_width_min, bridge_width_max) // 2
        x1, x2 = start_x, end_x
        y1, y2 = center_y - half_width, center_y + half_width
        bridge_height = random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = bridge_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    for i in range(6):  # Create 6 platforms and bridges
        # Add platform
        add_platform(cur_x + platform_length // 2, mid_y)
        goals[i] = [cur_x + platform_length // 2, mid_y]

        # Move x-coordinate ahead to place bridge
        cur_x += platform_length

        # Add a gap
        cur_x += gap_length

        # Add bridge
        bridge_length = random.randint(bridge_length_min, bridge_length_max)
        add_bridge(cur_x, cur_x + bridge_length, mid_y)
        
        # Move x-coordinate ahead to place next platform
        cur_x += bridge_length

        # Add another gap
        cur_x += gap_length
    
    # Add final platform
    add_platform(cur_x + platform_length // 2, mid_y)
    goals[6] = [cur_x + platform_length // 2, mid_y]

    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + platform_length + m_to_idx(0.5), mid_y]
    height_field[cur_x + platform_length:, :] = 0

    return height_field, goals

def set_terrain_10(length, width, field_resolution, difficulty):
    """Stepping stones and raised platforms for the robot to navigate, testing its jumping and balance skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and stepping stone dimensions
    stepping_stone_size = [0.4, 0.6]  # size range in meters
    stepping_stone_height = np.random.uniform(0.1, 0.3) + 0.2 * difficulty
    gap_length = 0.1 + 0.7 * difficulty

    platform_width = 1.0  # fixed width for larger platforms
    platform_width = m_to_idx(platform_width)
    platform_height = np.random.uniform(0.2, 0.4) + 0.2 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_stepping_stone(center_x, center_y, size, height):
        x, y = center_x - m_to_idx(size / 2), center_y - m_to_idx(size / 2)
        height_field[x: x + m_to_idx(size), y: y + m_to_idx(size)] = height

    def add_platform(start_x, start_y, width, height):
        x1, x2 = start_x, start_x + m_to_idx(1.0)
        y1, y2 = start_y - width // 2, start_y + width // 2
        height_field[x1:x2, y1:y2] = height

    # Add initial flat area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(4):  # Stepping stones section with 4 stones
        size = np.random.uniform(*stepping_stone_size)
        height = stepping_stone_height + np.random.uniform(-0.1, 0.1)
        add_stepping_stone(cur_x + m_to_idx(size / 2), mid_y, size, height)
        goals[i + 1] = [cur_x + m_to_idx(size / 2), mid_y]
        cur_x += m_to_idx(size + gap_length)

    # Add intermediate larger platform
    add_platform(cur_x, mid_y, platform_width, platform_height)
    goals[5] = [cur_x + m_to_idx(0.5), mid_y]
    cur_x += m_to_idx(1.0 + gap_length)

    for i in range(2):  # Another set of stepping stones
        size = np.random.uniform(*stepping_stone_size)
        height = stepping_stone_height + np.random.uniform(-0.1, 0.1)
        add_stepping_stone(cur_x + m_to_idx(size / 2), mid_y, size, height)
        goals[6 + i] = [cur_x + m_to_idx(size / 2), mid_y]
        cur_x += m_to_idx(size + gap_length)

    # Complete the terrain with a final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_11(length, width, field_resolution, difficulty):
    """Mixed terrain with platforms, stepping stones, and sloped surfaces to challenge various skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform and obstacle specifics
    platform_length = 0.8  # Fixed length of platforms
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.9, 1.2)  # Variable width for more complexity
    platform_width = m_to_idx(platform_width)

    # Heights and slopes based on difficulty
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.3 + 0.4 * difficulty
    slope_height = 0.2 + 0.4 * difficulty
    gap_length = 0.2 + 0.7 * difficulty  # Wider gaps for higher difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_slope(start_x, end_x, mid_y, height, direction):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slant = np.linspace(0, height, num=x2 - x1)[::direction]
        slant = slant[:, None]  # Add a dimension for broadcasting to y
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.0, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Set remaining area to a varied terrain
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length

    # First platform
    dx = np.random.randint(dx_min, dx_max)
    dy = np.random.randint(dy_min, dy_max) * (-1) ** np.random.randint(0, 2)
    platform_height = np.random.uniform(platform_height_min, platform_height_max)
    add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height)
    goals[1] = [cur_x + (platform_length + dx) // 2, mid_y + dy]
    cur_x += platform_length + dx + gap_length

    for i in range(5):  # Mixed obstacles
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max) * (-1) ** np.random.randint(0, 2)

        if i % 2 == 0:
            # Add platform
            platform_height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height)
            goals[i+2] = [cur_x + (platform_length + dx) // 2, mid_y + dy]
        else:
            # Add slope
            direction = (-1) ** np.random.randint(0, 2)
            add_slope(cur_x, cur_x + platform_length + dx, mid_y + dy, slope_height, direction)
            goals[i+2] = [cur_x + (platform_length + dx) // 2, mid_y + dy]

        cur_x += platform_length + dx + gap_length

    # Add final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_12(length, width, field_resolution, difficulty):
    """A complex course of platforms, ramps, and narrow beams for the quadruped to navigate and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]
    
    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    def add_platform(x_start, x_end, y_mid, height_min, height_max):
        y_half_width = m_to_idx(0.5)  # 1 meter wide platform
        platform_height = np.random.uniform(height_min, height_max)
        height_field[x_start:x_end, y_mid-y_half_width:y_mid+y_half_width] = platform_height

    def add_ramp(x_start, x_end, y_mid, height_min, height_max, slope_up):
        y_half_width = m_to_idx(0.5)  # 1 meter wide ramp
        ramp_height = np.random.uniform(height_min, height_max)
        slope = np.linspace(0, ramp_height, x_end-x_start) * (1 if slope_up else -1)
        slope = slope[:, None]
        height_field[x_start:x_end, y_mid-y_half_width:y_mid+y_half_width] = slope

    def add_beam(x_start, x_end, y_mid, beam_height):
        y_half_width = m_to_idx(0.2)  # 0.4 meter wide beam
        height_field[x_start:x_end, y_mid-y_half_width:y_mid+y_half_width] = beam_height

    def define_goal(x, y, index):
        goals[index] = [x, y]

    spawn_length = m_to_idx(2)
    mid_y = m_to_idx(width) // 2

    height_field[0:spawn_length, :] = 0  # Flat spawn area
    define_goal(spawn_length - m_to_idx(0.5), mid_y, 0)

    x_cursor = spawn_length
    height_min, height_max = 0.2 * difficulty, 0.5 * difficulty
    gap_min, gap_max = m_to_idx(0.2), m_to_idx(difficulty + 0.5)

    # First Platform
    platform_length = m_to_idx(1.5 + 0.3 * difficulty)
    add_platform(x_cursor, x_cursor + platform_length, mid_y, height_min, height_max)
    define_goal(x_cursor + platform_length // 2, mid_y, 1)
    x_cursor += platform_length + np.random.randint(gap_min, gap_max)
    
    # Second Beam
    beam_length = m_to_idx(1 + 0.5 * difficulty)
    add_beam(x_cursor, x_cursor + beam_length, mid_y, np.random.uniform(height_min, height_max))
    define_goal(x_cursor + beam_length // 2, mid_y, 2)
    x_cursor += beam_length + np.random.randint(gap_min, gap_max)
    
    # Third Ramp (up)
    ramp_length = m_to_idx(1.5 + 0.4 * difficulty)
    add_ramp(x_cursor, x_cursor + ramp_length, mid_y, height_min, height_max, slope_up=True)
    define_goal(x_cursor + ramp_length // 2, mid_y, 3)
    x_cursor += ramp_length + np.random.randint(gap_min, gap_max)

    # Fourth Platform
    add_platform(x_cursor, x_cursor + platform_length, mid_y, height_min, height_max)
    define_goal(x_cursor + platform_length // 2, mid_y, 4)
    x_cursor += platform_length + np.random.randint(gap_min, gap_max)
    
    # Fifth Ramp (down)
    add_ramp(x_cursor, x_cursor + ramp_length, mid_y, height_min, height_max, slope_up=False)
    define_goal(x_cursor + ramp_length // 2, mid_y, 5)
    x_cursor += ramp_length + np.random.randint(gap_min, gap_max)
    
    # Sixth Beam
    add_beam(x_cursor, x_cursor + beam_length, mid_y, np.random.uniform(height_min, height_max))
    define_goal(x_cursor + beam_length // 2, mid_y, 6)
    x_cursor += beam_length + np.random.randint(gap_min, gap_max)
    
    # Final Platform
    final_platform_length = m_to_idx(2)
    add_platform(x_cursor, x_cursor + final_platform_length, mid_y, height_min, height_max)
    define_goal(x_cursor + final_platform_length // 2, mid_y, 7)

    return height_field, goals

def set_terrain_13(length, width, field_resolution, difficulty):
    """Raised platforms combined with narrow beams and steep ramps to test agility, balance, and climbing abilities."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform, beam, and ramp dimensions
    platform_length = 1.0 - 0.1 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.5, 0.8)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.3 * difficulty, 0.6 * difficulty
    
    beam_length = 1.0 - 0.2 * difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = 0.2  # narrower width for the balance test
    beam_width = m_to_idx(beam_width)
    
    gap_length = 0.2 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)
    
    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_beam(start_x, end_x, mid_y):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        beam_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = beam_height

    def add_ramp(start_x, end_x, mid_y, direction):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(platform_height_min, platform_height_max)
        slant = np.linspace(0, ramp_height, num=y2 - y1)[::direction]
        slant = slant[None, :]
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)  
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Set first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    obstacles = [
        add_platform, add_beam, add_ramp, add_platform, add_beam, add_ramp, add_platform
    ]

    for i in range(6):
        obstacle_function = obstacles[i]
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        if obstacle_function == add_ramp:
            direction = (-1) ** i
            dy *= direction
            obstacle_function(cur_x, cur_x + platform_length + dx, mid_y + dy, direction)
        else:
            obstacle_function(cur_x, cur_x + platform_length + dx, mid_y + dy)

        goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

    goals[-1] = [cur_x + 0.5, mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_14(length, width, field_resolution, difficulty):
    """Staggered platforms and moderate gaps for balance, climbing, and precision movements."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Dimensions setup
    platform_length = 1.0 - 0.4 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.2)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 * difficulty, 0.3 * difficulty
    gap_length = 0.2 + 0.4 * difficulty
    gap_length = m_to_idx(gap_length)
    
    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = 0.0, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    current_height = 0
    
    for i in range(7):  # Create 7 platforms with varying heights and positions
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        # Vary the height for added difficulty and realism
        current_height = np.random.uniform(platform_height_min, platform_height_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, current_height)
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        
        cur_x += platform_length + dx + gap_length
    
    # Final goal placed beyond the last platform
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_15(length, width, field_resolution, difficulty):
    """Combination of narrow and wide platforms with slight elevation changes for the robot to balance, climb, and navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Dimensions of platforms and gaps
    base_platform_length = 1.2 - 0.2 * difficulty
    base_platform_width = np.random.uniform(0.6, 1.2)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.25 + 0.3 * difficulty
    base_gap_length = 0.5 + 0.5 * difficulty
    base_gap_length = m_to_idx(base_gap_length)

    def add_platform(start_x, end_x, mid_y, width, height):
        half_width = m_to_idx(width) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    mid_y = m_to_idx(width) // 2

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at spawn

    last_x = spawn_length
    for i in range(1, 8):
        platform_length = m_to_idx(base_platform_length + 0.1 * difficulty * (i % 2))
        platform_width = m_to_idx(base_platform_width + 0.3 * difficulty * (i % 2))
        platform_height = np.random.uniform(platform_height_min, platform_height_max)

        if i % 2 == 0:
            current_gap_length = int(base_gap_length * 0.7)
        else:
            current_gap_length = base_gap_length

        start_x = last_x + current_gap_length
        end_x = start_x + platform_length
        dy = np.random.randint(-m_to_idx(0.2), m_to_idx(0.2))
        mid_platform_y = mid_y + dy

        add_platform(start_x, end_x, mid_platform_y, platform_width, platform_height)

        goals[i] = [start_x + (platform_length) / 2, mid_platform_y]

        last_x = end_x

    return height_field, goals

def set_terrain_16(length, width, field_resolution, difficulty):
    """Varying-height steps and platforms for the robot to navigate and step over."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Setup platform dimensions
    platform_length_base = 0.8  # Base length of platform
    platform_length_variation = 0.3 * difficulty
    platform_width = np.random.uniform(0.8, 1.2)  # Narrower and slightly varied platform width
    platform_width = m_to_idx(platform_width)
    step_height_min, step_height_max = 0.05 * difficulty, 0.3 * difficulty
    gap_length_base = 0.2
    gap_length_variation = 0.5 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2  # Reduced polarity variation in y direction for a consistent path
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Add platforms and steps
    cur_x = spawn_length
    heights = [0.0]

    for i in range(7):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        platform_length = platform_length_base + (platform_length_variation * np.random.rand())
        platform_length = m_to_idx(platform_length)
        gap_length = gap_length_base + (gap_length_variation * np.random.rand())
        gap_length = m_to_idx(gap_length)

        step_height = np.random.uniform(step_height_min, step_height_max) * (-1 if i % 2 == 0 else 1)
        heights.append(heights[-1] + step_height)

        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, heights[-1])

        # Set goal in the center of the platform
        goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += platform_length + dx + gap_length

    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_17(length, width, field_resolution, difficulty):
    """Elevated platforms with narrow beams and gaps to test dexterity and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up obstacle dimensions
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)

    platform_width = np.random.uniform(0.8, 1.0)  # Narrower platforms
    platform_width = m_to_idx(platform_width)

    platform_height_min, platform_height_max = 0.2 + 0.3 * difficulty, 0.5 + 0.3 * difficulty
    gap_length = 0.5 + 0.7 * difficulty
    gap_length = m_to_idx(gap_length)

    beam_width = 0.2 + 0.2 * difficulty  # Narrow beams with increasing difficulty
    beam_width = m_to_idx(beam_width)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, start_y, end_y, height):
        height_field[start_x:end_x, start_y:end_y] = height

    cur_x = m_to_idx(2)
    height_field[0:cur_x, :] = 0  # Set spawn area to flat ground
    n_obstacles = 6

    # Initial goal at spawn area
    goals[0] = [cur_x - m_to_idx(0.5), mid_y]

    for i in range(n_obstacles):
        height = np.random.uniform(platform_height_min, platform_height_max)

        if i % 2 == 0:  # Add platforms
            end_x = cur_x + platform_length
            add_platform(cur_x, end_x, mid_y - platform_width // 2, mid_y + platform_width // 2, height)
            goals[i + 1] = [cur_x + platform_length // 2, mid_y]
            cur_x = end_x + gap_length

        else:  # Add narrow beams
            end_x = cur_x + platform_length
            add_platform(cur_x, end_x, mid_y - beam_width // 2, mid_y + beam_width // 2, height)
            goals[i + 1] = [cur_x + platform_length // 2, mid_y]
            cur_x = end_x + gap_length

    # Final goal position
    goals[-1] = [cur_x + m_to_idx(1), mid_y]

    return height_field, goals


def set_terrain_18(length, width, field_resolution, difficulty):
    """Narrow paths and elevated platforms with small gaps for precise navigation and controlled jumps."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Path and platform dimensions
    path_length = 1.0 - 0.3 * difficulty
    platform_length = 1.0 - 0.2 * difficulty
    path_length, platform_length = m_to_idx(path_length), m_to_idx(platform_length)
    path_width = 0.4 + 0.2 * difficulty
    path_width, platform_width = m_to_idx(path_width), m_to_idx(1.6 - 0.6 * difficulty)
    max_height = 0.3 + 0.3 * difficulty
    gap_max = 0.2 + 0.4 * difficulty
    mid_y = m_to_idx(width) // 2

    def add_path(start_x, end_x, center_y, width, height):
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = center_y - half_width, center_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_platform(start_x, end_x, center_y, width, height):
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = center_y - half_width, center_y + half_width
        height_field[x1:x2, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # Initial goal at spawn point
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    last_height = 0

    for i in range(1, 7):
        if i % 2 == 0:
            gap = np.random.uniform(0.1, gap_max)
            gap = m_to_idx(gap)
            next_height = np.random.uniform(last_height, max_height)
            add_platform(cur_x + gap, cur_x + gap + platform_length, mid_y, platform_width, next_height)
            goals[i] = [cur_x + gap + platform_length // 2, mid_y]
            cur_x += gap + platform_length
        else:
            next_height = np.random.uniform(last_height, max_height)
            add_path(cur_x, cur_x + path_length, mid_y, path_width, next_height)
            goals[i] = [cur_x + path_length // 2, mid_y]
            cur_x += path_length

        last_height = next_height

    # Set final goal behind the last platform
    goals[7] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_19(length, width, field_resolution, difficulty):
    """Mixed challenges with higher platforms, narrow beams, and varied gap jumps."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define properties of platforms and beams
    platform_length = 0.7 + 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 0.5 + 0.2 * difficulty
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.2 * difficulty, 0.5 + 0.3 * difficulty
    beam_length = 0.6 + 0.2 * difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = 0.2 + 0.1 * difficulty
    beam_width = m_to_idx(beam_width)
    gap_length_min, gap_length_max = 0.2 + 0.3 * difficulty, 0.5 + 0.5 * difficulty
    gap_length_min, gap_length_max = m_to_idx(gap_length_min), m_to_idx(gap_length_max)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, start_y, end_x, end_y):
        """Adds a platform to the terrain."""
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[start_x:end_x, start_y:end_y] = platform_height

    def add_beam(start_x, start_y, end_x, end_y, height):
        """Adds a narrow beam to the terrain."""
        height_field[start_x:end_x, start_y:end_y] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x, cur_y = spawn_length, mid_y - platform_width // 2

    # Create series of platforms and beams with varied gaps
    for i in range(1, 8):
        if i % 2 == 1:  # Add platform
            dx = np.random.randint(0, m_to_idx(0.2))
            dy = np.random.randint(-m_to_idx(0.4), m_to_idx(0.4))
            add_platform(cur_x + dx, cur_y + dy, cur_x + platform_length + dx, cur_y + platform_width + dy)
            goals[i] = [cur_x + platform_length // 2 + dx, cur_y + platform_width // 2 + dy]
            cur_x += platform_length + dx + np.random.randint(gap_length_min, gap_length_max)
        else:  # Add narrow beam
            height = np.random.uniform(0.1, 0.2)
            dx = np.random.randint(0, m_to_idx(0.2))
            dy = np.random.randint(-m_to_idx(0.2), m_to_idx(0.2))
            add_beam(cur_x + dx, cur_y + dy, cur_x + beam_length + dx, cur_y + beam_width + dy, height)
            goals[i] = [cur_x + beam_length // 2 + dx, cur_y + beam_width // 2 + dy]
            cur_x += beam_length + dx + np.random.randint(gap_length_min, gap_length_max)
            
    # Final goal after the last obstacle
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_20(length, width, field_resolution, difficulty):
    """Platforms and ramps with variable heights for the robot to navigate, focusing on balance and careful navigation."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and ramp dimensions
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.5)  # Maintain variable widths for platforms
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.2 * difficulty, 0.5 * difficulty
    ramp_height_min, ramp_height_max = 0.2 * difficulty, 0.5 * difficulty
    gap_length = 0.1 + 0.5 * difficulty  # Moderate gap lengths
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

    dx_min, dx_max = m_to_idx(-0.1), m_to_idx(0.1)
    dy_min, dy_max = m_to_idx(0.0), m_to_idx(0.4)  # Polarity of dy will alternate instead of being random

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Set remaining area to be a pit to force platform and ramp traversal
    height_field[spawn_length:, :] = -1.0

    # Add first platform
    cur_x = spawn_length
    dx = np.random.randint(dx_min, dx_max)
    dy = np.random.randint(dy_min, dy_max)
    add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
    goals[1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
    cur_x += platform_length + dx + gap_length

    for i in range(1, 6):  # Set up 5 ramps
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        direction = (-1) ** i  # Alternate left and right ramps
        dy = dy * direction  # Alternate positive and negative y offsets
        add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, direction)

        # Put goal in the center of the ramp
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += platform_length + dx + gap_length
    
    # Add final goal behind the last ramp, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_21(length, width, field_resolution, difficulty):
    """Complex mixed terrain with narrow beams, stepping stones, and varying height platforms."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    def add_narrow_beam(start_x, mid_y, length, width, height):
        """Add a narrow beam to the height field."""
        half_width = width // 2
        x1, x2 = start_x, start_x + length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_stepping_stones(start_x, end_x, mid_y, num_stones, stone_size, stone_height):
        """Add multiple stepping stones to the height field."""
        stone_gap = (end_x - start_x) // num_stones
        for i in range(num_stones):
            stone_x1 = start_x + i * stone_gap
            stone_x2 = stone_x1 + stone_size
            height_field[stone_x1:stone_x2, mid_y - stone_size//2:mid_y + stone_size//2] = stone_height

    def add_platform(start_x, mid_y, length, width, height):
        """Add a platform to the height field."""
        half_width = width // 2
        x1, x2 = start_x, start_x + length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    # Dimensions
    narrow_beam_length, narrow_beam_width = m_to_idx(1.5 - 0.5 * difficulty), m_to_idx(0.45)
    narrow_beam_height = 0.1 + 0.15 * difficulty
    stepping_stone_size, stepping_stone_height = m_to_idx(0.6), 0.2 + 0.15 * difficulty
    gap_length = m_to_idx(0.4 + 0.6 * difficulty)
    platform_length, platform_width = m_to_idx(1.0), m_to_idx(1.2)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.3 + 0.3 * difficulty

    mid_y = m_to_idx(width) // 2
    cur_x = m_to_idx(2)

    # Set spawn area to flat ground
    height_field[0:cur_x, :] = 0
    goals[0] = [cur_x - m_to_idx(0.5), mid_y]

    # Add a sequence of narrow beams, stepping stones, and platforms
    even_goal_distrib = np.linspace(1, 6, num=6, endpoint=True, dtype=np.int16)

    for i, rel_goal in enumerate(even_goal_distrib):
        if i % 3 == 0:
            add_narrow_beam(cur_x, mid_y, narrow_beam_length, narrow_beam_width, narrow_beam_height)
            goals[rel_goal] = [cur_x + narrow_beam_length / 2, mid_y]
            cur_x += narrow_beam_length + gap_length
        elif i % 3 == 1:
            add_stepping_stones(cur_x, cur_x + platform_length, mid_y, 5, stepping_stone_size, stepping_stone_height)
            goals[rel_goal] = [cur_x + platform_length / 2, mid_y]
            cur_x += platform_length + gap_length
        else:
            platform_height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, mid_y, platform_length, platform_width, platform_height)
            goals[rel_goal] = [cur_x + platform_length / 2, mid_y]
            cur_x += platform_length + gap_length

    # Place the final goal safely beyond the last obstacle
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    # Ensure the last few meters are flat ground
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_22(length, width, field_resolution, difficulty):
    """Combines inclined ramps, high platforms with steps, narrow beams, and variable terrain heights for increased difficulty."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Convert parameters to index space
    platform_length = m_to_idx(2.0 - 0.3 * difficulty)
    platform_width = m_to_idx(0.8 * (1.0 - difficulty))
    platform_height_range = (0.2 * difficulty, 0.4 * difficulty)
    ramp_length = m_to_idx(0.7 + 0.2 * difficulty)
    beam_width = m_to_idx(0.35 - 0.15 * difficulty)
    gap_length = m_to_idx(0.3 + 0.5 * difficulty)
    spawn_length = m_to_idx(2)
    mid_y = m_to_idx(width) // 2

    def add_inclined_ramp(start_x, end_x, mid_y, height, direction):
        delta_height = np.linspace(0, height, end_x - start_x)
        if direction == "down":
            delta_height = delta_height[::-1]
        height_field[start_x:end_x, mid_y - platform_width // 2:mid_y + platform_width // 2] = delta_height[:, np.newaxis]

    def add_platform(start_x, end_x, mid_y, height):
        height_field[start_x:end_x, mid_y - platform_width // 2:mid_y + platform_width // 2] = height

    def add_narrow_beam(start_x, end_x, mid_y):
        height_field[start_x:end_x, mid_y - beam_width // 2:mid_y + beam_width // 2] = platform_height_range[1]

    # Set flat spawn area
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]
    cur_x = spawn_length

    # Add inclined ramp
    ramp_height = np.random.uniform(*platform_height_range)
    add_inclined_ramp(cur_x, cur_x + ramp_length, mid_y, ramp_height, direction="up")
    goals[1] = [cur_x + ramp_length // 2, mid_y]
    cur_x += ramp_length + gap_length

    # Add high platforms with steps
    for step in range(2):
        platform_height = np.random.uniform(*platform_height_range)
        add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)
        goals[2 + step] = [cur_x + platform_length // 2, mid_y]
        cur_x += platform_length + gap_length

    # Add narrow beam navigation
    add_narrow_beam(cur_x, cur_x + platform_length, mid_y)
    goals[4] = [cur_x + platform_length // 2, mid_y]
    cur_x += platform_length + gap_length

    # Add variable terrain heights
    for i in range(2):
        height = np.random.uniform(*platform_height_range)
        add_platform(cur_x, cur_x + platform_length, mid_y, height)
        goals[5 + i] = [cur_x + platform_length // 2, mid_y]
        cur_x += platform_length + gap_length

    # Add final goal after last platform
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_23(length, width, field_resolution, difficulty):
    """Obstacle course with varied platforms and thin beams for balance and navigation challenges."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if isinstance(m, (int, float)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Dimensions and height ranges of platforms and beams
    basic_height_min, basic_height_max = 0.1 + 0.2 * difficulty, 0.3 + 0.4 * difficulty
    beam_width = np.random.uniform(0.4, 0.5)  # Narrower beams for greater difficulty
    beam_width = m_to_idx(beam_width)
    platform_length = 0.8 + 0.4 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width_range = [1.0, 1.4]
    gap_length_range = [0.2, 0.7]
    
    mid_y = m_to_idx(width) // 2

    def add_platform(x_start, length, height, mid_y):
        """Creates a rectangular platform at provided location."""
        width = np.random.uniform(*platform_width_range)
        width = m_to_idx(width)
        x_end = x_start + length
        half_width = width // 2
        height_field[x_start:x_end, mid_y - half_width:mid_y + half_width] = height

    def add_beam(x_start, length, height, mid_y, shift=0):
        """Creates a thin beam for balance challenge."""
        x_end = x_start + length
        y_start = mid_y - beam_width // 2 + shift
        y_end = mid_y + beam_width // 2 + shift
        height_field[x_start:x_end, y_start:y_end] = height

    # Set flat ground for spawning area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(1), mid_y]

    cur_x = spawn_length
    cur_y_shift = 0

    for i in range(7):
        platform_height = np.random.uniform(basic_height_min, basic_height_max)
        gap_length = np.random.uniform(*gap_length_range)
        gap_length = m_to_idx(gap_length)

        if i % 2 == 0:  # Even indices -> platform
            add_platform(cur_x, platform_length, platform_height, mid_y + cur_y_shift)
            goals[i+1] = [cur_x + platform_length / 2, mid_y + cur_y_shift]
            cur_x += platform_length + gap_length
        else:  # Odd indices -> beam
            add_beam(cur_x, platform_length, platform_height, mid_y, shift=cur_y_shift)
            goals[i+1] = [cur_x + platform_length / 2, mid_y + cur_y_shift]
            cur_x += platform_length + gap_length
        
        # Alternate y-shift to promote diverse navigation
        cur_y_shift = (-1) ** i * np.random.randint(0, m_to_idx(0.4))
    
    goals[-1] = [cur_x + m_to_idx(1), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_24(length, width, field_resolution, difficulty):
    """Staggered narrow beams with changing heights to test balance and precise movement."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Beam dimensions
    beam_length = 0.9 + 0.1 * difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = 0.4 + 0.04 * difficulty
    beam_width = m_to_idx(beam_width)
    min_height = 0.1 * difficulty
    max_height = 0.5 * difficulty
    beam_gap = 0.1 * difficulty
    beam_gap = m_to_idx(beam_gap)
    
    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, y, height):
        x1, x2 = start_x, end_x
        y1, y2 = y - beam_width // 2, y + beam_width // 2
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = -0.1, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(6):  # Place 6 beams
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        height = np.random.uniform(min_height, max_height)
        add_beam(cur_x, cur_x + beam_length + dx, mid_y + dy, height)

        # Place goal in the center of the beam
        goals[i+1] = [cur_x + (beam_length + dx) / 2, mid_y + dy]

        # Add gap after beam
        cur_x += beam_length + dx + beam_gap
    
    # Place the final goal at the end
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_25(length, width, field_resolution, difficulty):
    """Series of narrow beams for the robot to carefully navigate across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up beam dimensions
    beam_length = 2.0 - difficulty  # Beams get shorter with higher difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = 0.4 + 0.2 * difficulty  # The width of the beams, keeping it between 0.4m and 0.6m
    beam_width = m_to_idx(beam_width)
    beam_height = 0.2 + 0.3 * difficulty  # The height of the beams, increasing with difficulty
    gap_length = 0.4 + 0.6 * difficulty  # Gaps between beams

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, mid_y):
        y_half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - y_half_width, mid_y + y_half_width
        height_field[x1:x2, y1:y2] = beam_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(6):  # Set up 6 beams
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_beam(cur_x, cur_x + beam_length + dx, mid_y + dy)

        # Put goal in the center of the beam
        goals[i+1] = [cur_x + (beam_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += beam_length + dx + m_to_idx(gap_length)

    # Add final goal behind the last beam, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_26(length, width, field_resolution, difficulty):
    """Mixed terrains with varying heights, slopes, and narrow passages for complex navigation"""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set platform dimensions
    platform_length = 1.5 - 0.4 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.4)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.2 * difficulty, 0.4 * difficulty
    pit_depth = -1.0  # Depth of the pits between platforms
    gap_length = 0.2 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_slope(start_x, end_x, mid_y, height_start, height_end):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slope = np.linspace(height_start, height_end, x2-x1)
        slope = slope[:, None]  # Add an axis to broadcast to the y-dimension
        height_field[x1:x2, y1:y2] = slope

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length

    # Add steps and platforms
    for i in range(3):
        # Random platform height and gap between obstacles
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        dx = np.random.randint(-m_to_idx(0.1), m_to_idx(0.1))
        dy = np.random.randint(-m_to_idx(0.3), m_to_idx(0.3))
        
        # Add platform
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height)
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += platform_length + dx + gap_length

        # After every 2 platforms, add a slope
        if i % 2 == 1:
            slope_end_height = np.random.uniform(platform_height_max, platform_height_max + 0.15 * difficulty)
            add_slope(cur_x - gap_length, cur_x, mid_y + dy, 0.0, slope_end_height)

    # Transition to alternating steps
    for i in range(3):
        platform_height = np.random.uniform(platform_height_min + 0.1, platform_height_max + 0.2)
        dx = np.random.randint(-m_to_idx(0.1), m_to_idx(0.1))
        dy = np.random.randint(-m_to_idx(0.3), m_to_idx(0.3))

        # Add step up
        add_platform(cur_x, cur_x + m_to_idx(0.5) + dx, mid_y - dy, platform_height)
        goals[i+4] = [cur_x + (m_to_idx(0.25) + dx) / 2, mid_y - dy]

        cur_x += m_to_idx(0.5) + dx + gap_length

        # Add step down
        add_platform(cur_x, cur_x + m_to_idx(0.5) + dx, mid_y + dy, -platform_height)
        cur_x += m_to_idx(0.5) + dx + gap_length

    # Add final goal at the end of the course
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0  # Ensure the final surface is flat

    return height_field, goals

def set_terrain_27(length, width, field_resolution, difficulty):
    """Series of narrow beams aligned with gaps in between for the robot to balance and traverse."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up beam and gap sizes based on difficulty
    beam_width_min, beam_width_max = 0.4 - 0.2 * difficulty, 0.8 - 0.3 * difficulty
    beam_width = np.random.uniform(beam_width_min, beam_width_max)
    beam_width = m_to_idx(beam_width)
    beam_height = 0.3 + 0.5 * difficulty
    gap_width = 0.2 + 0.6 * difficulty
    gap_width = m_to_idx(gap_width)

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, beam_width, mid_y):
        half_width = beam_width // 2
        x1 = start_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x1 + beam_width, y1:y2] = beam_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    for i in range(6):  # Set up 6 beams
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_beam(cur_x, beam_width + dx, mid_y + dy)

        # Put goal at the endpoint of each beam
        goals[i+1] = [cur_x + (beam_width + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += beam_width + dx + gap_width
    
    # Add final goal behind the last beam, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_28(length, width, field_resolution, difficulty):
    """Narrow bridges and sharp turns for the robot to navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Basic obstacle sizes and properties
    bridge_width = max(0.4, 0.8 * (1 - difficulty))  # Bridge width decreases with difficulty
    bridge_width = m_to_idx(bridge_width)
    bridge_length_min = 2.0
    bridge_length_max = 3.0
    bridge_length_min = m_to_idx(bridge_length_min)
    bridge_length_max = m_to_idx(bridge_length_max)
    bridge_height = 0.05 + 0.25 * difficulty  # Increase height with difficulty
    pit_depth = -1.0  # Depth of the pit around bridges
  
    spawn_x_idx = m_to_idx(2)
    height_field[0:spawn_x_idx, :] = 0  # Spawn area flat ground
    mid_y_idx = m_to_idx(width / 2)

    # Set the initial goal at spawn area
    goals[0] = [spawn_x_idx - m_to_idx(0.5), mid_y_idx]

    def add_bridge(start_x_idx, start_y_idx, length):
        half_width = bridge_width // 2
        x1, x2 = start_x_idx, start_x_idx + length
        y1, y2 = start_y_idx - half_width, start_y_idx + half_width
        height_field[x1:x2, y1:y2] = bridge_height

    cur_x = spawn_x_idx

    for i in range(7):  # Set up 7 bridges
        bridge_length = np.random.randint(bridge_length_min, bridge_length_max)
        offset_y = np.random.uniform(-1.0, 1.0)
        offset_y = m_to_idx(offset_y)
        
        add_bridge(cur_x, mid_y_idx + offset_y, bridge_length)
        goals[i+1] = [cur_x + bridge_length // 2, mid_y_idx + offset_y]  # Goal in the center of the bridge

        # Add space (pit) before the next bridge
        pit_length = np.random.uniform(0.4, 0.6)
        pit_length = m_to_idx(pit_length)
        cur_x += bridge_length + pit_length

    # Fill in the remaining area after the last bridge with flat ground
    height_field[cur_x:, :] = 0
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y_idx]  # Final goal just after last bridge

    return height_field, goals

def set_terrain_29(length, width, field_resolution, difficulty):
    """Combination of narrow beams and raised platforms for an increased challenge."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Parameters for raised platforms and beams
    platform_length = 1.0 - 0.4 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width_min = 0.6  # Narrower platforms
    platform_width_max = 1.0
    platform_width_min = m_to_idx(platform_width_min)
    platform_width_max = m_to_idx(platform_width_max)

    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.15 + 0.25 * difficulty
    beam_width = 0.4  # Fixed narrow beam width
    beam_width = m_to_idx(beam_width)
    beam_length_min = 0.4  # Minimum beam length
    beam_length_max = 1.0  # Maximum beam length
    beam_length_min = m_to_idx(beam_length_min)
    beam_length_max = m_to_idx(beam_length_max)

    gap_length_min = 0.2
    gap_length_min = m_to_idx(gap_length_min)
    gap_length_max = 0.8 + 0.6 * difficulty
    gap_length_max = m_to_idx(gap_length_max)

    mid_y = m_to_idx(width) // 2

    def add_platform(center_x, center_y, size, height):
        half_size_length = size[0] // 2
        half_size_width = size[1] // 2
        x1, x2 = center_x - half_size_length, center_x + half_size_length
        y1, y2 = center_y - half_size_width, center_y + half_size_width
        height_field[x1:x2, y1:y2] = height

    def add_beam(start_x, mid_y, length, direction):
        if direction == 'horizontal':
            x1, x2 = start_x, start_x + length
            y1, y2 = mid_y - beam_width // 2, mid_y + beam_width // 2
        else:
            x1, x2 = start_x - beam_width // 2, start_x + beam_width // 2
            y1, y2 = mid_y, mid_y + length
        
        beam_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = beam_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(3):  # Set up 3 beams
        length = np.random.randint(beam_length_min, beam_length_max)
        direction = 'horizontal' if i % 2 == 0 else 'vertical'
        add_beam(cur_x, mid_y, length, direction)

        # Position goal in the middle of the beam
        if direction == 'horizontal':
            goals[i + 1] = [cur_x + length // 2, mid_y]
            cur_x += length + gap_length_min
        else:
            goals[i + 1] = [cur_x, mid_y + length // 2]

    for j in range(3):  # Set up 3 platforms
        size = [np.random.randint(platform_length // 2, platform_length),
                np.random.randint(platform_width_min, platform_width_max)]
        height = np.random.uniform(platform_height_min, platform_height_max)
        add_platform(cur_x, mid_y, size, height)

        goals[j + 4] = [cur_x, mid_y]
        cur_x += size[0] + gap_length_max

    # Add final goal behind the last platform
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_30(length, width, field_resolution, difficulty):
    """Obstacle course with platforms, short ramps, and mild gaps for the robot to balance, climb, and jump across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and ramp dimensions
    platform_length = 1.0
    platform_length = m_to_idx(platform_length)
    platform_width = m_to_idx(np.random.uniform(0.9, 1.2))
    platform_height_min, platform_height_max = 0.0 + 0.1 * difficulty, 0.2 + 0.2 * difficulty
    gap_length = m_to_idx(0.1 + 0.1 * difficulty)

    ramp_length = platform_length // 2
    ramp_height_min, ramp_height_max = 0.2, 0.3 + 0.2 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_ramp(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_slope = np.linspace(0, height, num=end_x - start_x)
        height_field[x1:x2, y1:y2] = ramp_slope[:, np.newaxis]

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0.0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    for i in range(6):  # Creating a mix of platforms and ramps
        if i % 2 == 0:
            add_platform(cur_x, cur_x + platform_length, mid_y)
            goals[i + 1] = [cur_x + platform_length // 2, mid_y]
            cur_x += platform_length + gap_length

        else:
            ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
            add_ramp(cur_x, cur_x + ramp_length, mid_y, ramp_height)
            goals[i + 1] = [cur_x + ramp_length // 2, mid_y]
            cur_x += ramp_length + gap_length

    # Add final goal behind the last element and fill rest with flat terrain
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0.0

    return height_field, goals

def set_terrain_31(length, width, field_resolution, difficulty):
    """Alternating high steps and low platforms for the robot to jump across and climb."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set dimensions for high steps and low platforms
    high_step_height_min, high_step_height_max = 0.15 + 0.1 * difficulty, 0.25 + 0.2 * difficulty
    low_platform_height_min, low_platform_height_max = 0.0, 0.1 * difficulty
    step_length, platform_length = 0.8 + 0.2 * difficulty, 1.2 - 0.2 * difficulty
    step_length, platform_length = m_to_idx(step_length), m_to_idx(platform_length)
    gap_length = 0.2 + 0.2 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_step(start_x, height):
        x1, x2 = start_x, start_x + step_length
        y1, y2 = mid_y - m_to_idx(0.64), mid_y + m_to_idx(0.64)  # Width set to 1.28 meters
        height_field[x1:x2, y1:y2] = height

    def add_platform(start_x, height):
        x1, x2 = start_x, start_x + platform_length
        y1, y2 = mid_y - m_to_idx(1.0), mid_y + m_to_idx(1.0)  # Width set to 2 meters
        height_field[x1:x2, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0.0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    for i in range(3):  # Create 3 high steps
        high_step_height = np.random.uniform(high_step_height_min, high_step_height_max)
        low_platform_height = np.random.uniform(low_platform_height_min, low_platform_height_max)
        
        # Add alternating high step and low platform
        add_step(cur_x, high_step_height)
        goals[2 * i + 1] = [cur_x + step_length // 2, mid_y]
        cur_x += step_length + gap_length
        
        add_platform(cur_x, low_platform_height)
        goals[2 * i + 2] = [cur_x + platform_length // 2, mid_y]
        cur_x += platform_length + gap_length

    # Final low platform with goal
    add_platform(cur_x, low_platform_height_min)
    goals[7] = [cur_x + platform_length // 2, mid_y]

    return height_field, goals

def set_terrain_32(length, width, field_resolution, difficulty):
    """Narrow ledges with alternating heights for the robot to balance and navigate across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define parameters for platforms and gaps
    platform_length_min = 0.8 - 0.25 * difficulty
    platform_length_max = 1.2 - 0.1 * difficulty
    platform_width = 0.4 + 0.05 * difficulty
    platform_height_min = 0.0 + 0.2 * difficulty
    platform_height_max = 0.1 + 0.3 * difficulty
    gap_length_min = 0.1 + 0.05 * difficulty
    gap_length_max = 0.3 + 0.2 * difficulty

    platform_length_min, platform_length_max = m_to_idx([platform_length_min, platform_length_max])
    platform_width = m_to_idx(platform_width)
    gap_length_min, gap_length_max = m_to_idx([gap_length_min, gap_length_max])

    mid_y = m_to_idx(width) // 2
    half_width = platform_width // 2

    def add_platform(start_x, end_x, mid_y, height):
        """Adds a platform with a specified height."""
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[start_x:end_x, y1:y2] = height

    dx_offset = m_to_idx(0.1)
    dy_offset_min, dy_offset_max = m_to_idx([-0.2, 0.2])

    # Set spawn area to flat ground and the first goal
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(6):
        platform_length = np.random.randint(platform_length_min, platform_length_max)
        height = np.random.uniform(platform_height_min, platform_height_max)

        dy_offset = np.random.randint(dy_offset_min, dy_offset_max)
        add_platform(cur_x, cur_x + platform_length, mid_y + dy_offset, height)

        # Place goal at the middle of the platform
        goals[i+1] = [cur_x + platform_length // 2, mid_y + dy_offset]

        # Add a gap before the next platform
        gap_length = np.random.randint(gap_length_min, gap_length_max)
        cur_x += platform_length + gap_length

    # Ensure the final section is reachable
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_33(length, width, field_resolution, difficulty):
    """Serpentine pathways with varying heights and narrow bridges to test the robot's turning and balance abilities."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Setup parameters for serpentine pathways and bridges
    pathway_width = 0.4 + 0.6 * (1 - difficulty)
    pathway_width = m_to_idx(pathway_width)
    pathway_height_min, pathway_height_max = 0.1 * difficulty, 0.4 * difficulty
    bridge_length = 1.0 - 0.7 * difficulty
    bridge_length = m_to_idx(bridge_length)
    bridge_height_min, bridge_height_max = 0.2 * difficulty, 0.5 * difficulty

    y_center = m_to_idx(width / 2)
    serpentine_amplitude = m_to_idx(0.5 + 1.5 * difficulty)
    serpentine_frequency = 3 + 5 * difficulty

    def add_pathway_pattern(start_x, end_x, y_center, serpentine_amplitude, serpentine_frequency):
        half_width = pathway_width // 2
        for x in range(start_x, end_x):
            offset = int(serpentine_amplitude * np.sin(serpentine_frequency * 2 * np.pi * (x - start_x) / (end_x - start_x)))
            y1, y2 = y_center + offset - half_width, y_center + offset + half_width
            pathway_height = np.random.uniform(pathway_height_min, pathway_height_max)
            height_field[x, y1:y2] = pathway_height

    def add_bridge(start_x, start_y, end_x, end_y):
        if start_x > end_x or start_y > end_y:
            return
        height_diff = np.random.uniform(bridge_height_min, bridge_height_max)
        bridge_slope = np.linspace(0, height_diff, num=end_x - start_x)
        mid_y = (start_y + end_y) // 2
        for x in range(start_x, end_x):
            height_field[x, mid_y-2:mid_y+2] = bridge_slope[x-start_x]

    dx_min, dx_max = m_to_idx(-0.05), m_to_idx(0.05)
    dy_min, dy_max = m_to_idx(-0.2), m_to_idx(0.2)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), y_center]

    # Add serpentine pathways
    cur_x = spawn_length
    section_length = m_to_idx(2)
    for i in range(4):  # Four primary sections
        next_x = cur_x + section_length
        dy = np.random.randint(dy_min, dy_max)
        add_pathway_pattern(cur_x, next_x, y_center + dy, serpentine_amplitude, serpentine_frequency)
        goals[i+1] = [cur_x + section_length // 2, y_center + dy]
        cur_x = next_x + m_to_idx(0.1)

    # Add narrow bridges connecting pathways
    for i in range(4, 7):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_bridge(cur_x, y_center + dy, cur_x + bridge_length, y_center + dy)
        goals[i+1] = [cur_x + bridge_length // 2, y_center + dy]
        cur_x += bridge_length + m_to_idx(0.1)

    # Add final goal behind the last section of serpentine pathway or bridge
    goals[-1] = [cur_x + m_to_idx(0.5), y_center]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_34(length, width, field_resolution, difficulty):
    """Narrow beams, varying width platforms, and slopes to test balance, precision, and incline traversal."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define the size parameters based on difficulty
    min_beam_width = 0.4 + 0.1 * difficulty
    max_beam_width = 1.0 - 0.2 * difficulty
    min_platform_width = 1.0 + 0.2 * difficulty
    max_platform_width = 2.0 - 0.2 * difficulty
    min_height = 0.1 * difficulty
    max_height = 0.5 * difficulty
    gap_min = 0.2
    gap_max = 1.0

    mid_y = m_to_idx(width / 2)

    def add_beam_or_platform(start_x, end_x, mid_y, platform_width, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
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
        # Determine if this is a beam, wide platform, or inclined ramp
        if i % 2 == 0:  # Use beams for even indices
            platform_width = np.random.uniform(min_beam_width, max_beam_width)
        else:  # Use wide platforms for odd indices
            platform_width = np.random.uniform(min_platform_width, max_platform_width)

        platform_length = 1.0 + 0.4 * difficulty
        platform_length = m_to_idx(platform_length)
        platform_height = np.random.uniform(min_height, max_height)
        
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        add_beam_or_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, m_to_idx(platform_width), platform_height)

        # Place a goal at each obstacle
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Create a gap between platforms
        gap_length = np.random.uniform(gap_min, gap_max) * difficulty + 0.1
        gap_length = m_to_idx(gap_length)

        cur_x += platform_length + dx + gap_length

    # Add final goal behind the last platform, filling in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_35(length, width, field_resolution, difficulty):
    """Narrow passageways and raised walkways to test precision and careful navigation."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]
    
    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Configure parameters based on difficulty
    path_width = 0.4 + (0.6 * (1 - difficulty))  # Path width between 0.4m and 1m
    passage_height = 0.05 + (0.3 * difficulty)  # Passage height between 0.05m and 0.35m
    walkway_height = 0.1 + (0.3 * difficulty)  # Walkway height between 0.1m and 0.4m
    section_length = 1.0 + (1.0 * difficulty)  # Varying section lengths, longer with higher difficulty

    path_width = m_to_idx(path_width)
    passage_height = np.random.uniform(passage_height, passage_height + 0.1 * difficulty)
    walkway_height = np.random.uniform(walkway_height, walkway_height + 0.1 * difficulty)
    section_length = m_to_idx(section_length)

    # Initial flat ground area for spawn point
    spawn_area = m_to_idx(2)
    height_field[:spawn_area, :] = 0
    mid_y = m_to_idx(width) // 2
    goals[0] = [spawn_area - m_to_idx(0.5), mid_y]

    cur_x = spawn_area

    def add_narrow_passage(start_x, length, height, center_y):
        half_width = path_width // 2
        x_start, x_end = start_x, start_x + length
        y_start, y_end = center_y - half_width, center_y + half_width
        height_field[x_start:x_end, y_start:y_end] = height

    # Create a sequence of narrow passages and raised walkways
    for i in range(7):
        if i % 2 == 0:
            # Add narrow passage
            add_narrow_passage(cur_x, section_length, passage_height, mid_y)
            goals[i+1] = [cur_x + section_length / 2, mid_y]
        else:
            # Add raised walkway
            height_field[cur_x:cur_x + section_length, :] = walkway_height
            goals[i+1] = [cur_x + section_length / 2, mid_y]

        cur_x += section_length

    # Final goal at the end of the course
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    return height_field, goals

def set_terrain_36(length, width, field_resolution, difficulty):
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

def set_terrain_37(length, width, field_resolution, difficulty):
    """Alternating narrow walkways and wider platforms testing the robot's balance and navigation."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    length_idx = m_to_idx(length)
    width_idx = m_to_idx(width)
    height_field = np.zeros((length_idx, width_idx))
    goals = np.zeros((8, 2))

    narrow_walkway_width = 0.4 + 0.1 * difficulty  # Narrower walkways
    narrow_walkway_width = m_to_idx(narrow_walkway_width)
    platform_width = np.random.uniform(1.0, 1.5)  # Wider platforms
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.2 * difficulty, 0.4 * difficulty

    slope_length = 0.9 - 0.3 * difficulty
    slope_length = m_to_idx(slope_length)

    mid_y = width_idx // 2

    def add_narrow_walkway(start_x, end_x, mid_y):
        half_width = narrow_walkway_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = np.random.uniform(platform_height_min, platform_height_max)

    def add_wide_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = np.random.uniform(platform_height_min, platform_height_max)

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(1, 8):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        if i % 2 == 1:
            # Add narrow walkway
            add_narrow_walkway(cur_x, cur_x + slope_length + dx, mid_y + dy)
        else:
            # Add wide platform
            add_wide_platform(cur_x, cur_x + slope_length + dx, mid_y + dy)

        goals[i] = [cur_x + (slope_length + dx) / 2, mid_y + dy]
        cur_x += slope_length + dx  # No large gaps to reduce edge violations

    return height_field, goals

def set_terrain_38(length, width, field_resolution, difficulty):
    """A series of alternating steps and tilted platforms to test precise foot placement and balance in varied terrain."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Terrain and obstacle configurations
    step_height_base = 0.1
    step_height_var = 0.15 * difficulty
    step_length = 0.5
    platform_length = 1.2 - 0.5 * difficulty
    platform_width = 0.6 + 0.5 * difficulty
    platform_tilt_max = 0.1 + 0.3 * difficulty
    gap_length = 0.3 * difficulty

    step_length = m_to_idx(step_length)
    platform_length = m_to_idx(platform_length)
    platform_width = m_to_idx(platform_width)
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_step(start_x, height):
        width = m_to_idx(0.8)
        half_width = width // 2
        x1, x2 = start_x, start_x + step_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_tilted_platform(start_x, end_x, mid_y, tilt_angle):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        tilt = np.linspace(0, tilt_angle, y2 - y1)
        tilt = tilt[None, :]  # Add a dimension for broadcasting to x
        height_field[x1:x2, y1:y2] = tilt

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    current_x = spawn_length

    # Place alternating steps and tilted platforms
    for i in range(3):
        # Step
        step_height = step_height_base + random.uniform(-step_height_var, step_height_var)
        add_step(current_x, step_height)
        goals[i+1] = [current_x + step_length // 2, mid_y]
        current_x += step_length

        # Gap
        current_x += gap_length

        # Tilted platform
        tilt_angle = random.uniform(0, platform_tilt_max)
        add_tilted_platform(current_x, current_x + platform_length, mid_y, tilt_angle)
        goals[i+4] = [current_x + platform_length // 2, mid_y]
        current_x += platform_length

        # Gap
        current_x += gap_length

    # Add final goal at the end
    goals[-1] = [m_to_idx(11.5), mid_y]
    height_field[m_to_idx(11):, :] = 0

    return height_field, goals

def set_terrain_39(length, width, field_resolution, difficulty):
    """Multi-skill course featuring small ramps, jumps, and a final narrow bridge."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    mid_y = m_to_idx(width / 2)

    def add_ramp(start_x, end_x, mid_y, start_height, end_height):
        """Add a ramp to the height field."""
        for x in range(start_x, end_x):
            height_value = start_height + ((end_height - start_height) * (x - start_x) / (end_x - start_x))
            height_field[x, mid_y- m_to_idx(0.5): mid_y + m_to_idx(0.5)] = height_value

    def add_jump(start_x, mid_y, height, length, width):
        """Add a platform to jump onto."""
        x1, x2 = start_x, start_x + length
        y1, y2 = mid_y - width//2, mid_y + width//2
        height_field[x1:x2, y1:y2] = height

    def add_narrow_bridge(start_x, end_x, mid_y, width):
        """Add a narrow bridge towards the end of the course."""
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - width//2, mid_y + width//2
        height_field[x1:x2, y1:y2] = 0.5

    # Set up levels and parameters
    ramp_height = 0.2 + 0.3 * difficulty
    platform_height = 0.4 + 0.3 * difficulty
    gap_length = m_to_idx(0.4)
    narrow_bridge_width = m_to_idx(0.4)

    # Clear spawn area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    # Add series of ramps and platforms
    for i in range(3):
        ramp_length = m_to_idx(1.0 + 0.5 * difficulty)
        add_ramp(cur_x, cur_x + ramp_length, mid_y, 0, ramp_height)
        goals[i+1] = [cur_x + ramp_length//2, mid_y]
        
        cur_x += ramp_length + gap_length
        
        platform_length = m_to_idx(1.0)
        add_jump(cur_x, mid_y, platform_height, platform_length, m_to_idx(1.0))
        goals[i+2] = [cur_x + platform_length//2, mid_y]
        
        cur_x += platform_length + gap_length

    # Add a final narrow bridge
    bridge_length = m_to_idx(2.0)
    add_narrow_bridge(cur_x, cur_x + bridge_length, mid_y, narrow_bridge_width)
    goals[6] = [cur_x + bridge_length//2, mid_y]

    cur_x += bridge_length
    
    # Set final goal
    goals[7] = [cur_x + m_to_idx(0.5), mid_y]

    #Ensure remaining area is flat
    height_field[cur_x:, :] = 0

    return height_field, goals

# INSERT TERRAIN FUNCTION DEFINITIONS HERE
