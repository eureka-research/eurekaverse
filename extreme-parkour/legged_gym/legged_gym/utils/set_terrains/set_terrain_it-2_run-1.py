
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
    """Multiple staggered platforms and sideways ramps for climbing, balancing, and precise navigation."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform, ramp dimensions, and gaps
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 1.0 + 0.2 * difficulty  # Slightly varied width for challenge
    platform_width = m_to_idx(platform_width)
    
    platform_height_min, platform_height_max = 0.1, 0.4 * difficulty
    ramp_height_min, ramp_height_max = 0.2, 0.6 * difficulty
    gap_length = 0.15 + 0.4 * difficulty
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

    dx_min, dx_max = -0.1, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Set pit after spawn area
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    for i in range(3):  # Set 3 platforms
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
        goals[i+1] = [cur_x + (platform_length+dx) // 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

    for i in range(3):  # Set 3 sideways ramps
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        direction = (-1) ** i  # Alternate direction for variety
        dy *= direction
        add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, direction)
        goals[4+i] = [cur_x + (platform_length+dx) // 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

    # Add final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_1(length, width, field_resolution, difficulty):
    """Elevated platforms with tilt and varying heights requiring precision and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform parameters
    base_length = 1.0
    base_width = 0.9
    base_height = 0.3
    
    platform_length = base_length - 0.4 * difficulty
    platform_width = base_width - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = m_to_idx(platform_width)
    height_min = base_height + 0.2 * difficulty
    height_max = base_height + 0.4 * difficulty

    gap_min = 0.2
    gap_max = 0.7
    gap_length = gap_min + (gap_max - gap_min) * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width / 2)

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_tilted_platform(start_x, end_x, mid_y, height, tilt):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slant = np.linspace(0, tilt, num=(y2-y1))[None, :]
        height_field[x1:x2, y1:y2] = height + slant

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # First goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Set remaining area to pit
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length

    for i in range(6):  # Set up 6 platforms
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        platform_height = np.random.uniform(height_min, height_max)
        if i % 2 == 0:
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height)
        else:
            tilt = np.random.uniform(0.05, 0.15) * difficulty
            add_tilted_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height, tilt)

        # Goal in center of each platform
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += platform_length + dx + gap_length

    # Final goal behind last obstacle
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_2(length, width, field_resolution, difficulty):
    """Narrow beams with varying heights to test the quadruped's balance and agility."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up beam and platform dimensions
    beam_length = 1.0 - 0.3 * difficulty
    beam_length_idx = m_to_idx(beam_length)
    beam_width = 0.2  # Narrow beam width of 0.2 meters
    beam_width_idx = m_to_idx(beam_width)
    beam_height_min, beam_height_max = 0.05 * difficulty, 0.3 * difficulty

    plank_width = np.random.uniform(0.5, 1.0)  # Mildly wider than beam for variety
    plank_width_idx = m_to_idx(plank_width)
    plank_height_min, plank_height_max = 0.05 * difficulty, 0.2 * difficulty

    gap_length = 0.1 + 0.6 * difficulty
    gap_length_idx = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, mid_y):
        """Adds a narrow beam with varying height."""
        half_width = beam_width_idx // 2
        beam_height = np.random.uniform(beam_height_min, beam_height_max)
        height_field[start_x:end_x, mid_y - half_width:mid_y + half_width] = beam_height

    def add_plank(start_x, end_x, mid_y):
        """Adds a wider plank with varying height."""
        half_width = plank_width_idx // 2
        plank_height = np.random.uniform(plank_height_min, plank_height_max)
        height_field[start_x:end_x, mid_y - half_width:mid_y + half_width] = plank_height

    dx_min, dx_max = -0.1, 0.2
    dx_min_idx, dx_max_idx = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min_idx, dy_max_idx = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # First goal near spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    # Begin placing beams and planks
    for i in range(4):  # Alternating 4 beams and 4 planks in total
        dx = np.random.randint(dx_min_idx, dx_max_idx)
        dy = np.random.randint(dy_min_idx, dy_max_idx)

        # Alternate between beams and planks
        if i % 2 == 0:
            add_beam(cur_x, cur_x + beam_length_idx + dx, mid_y + dy)
        else:
            add_plank(cur_x, cur_x + beam_length_idx + dx, mid_y + dy)

        goals[i + 1] = [cur_x + (beam_length_idx + dx) // 2, mid_y + dy]
        cur_x += beam_length_idx + dx + gap_length_idx

    # Fill remaining gap and add last goals behind the final beam
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_3(length, width, field_resolution, difficulty):
    """Urban-inspired obstacle course featuring elevated platforms and gaps for jumping."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions
    platform_length = 1.2 - 0.3 * difficulty  # More consistent and challenging length
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.4)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.2 + 0.2 * difficulty, 0.4 + 0.25 * difficulty
    gap_length = 0.4 + 0.6 * difficulty  # Increased gap lengths for added difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.5, 0.5
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    for i in range(7):  # Set up 7 platforms
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)

        # Put goal in the center of the platform
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += platform_length + dx + gap_length
    
    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_4(length, width, field_resolution, difficulty):
    """Mixed narrow beams and varied-height steps for precision foot placement and stability."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    
    # Set up platform and step dimensions
    platform_length = 0.6 + 0.2 * difficulty  # Longer for easier course, shorter for harder
    platform_length = m_to_idx(platform_length)
    platform_width = 0.4 + 0.2 * difficulty  # Wide platforms for easier and narrow for harder
    platform_width = m_to_idx(platform_width)

    step_height_min = 0.05 * difficulty
    step_height_max = 0.25 * difficulty
    gap_length = 0.2 + 0.3 * difficulty  # Smaller gaps for easier course, larger gaps for harder
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        """Adds a platform to the height field."""
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_step(start_x, end_x, mid_y, height):
        """Adds steps of varying heights to the terrain."""
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = m_to_idx(-0.1), m_to_idx(0.1)
    dy_min, dy_max = m_to_idx(-0.2), m_to_idx(0.2)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal near the spawn area
    
    cur_x = spawn_length
    for i in range(6):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        height = np.random.uniform(step_height_min, step_height_max)
        
        if i % 2 == 0:  # Even - add platform
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, height)
        else:  # Odd - add step
            add_step(cur_x, cur_x + platform_length + dx, mid_y + dy, height)
        
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += platform_length + dx + gap_length

    # Add final goal after the last platform/step
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_5(length, width, field_resolution, difficulty):
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

def set_terrain_6(length, width, field_resolution, difficulty):
    """Combination of stairs, narrow beams, and sloped surfaces traversing a pit for the robot to climb on and jump across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Distance between key features
    gap_length = 0.4 + 0.4 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    # Function to add stairs
    def add_stairs(start_x, end_x, mid_y, steps, step_height):
        half_width = m_to_idx(0.6)  # making stairs wider
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        stair_spacing = (x2 - x1) // steps
        for i in range(steps):
            height_field[x1 + i * stair_spacing : x1 + (i + 1) * stair_spacing, y1:y2] = i * step_height

    # Function to add beams
    def add_beam(start_x, end_x, mid_y):
        half_width = m_to_idx(0.4)  # narrow beams
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        beam_height = np.random.uniform(0.15, 0.3)
        height_field[x1:x2, y1:y2] = beam_height

    # Function to add slopes
    def add_slope(start_x, end_x, mid_y, direction):
        half_width = m_to_idx(0.5)
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slope_height = np.random.uniform(0.1 + 0.1 * difficulty, 0.25 + 0.25 * difficulty)
        slant = np.linspace(0, slope_height, num=x2-x1)
        if direction == 'up':
            height_field[x1:x2, y1:y2] = slant[:, None]
        else:
            height_field[x1:x2, y1:y2] = slant[::-1][:, None]

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at the end of the spawn area

    # Set remaining area to be a pit
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    features = ['stair', 'beam', 'slope'] * 2  # Repeat feature types
    random.shuffle(features)

    for i in range(6):  # Set up 6 features
        dx = random.randint(-m_to_idx(0.1), m_to_idx(0.1))
        if features[i] == 'stair':
            add_stairs(cur_x, cur_x + m_to_idx(1.2) + dx, mid_y, 5, 0.1 + 0.1 * difficulty)
        elif features[i] == 'beam':
            add_beam(cur_x, cur_x + m_to_idx(1.0) + dx, mid_y)
        elif features[i] == 'slope':
            direction = 'up' if i % 2 == 0 else 'down'
            add_slope(cur_x, cur_x + m_to_idx(1.0) + dx, mid_y, direction)

        # Put goal in the center of each feature
        goals[i+1] = [cur_x + (m_to_idx(1.0) + dx) / 2, mid_y]

        # Add gap
        cur_x += m_to_idx(1.0) + dx + gap_length

    # Add final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_7(length, width, field_resolution, difficulty):
    """Mixed terrain including uneven steps, narrow planks, and tilted surfaces for the quadruped to navigate through."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Constants
    platform_length = 1.0 - 0.3 * difficulty  # Adjusted for difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 0.3 + 0.05 * difficulty
    platform_width = m_to_idx(platform_width)
    pit_depth = -1.0
    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_plank(start_x, end_x, mid_y, height, tilt):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slant = np.linspace(0, tilt, num=x2-x1)[:, None]  # tilt effect
        height_field[x1:x2, y1:y2] = height + slant

    def add_gap(cur_x):
        # Set gap area to pit depth
        height_field[cur_x:cur_x + gap_length, :] = pit_depth
        return cur_x + gap_length

    dx_min, dx_max = -0.1, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)
    tilt_range = 0.0, 0.05 + 0.1 * difficulty

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Set remaining area to be a pit and platforms
    cur_x = spawn_length
    for i in range(6):  # Set up 6 mixed platforms and bridges
        dx = np.random.randint(dx_min, dx_max)
        height_min, height_max = 0.1 * difficulty, 0.5 * difficulty
        platform_height = np.random.uniform(height_min, height_max)
        dy = np.random.randint(dy_min, dy_max)
        if i % 2 == 0:
            # Plank with slope
            tilt = np.random.uniform(*tilt_range)
            add_plank(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height, tilt)
        else:
            # Regular platform
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height)

        # Put goal in the center of the platform/plank
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Add gap
        gap_length = m_to_idx(0.1 + 0.5 * difficulty)
        cur_x = add_gap(cur_x + platform_length + dx)
    
    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_8(length, width, field_resolution, difficulty):
    """Offset and narrow platforms forming a zigzag path to test the quadruped's balancing and turning abilities."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and gap dimensions
    platform_length = 0.6 + 0.4 * difficulty  # Slightly smaller length to increase maneuvering challenge
    platform_length = m_to_idx(platform_length)
    platform_width = 0.5 + 0.2 * difficulty  # Slightly smaller width
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.2 + 0.3 * difficulty  # Modest height range
    gap_length = 0.3 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(center_x, center_y, height):
        half_length = platform_length // 2
        half_width = platform_width // 2
        x1, x2 = center_x - half_length, center_x + half_length
        y1, y2 = center_y - half_width, center_y + half_width
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = -0.2, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4  # Allow small y-axis variations
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length + gap_length

    for i in range(7):  # Set up 7 platforms
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        platform_height = np.random.uniform(platform_height_min, platform_height_max)

        add_platform(cur_x + dx, mid_y + dy, platform_height)

        # Put goal at the center of each platform
        goals[i+1] = [cur_x + dx + m_to_idx(0.25), mid_y + dy]  # Center goals with slight forward offset

        # Add gap
        cur_x += platform_length + dx + gap_length

    return height_field, goals


