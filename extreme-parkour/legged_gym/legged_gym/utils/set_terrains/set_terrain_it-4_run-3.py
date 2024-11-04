
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
    """Complex course with stepping stones, staggered platforms, and inclined ramps."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform dimensions and height range
    platform_length = 1.0
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.9, 1.2)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.1 * difficulty, 0.3 + 0.3 * difficulty

    gap_length = m_to_idx(0.3 + 0.6 * difficulty)
    
    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_stepping_stones(start_x, num_stones, mid_y):
        stone_length = m_to_idx(0.4)
        stone_width = m_to_idx(0.4)
        stone_height_range = 0.0 + 0.25 * difficulty, 0.1 + 0.35 * difficulty

        for i in range(num_stones):
            platform_height = np.random.uniform(*stone_height_range)
            step_x = start_x + i * (stone_length + gap_length)
            add_platform(step_x, step_x + stone_length, mid_y + (np.random.randint(-2, 3) * stone_width), platform_height)

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
    
    # Add first platform
    platform_height = np.random.uniform(platform_height_min, platform_height_max)
    add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)
    goals[1] = [cur_x + platform_length / 2, mid_y]
    cur_x += platform_length + gap_length

    # Add stepping stones
    add_stepping_stones(cur_x, 3, mid_y)  # 3 stepping stones
    goals[2] = [cur_x + platform_length, mid_y]

    cur_x += 3 * m_to_idx(0.4) + 3 * gap_length

    # Add staggered platform with narrow bridges
    stagger_x = [cur_x, cur_x + platform_length + gap_length, cur_x + 2 * (platform_length + gap_length)]
    stagger_y = [mid_y - m_to_idx(1), mid_y, mid_y + m_to_idx(1)]
    for x, y in zip(stagger_x, stagger_y):
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        add_platform(x, x + platform_length, y, platform_height)

    goals[3] = [stagger_x[-1] + platform_length / 2, stagger_y[-1]]
    cur_x = stagger_x[-1] + platform_length + gap_length

    # Add inclined ramp
    ramp_height = np.random.uniform(0.3 + 0.3 * difficulty, 0.5 + 0.5 * difficulty)
    add_ramp(cur_x, cur_x + platform_length, mid_y, ramp_height)
    goals[4] = [cur_x + platform_length / 2, mid_y]
    cur_x += platform_length + gap_length

    # Add final set of platforms
    for i in range(3):  # 3 platforms
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        add_platform(cur_x, cur_x + platform_length, mid_y + m_to_idx(i * 0.2), platform_height)
        goals[5 + i] = [cur_x + platform_length / 2, mid_y + m_to_idx(i * 0.2)]
        cur_x += platform_length + gap_length

    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals  # Return the desired terrain and goals

def set_terrain_1(length, width, field_resolution, difficulty):
    """Zigzag sloped ramps and variable-height platforms to test balance and varied movement."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set dimensions for platforms and ramps
    platform_length = 1.0 - 0.1 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.2)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.1 * difficulty, 0.3 + 0.2 * difficulty
    ramp_length = 1.0 - 0.15 * difficulty
    ramp_length = m_to_idx(ramp_length)
    ramp_height_min, ramp_height_max = 0.1 + 0.15 * difficulty, 0.35 + 0.25 * difficulty
    slope_width = m_to_idx(1.0)
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
        half_width = slope_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        slant = np.linspace(0, ramp_height, num=y2-y1)[::direction]
        slant = slant[None, :]  # Add a dimension for broadcasting to x
        height_field[x1:x2, y1:y2] = slant
    
    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # Initial goal at spawn

    cur_x = spawn_length
    for i in range(3):  # Add 3 platform-ramp pairs
        # Add a platform
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)

        # Put goal in the center of the platform
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        cur_x += platform_length + dx + gap_length

        # Add a ramp
        direction = (-1) ** i  # Alternate ramp direction (left/right)
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max) * direction

        add_ramp(cur_x, cur_x + ramp_length + dx, mid_y + dy, direction)

        # Put goal in the center of the ramp
        goals[i+4] = [cur_x + (ramp_length + dx) / 2, mid_y + dy]

        cur_x += ramp_length + dx + gap_length
    
    # Add final goal, fill remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_2(length, width, field_resolution, difficulty):
    """Series of slopes and alternating narrow platforms, testing the robot's ability to traverse changing elevations and gaps."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.0)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.15 * difficulty, 0.3 * difficulty
    slope_height_min, slope_height_max = 0.1, 0.5 * difficulty
    gap_length = 0.1 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)
    mid_y = m_to_idx(width) // 2

    def create_slope(start_x, end_x, mid_y, slope_height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = np.linspace(0, slope_height, x2 - x1).reshape(-1, 1)

    def create_narrow_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 4
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    # Create Slopes and Platforms
    for i in range(7):
        slope_height = np.random.uniform(slope_height_min, slope_height_max)
        create_slope(cur_x, cur_x + platform_length, mid_y, slope_height)
        cur_x += platform_length
        goals[i + 1] = [cur_x - m_to_idx(0.5), mid_y]
        
        if i % 2 == 0:  # Every other goal introduces a narrow platform
            height = np.random.uniform(platform_height_min, platform_height_max)
            create_narrow_platform(cur_x, cur_x + platform_length, mid_y, height)
            cur_x += platform_length + gap_length

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_3(length, width, field_resolution, difficulty):
    """Multiple platforms, narrow beams, and ramps for the robot to climb on, balance, and jump across."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions
    platform_length = 1.0 - 0.2 * difficulty  # Slightly longer platforms
    platform_length = m_to_idx(platform_length)
    platform_width = m_to_idx(1.0)
    platform_height_min, platform_height_max = 0.1 + 0.3 * difficulty, 0.15 + 0.4 * difficulty
    gap_length = 0.3 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)

    # Set up narrow beam dimensions
    beam_length = platform_length
    beam_width = m_to_idx(0.4 - 0.1 * difficulty)  # Narrower beams
    beam_height = 0.15 + 0.35 * difficulty

    # Set up ramp dimensions
    ramp_length = m_to_idx(1.5 - 0.5 * difficulty)
    ramp_width = m_to_idx(0.4 - 0.1 * difficulty)
    ramp_height = 0.2 + 0.5 * difficulty

    mid_y = m_to_idx(width / 2)

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_narrow_beam(start_x, end_x, mid_y):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = beam_height

    def add_ramp(start_x, end_x, mid_y, direction):
        half_width = ramp_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width * direction, mid_y + half_width * direction
        slant = np.linspace(0, ramp_height, num=x2 - x1)[::direction]
        height_field[x1:x2, y1:y2] = slant[:, None]

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    alternator = 0  # To alternate between different obstacles

    for i in range(7):
        dx = np.random.randint(dx_min, dx_max)
        dy = (i % 2) * np.random.randint(dy_min, dy_max)

        if alternator % 3 == 0:
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i+1] = [cur_x + (platform_length + dx) // 2, mid_y + dy]
        elif alternator % 3 == 1:
            add_narrow_beam(cur_x, cur_x + beam_length + dx, mid_y + dy)
            goals[i+1] = [cur_x + (beam_length + dx) // 2, mid_y + dy]
        else:
            direction = 1 if i % 4 < 2 else -1
            add_ramp(cur_x, cur_x + ramp_length + dx, mid_y + dy, direction)
            goals[i+1] = [cur_x + (ramp_length + dx) // 2, mid_y + dy]

        cur_x += platform_length + dx + gap_length
        alternator += 1

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_4(length, width, field_resolution, difficulty):
    """A series of inclined and varied platforms for the quadruped to navigate and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and obstacle dimensions
    platform_length_base = 0.8 + 0.2 * difficulty
    platform_length_variation = 0.3 * difficulty
    platform_width_min, platform_width_max = 0.4, 0.8  # Narrower for more difficulty
    platform_height_min, platform_height_max = 0.1, 0.4 * difficulty
    gap_length_base = 0.2
    gap_length_variation = 0.5 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_platform_or_ramp(start_x, end_x, y_mid, height, is_ramp=False, direction=1):
        half_width = m_to_idx(np.random.uniform(platform_width_min, platform_width_max) / 2)
        x1, x2 = start_x, end_x
        y1, y2 = y_mid - half_width, y_mid + half_width
        
        if is_ramp:
            incline = np.linspace(0, height * direction, x2 - x1)[:, None]
            height_field[x1:x2, y1:y2] = incline + height_field[x1, y1:y1+1]
        else:
            height_field[x1:x2, y1:y2] = height

    def add_goal(start_x, end_x, y_mid):
        goals.append([(start_x + end_x) / 2, y_mid])

    dx_min, dx_max = -0.2, 0.2
    dy_variation = 0.4  # Max shift along y-axis

    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_variation = m_to_idx(dy_variation)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Initial platform after spawn flat area
    cur_x = spawn_length
    for i in range(6):  # Create a variety of platforms and ramps
        platform_length = m_to_idx(platform_length_base + platform_length_variation * np.random.random())
        gap_length = m_to_idx(gap_length_base + gap_length_variation * np.random.random())

        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(-dy_variation, dy_variation)
        
        is_ramp = (i % 2 == 0)  # every alternate platform is a ramp
        height = np.random.uniform(platform_height_min, platform_height_max)
        direction = (-1) ** i  # alternate inclination direction for ramp
        
        add_platform_or_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, height, is_ramp, direction)
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        cur_x += platform_length + dx + gap_length

    # Final goal past the last platform
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_5(length, width, field_resolution, difficulty):
    """A blend of curved inclines and varied-width platforms to navigate carefully and balance across obstacles."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform and incline dimensions
    platform_length_base = 1.0 - 0.2 * difficulty
    platform_width_range = (1.0, 1.6)
    platform_height_min, platform_height_max = 0.1, 0.5 * difficulty
    incline_length = 1.0 - 0.2 * difficulty
    incline_length = m_to_idx(incline_length)
    gap_length_base = 0.1 + 0.4 * difficulty
    mid_y = m_to_idx(width) // 2

    def add_platform_segment(start_x, width_range, height_range):
        half_width = m_to_idx(np.random.uniform(*width_range)) // 2
        x1, x2 = start_x, start_x + m_to_idx(platform_length_base)
        y_center = mid_y + np.random.randint(-m_to_idx(0.5), m_to_idx(0.5))
        y1, y2 = y_center - half_width, y_center + half_width
        platform_height = np.random.uniform(*height_range)
        height_field[x1:x2, y1:y2] = platform_height
        return x2, y_center

    def add_incline(start_x, direction):
        half_width = m_to_idx(platform_width_range[0]) // 2
        x1, x2 = start_x, start_x + incline_length
        if direction > 0:
            slant = np.linspace(0, difficulty * 0.5, num=x2-x1)[:, None]
        else:
            slant = np.linspace(difficulty * 0.5, 0, num=x2-x1)[:, None]
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] += slant

    x_start = m_to_idx(2)
    goals[0] = [x_start - m_to_idx(0.5), mid_y]

    # Setting platforms with variations
    for i in range(4):
        x_start, y_center = add_platform_segment(x_start, platform_width_range, (platform_height_min, platform_height_max))
        goals[i+1] = [x_start - m_to_idx(platform_length_base / 2), y_center]
        x_start += m_to_idx(gap_length_base)
    
    # Adding an incline path
    add_incline(x_start, direction=1)
    goals[5] = [x_start + incline_length // 2, mid_y]

    x_start += incline_length + m_to_idx(gap_length_base)

    # Setting remaining varied-height platforms
    for i in range(2):
        x_start, y_center = add_platform_segment(x_start, platform_width_range, (platform_height_min, platform_height_max))
        goals[6+i] = [x_start - m_to_idx(platform_length_base / 2), y_center]
        x_start += m_to_idx(gap_length_base)

    # Final goal and reset terrain to flat toward the end.
    goals[7] = [x_start + m_to_idx(0.5), mid_y]
    height_field[x_start:, :] = 0

    return height_field, goals

def set_terrain_6(length, width, field_resolution, difficulty):
    """Varying-height platforms and shallow inclines for balancing and moderate climbing."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length = 1.0 - 0.1 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 0.8
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.1 * difficulty, 0.15 + 0.2 * difficulty
    incline_length = 0.5 + 0.2 * difficulty
    incline_length = m_to_idx(incline_length)
    gap_length = 0.3 + 0.4 * difficulty  # Adjust gap length for difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_incline(start_x, end_x, mid_y, height, direction):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        incline = np.linspace(0, height, num=x2-x1)[::direction]
        incline = incline[:, None]  # Add a dimension for broadcasting to y
        height_field[x1:x2, y1:y2] = incline

    dx_range = m_to_idx([0.0, 0.2])
    dy_range = m_to_idx([0.0, 0.4])
    dy_offset_direction = (-1) ** np.arange(6)  # Alternate slope directions

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    for i in range(5):  # Set up 5 platforms and inclines
        dx = np.random.randint(*dx_range)
        dy = np.random.randint(*dy_range) * dy_offset_direction[i]

        if i % 2 == 0:
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        else:
            height = np.random.uniform(platform_height_min, platform_height_max)
            add_incline(cur_x, cur_x + incline_length + dx, mid_y + dy, height, (-1) ** i)
            goals[i+1] = [cur_x + (incline_length + dx) / 2, mid_y + dy]

        cur_x += platform_length + incline_length + dx + gap_length if i % 2 != 0 else platform_length + dx + gap_length

    # Add final goal behind the last platform/incline, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_7(length, width, field_resolution, difficulty):
    """Raised platforms with varied heights and staggered pathways for the robot to navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform dimensions
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width_min, platform_width_max = 0.5, 1.2 - 0.3 * difficulty
    platform_heights = np.linspace(0.1, 0.35 * difficulty, 4)
    gap_length = 0.1 + 0.2 * difficulty
    gap_length = m_to_idx(gap_length)
    
    mid_y = m_to_idx(width) // 2
    
    def add_platform(start_x, end_x, mid_y, width, height):
        half_width = m_to_idx(width) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height
    
    # Initial Spawn Area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(6):
        platform_width = np.random.uniform(platform_width_min, platform_width_max)
        platform_height = np.random.choice(platform_heights)
        dx = np.random.uniform(-0.1, 0.1) * field_resolution
        dy = np.random.uniform(-0.4, 0.4) * field_resolution
        
        add_platform(cur_x, cur_x + platform_length, mid_y + m_to_idx(dy), platform_width, platform_height)
        goals[i+1] = [cur_x + platform_length // 2, mid_y + m_to_idx(dy)]
        
        cur_x += platform_length + gap_length
    
    # Final goal beyond last platform
    add_platform(cur_x, cur_x + platform_length, mid_y, platform_width, np.random.choice(platform_heights))
    goals[-1] = [cur_x + platform_length // 2, mid_y]
    
    return height_field, goals

def set_terrain_8(length, width, field_resolution, difficulty):
    """Mixed terrain with stepping stones, gaps, and varying height platforms for the quadruped to navigate."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Terrain and obstacle parameters
    step_length = 0.4
    step_length_idx = m_to_idx(step_length)
    step_width = 0.4 + 0.2 * difficulty
    step_width_idx = m_to_idx(step_width)
    step_height_min, step_height_max = 0.1, 0.25 + 0.2 * difficulty
    gap_length = 0.2 + 0.5 * difficulty
    gap_length_idx = m_to_idx(gap_length)

    platform_length = 0.8 - 0.2 * difficulty
    platform_length_idx = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.2)
    platform_width_idx = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.05 + 0.2 * difficulty, 0.1 + 0.3 * difficulty
    
    mid_y = m_to_idx(width) // 2

    def add_step(start_x, mid_y):
        half_width = step_width_idx // 2
        x1 = start_x
        x2 = start_x + step_length_idx
        y1 = mid_y - half_width
        y2 = mid_y + half_width
        step_height = np.random.uniform(step_height_min, step_height_max)
        height_field[x1:x2, y1:y2] = step_height

    def add_gap(start_x, mid_y):
        half_width = step_width_idx // 2
        x1 = start_x
        x2 = start_x + gap_length_idx
        y1 = mid_y - half_width
        y2 = mid_y + half_width
        height_field[x1:x2, y1:y2] = -0.2
    
    def add_platform(start_x, mid_y):
        half_width = platform_width_idx // 2
        x1 = start_x
        x2 = start_x + platform_length_idx
        y1 = mid_y - half_width
        y2 = mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]
    
    cur_x = spawn_length

    # Add a series of steps, gaps, and platforms
    for i in range(3):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_step(cur_x, mid_y + dy)
        goals[i + 1] = [cur_x + step_length_idx // 2, mid_y + dy]
        cur_x += step_length_idx + dx + gap_length_idx
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_gap(cur_x, mid_y + dy)
        cur_x += gap_length_idx + dx
    
    for i in range(3):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, mid_y + dy)
        goals[4 + i] = [cur_x + platform_length_idx // 2, mid_y + dy]
        cur_x += platform_length_idx + dx + gap_length_idx

    # Add final goal behind the last platform
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_9(length, width, field_resolution, difficulty):
    """Series of mid-width platforms, shallow ramps, and gaps to balance climbing, balancing, and jumping needs."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform and ramp dimensions
    platform_length = 1.2 - 0.2 * difficulty  # Slightly longer platforms
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.3)  # Wider platforms for less edge errors
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.1 * difficulty, 0.3 + 0.2 * difficulty  # Reasonable heights
    ramp_height_min, ramp_height_max = 0.1 + 0.2 * difficulty, 0.2 + 0.3 * difficulty
    gap_length = 0.2 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_ramp(start_x, end_x, mid_x, direction):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        slant = np.linspace(0, ramp_height, num=x2-x1)[::direction]
        slant = slant[:, None]  # Add a dimension for broadcasting to y
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.0, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set initial flat ground for spawning
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(5):  # Mix 5 platforms and ramps
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        if i % 2 == 0:  # Add platform
            platform_height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height)
        else:  # Add ramp
            direction = (-1) ** (i // 2)  # Alternate direction for ramps
            add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, direction)

        # Set goal location in the center of current feature
        goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Move to the next section
        cur_x += platform_length + dx + gap_length

    # Final goal behind the last platform
    goals[-2] = [cur_x, mid_y]
    
    # Ensure the final gap is realistic and has a clearance
    gap_for_last_platform = platform_length + dx + gap_length // 2
    cur_x += gap_for_last_platform
    height_field[cur_x - m_to_idx(0.1):, :] = 0
    
    goals[-1] = [cur_x, mid_y]

    return height_field, goals

# INSERT TERRAIN FUNCTION DEFINITIONS HERE
