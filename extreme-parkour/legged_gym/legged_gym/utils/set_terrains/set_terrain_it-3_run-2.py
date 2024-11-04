
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
    """Series of narrow beams and varied-height platforms with undulating terrain for the robot to climb up and navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up beam and platform dimensions
    beam_length = 1.0 - 0.3 * difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = np.random.uniform(0.4, 0.6)
    beam_width = m_to_idx(beam_width)
    beam_height_min, beam_height_max = 0.1 + 0.2 * difficulty, 0.3 + 0.25 * difficulty
    
    platform_width = 0.8 + 0.2 * difficulty  # Platforms between the beams
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.3 + 0.25 * difficulty
    
    gap_length = 0.2 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, mid_y, height):
        half_width = beam_width // 2
        height_field[start_x:end_x, mid_y - half_width: mid_y + half_width] = height

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        height_field[start_x:end_x, mid_y - half_width: mid_y + half_width] = height

    dx_min, dx_max = -0.05, 0.05
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.1, 0.1
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)
    
    height_field[0:m_to_idx(2), :] = 0  # Flat spawn area
    
    goals[0] = [m_to_idx(1), mid_y]
    
    cur_x = m_to_idx(2)
    i = 1
    while i < 7:  # Set up structure: platform-beam-platform-beam...
        dx, dy = np.random.randint(dx_min, dx_max), np.random.randint(dy_min, dy_max)
        
        if i % 2 == 1:  # Add a platform
            height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, cur_x + platform_width, mid_y + dy, height)
            goals[i] = [cur_x + platform_width / 2, mid_y + dy]
            cur_x += platform_width + gap_length
        else:  # Add a beam
            height = np.random.uniform(beam_height_min, beam_height_max)
            add_beam(cur_x, cur_x + beam_length, mid_y + dy, height)
            goals[i] = [cur_x + beam_length / 2, mid_y + dy]
            cur_x += beam_length + gap_length

        i += 1
    
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0  # Flat area after last obstacle
    
    return height_field, goals

def set_terrain_1(length, width, field_resolution, difficulty):
    """Combines varied-height platforms with narrow bridges to test balance and stepping accuracy."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Parameters for platforms and bridges
    platform_length = m_to_idx(0.8)
    bridge_length = m_to_idx(0.6) + m_to_idx(0.4 * difficulty)
    total_length = platform_length + bridge_length
    platform_width = m_to_idx(1.0)
    bridge_width = m_to_idx(0.4) - m_to_idx(0.2 * difficulty)
    platform_height_min, platform_height_max = 0.05 + 0.15 * difficulty, 0.1 + 0.25 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, length, width, height, mid_y):
        half_width = width // 2
        height_field[start_x:start_x+length, mid_y-half_width:mid_y+half_width] = height

    def add_bridge(start_x, length, width, mid_y):
        half_width = width // 2
        height_field[start_x:start_x+length, mid_y-half_width:mid_y+half_width] = 0.0

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Create varied height platforms with narrow bridges
    cur_x = spawn_length
    for i in range(7):
        platform_height = np.random.uniform(platform_height_min, platform_height_max)

        # Add platform
        add_platform(cur_x, platform_length, platform_width, platform_height, mid_y)
        goals[i+1] = [cur_x + platform_length // 2, mid_y]

        # Add connecting bridge
        cur_x += platform_length
        add_bridge(cur_x, bridge_length, bridge_width, mid_y)
        
        # Continue to the next platform
        cur_x += bridge_length

    # Fill the rest of the terrain to flat ground
    height_field[cur_x:, :] = 0
    goals[-1] = [m_to_idx(length) - m_to_idx(0.5), mid_y]

    return height_field, goals

def set_terrain_2(length, width, field_resolution, difficulty):
    """Complex course with staggered elevated platforms and sideways facing ramps to challenge balance, precision, and incline traversal."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions
    platform_length = 0.8 + 0.4 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.2 + 0.2 * difficulty)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.3 + 0.5 * difficulty
    gap_length = 0.2 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

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
        ramp_height = np.linspace(0, height, x2 - x1)[::direction]
        ramp_height = ramp_height[:, None]  # Broadcasting for y-axis width
        height_field[x1:x2, y1:y2] = ramp_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Set remaining area to potential pits to enforce the robot to stay on platforms
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    for i in range(6):  # Set up platforms and ramps
        if i % 2 == 0:  # Platforms at even indices
            platform_height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)
            height = platform_height
        else:  # Ramps at odd indices
            ramp_height = np.random.uniform(platform_height_min, platform_height_max)
            direction = 1 if i % 4 == 1 else -1  # Just alternating the direction
            add_ramp(cur_x, cur_x + platform_length, mid_y, direction, ramp_height)
            height = ramp_height

        # Place goals in the middle of each platform or ramp
        goals[i+1] = [cur_x + platform_length / 2, mid_y]

        # Add gap
        cur_x += platform_length + gap_length

    # Add final goal behind the last platform/ramp, fill in remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_3(length, width, field_resolution, difficulty):
    """Varied course with multiple raised platforms, narrow beams, and sideways-facing ramps to improve precision and climbing skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform, beam, and ramp dimensions
    platform_length = 0.8 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.2)
    platform_width = m_to_idx(platform_width)
    beam_width = m_to_idx(0.4 - 0.1 * difficulty)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.2 + 0.3 * difficulty
    ramp_height_min, ramp_height_max = 0.2 + 0.2 * difficulty, 0.3 + 0.4 * difficulty
    gap_length = 0.2 + 0.3 * difficulty
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
        height_field[x1:x2, y1:y2] = 0.1 + 0.2 * difficulty

    def add_ramp(start_x, end_x, mid_y, direction):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        slant = np.linspace(0, ramp_height, num=x2-x1)[::direction]
        slant = slant[:, None]
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.0, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(2):  # Create 2 platforms
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

    for i in range(2, 4):  # Create 2 beams
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_beam(cur_x, cur_x + platform_length + dx, mid_y + dy)
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

    for i in range(4, 7):  # Create 3 sideways-facing ramps
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        direction = (-1) ** i
        dy = dy * direction
        add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, direction)
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_4(length, width, field_resolution, difficulty):
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