def set_terrain_9(length, width, field_resolution, difficulty):
    """Combination of varying height platforms and angle ramps for the quadruped to climb up and jump across."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up dimensions for platforms and ramps
    platform_length = 0.8 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width_min, platform_width_max = 0.8, 1.2
    platform_width_min = m_to_idx(platform_width_min)
    platform_width_max = m_to_idx(platform_width_max)
    platform_height_min, platform_height_max = 0.1, 0.3
    platform_height_min = platform_height_min * difficulty
    platform_height_max = platform_height_max * difficulty
    gap_length = 0.4 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)
    
    ramp_length = 1.2 - 0.2 * difficulty
    ramp_length = m_to_idx(ramp_length)
    ramp_height_min, ramp_height_max = 0.1, 0.35
    ramp_height_min = ramp_height_min * difficulty
    ramp_height_max = ramp_height_max * difficulty
    
    cur_x = m_to_idx(2)   # Start position after the spawn
    mid_y = m_to_idx(width // 2)
    
    def add_platform(x, y_mid):
        """Adds a platform."""
        half_width = np.random.randint(platform_width_min//2, platform_width_max//2)
        height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x:x + platform_length, y_mid - half_width:y_mid + half_width] = height
        return x + platform_length, height
    
    def add_ramp(x, y_mid, height, slope):
        """Adds a ramp."""
        half_width = np.random.randint(platform_width_min//2, platform_width_max//2)
        rem_height = slope * (height_field.shape[0] - x)
        rem_height = min(rem_height, height * 0.5)
        new_height = height + rem_height
        heights = np.linspace(height, new_height, ramp_length)
        for i in range(ramp_length):
            height_field[x + i, y_mid - half_width:y_mid + half_width] = heights[i]
        return x + ramp_length, new_height
    
    # Make the first goal just in front to start
    goals[0] = [m_to_idx(2) - m_to_idx(0.5), mid_y]
    
    # Create a series of platforms and ramps
    for i in range(7):
        if i % 2 == 0:
            cur_x, cur_height = add_platform(cur_x, mid_y)
        else:
            cur_x, cur_height = add_ramp(cur_x, mid_y, cur_height, 0.5)
        if i < 7-1:  # Add goals only for the first 7
            goals[i + 1] = [cur_x - platform_length // 2, mid_y]
        cur_x += gap_length  # Leave a gap after each obstacle

    # Add final goal slightly beyond the last obstacle
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    return height_field, goals

# INSERT TERRAIN FUNCTION DEFINITIONS HERE