def set_terrain_5(length, width, field_resolution, difficulty):
    """Zigzag raised platforms with varying heights for the robot to navigate and climb."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Dimensions for platforms
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.6)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.2 * difficulty, 0.1 + 0.3 * difficulty
    gap_length = 0.1 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    def add_platform(start_x, end_x, start_y, end_y):
        height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[start_x:end_x, start_y:end_y] = height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    mid_y = m_to_idx(width) // 2

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Setup platforms in a zigzag pattern
    cur_x = spawn_length
    for i in range(6):  # Set up 6 platforms
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        y_offset = (i % 2) * m_to_idx(3) - m_to_idx(1.5)  # Alternate between offsets on the y-axis
        start_y = mid_y + y_offset
        end_y = start_y + platform_width
        
        add_platform(cur_x, cur_x + platform_length + dx, start_y, end_y)

        # Put goal in the center of the platform
        goals[i + 1] = [cur_x + (platform_length + dx) // 2, (start_y + end_y) // 2]

        cur_x += platform_length + dx + gap_length

    # Add final goal behind the last platform and set a flat terrain
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_6(length, width, field_resolution, difficulty):
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

def set_terrain_7(length, width, field_resolution, difficulty):
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

def set_terrain_8(length, width, field_resolution, difficulty):
    """Varied platforms, narrow beams, and tilted ramps for the robot to navigate, jump, and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up obstacle dimensions
    step_length = 0.4 + 0.1 * difficulty
    step_length = m_to_idx(step_length)
    step_width = 0.3 + 0.3 * difficulty
    step_width = m_to_idx(step_width)
    step_height_min, step_height_max = 0.1, 0.25 + 0.15 * difficulty
    narrow_beam_length = 0.8 + 0.2 * difficulty
    narrow_beam_length = m_to_idx(narrow_beam_length)
    narrow_beam_width = 0.3
    narrow_beam_width = m_to_idx(narrow_beam_width)
    beam_height_min, beam_height_max = 0.2 + 0.2 * difficulty, 0.35 + 0.3 * difficulty
    platform_length = 0.8 + 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.6)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.2 + 0.4 * difficulty, 0.05 + 0.6 * difficulty
    ramp_length = 1.0
    ramp_length = m_to_idx(ramp_length)
    ramp_height = 0.2 + 0.4 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_stepping_stone(start_x, mid_y):
        half_width = step_width // 2
        x1 = start_x
        x2 = start_x + step_length
        y1 = mid_y - half_width
        y2 = mid_y + half_width
        step_height = np.random.uniform(step_height_min, step_height_max)
        height_field[x1:x2, y1:y2] = step_height

    def add_narrow_beam(start_x, mid_y, height):
        half_width = narrow_beam_width // 2
        x1 = start_x
        x2 = start_x + narrow_beam_length
        y1 = mid_y - half_width
        y2 = mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_platform(start_x, mid_y):
        half_width = platform_width // 2
        x1 = start_x
        x2 = start_x + platform_length
        y1 = mid_y - half_width
        y2 = mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_ramp(start_x, mid_y, height):
        half_width = platform_width // 2
        x1 = start_x
        x2 = start_x + ramp_length
        y1 = mid_y - half_width
        y2 = mid_y + half_width
        height_field[x1:x2, y1:y2] = np.linspace(0, height, x2-x1)[:, None]

    dx_min = m_to_idx(-0.2)
    dx_max = m_to_idx(0.2)
    dy_min = m_to_idx(-0.2)
    dy_max = m_to_idx(0.2)

    # Set spawn area to flat ground and first goal at the spawn
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    # Stepping stones
    for i in range(2):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_stepping_stone(cur_x, mid_y + dy)
        goals[i+1] = [cur_x + step_length / 2, mid_y + dy]
        cur_x += step_length + dx + step_length

    # Narrow beams
    for i in range(2):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        beam_height = np.random.uniform(beam_height_min, beam_height_max)
        add_narrow_beam(cur_x, mid_y + dy, beam_height)
        goals[i+3] = [cur_x + narrow_beam_length / 2, mid_y + dy]
        cur_x += narrow_beam_length + dx + narrow_beam_length

    # Raised platforms
    for i in range(2):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, mid_y + dy)
        goals[i+5] = [cur_x + platform_length / 2, mid_y + dy]
        cur_x += platform_length + dx + step_length
    
    # Tilted ramp
    dx = np.random.randint(dx_min, dx_max)
    dy = np.random.randint(dy_min, dy_max)
    add_ramp(cur_x, mid_y + dy, ramp_height)
    goals[-2] = [cur_x + ramp_length / 2, mid_y + dy]
    cur_x += ramp_length + dx + step_length

    # Final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_9(length, width, field_resolution, difficulty):
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

# INSERT TERRAIN FUNCTION DEFINITIONS HERE
