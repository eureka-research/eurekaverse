
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
    """Alternating narrow and wide platforms with varied heights, staggered beams, and offset steps."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Parameters for obstacles
    platform_min_width = 0.4  # minimum width for narrow beams
    platform_max_width = 1.8  # maximum width for wider platforms
    platform_min_height = 0.1  # minimum height for platforms
    platform_max_height = 0.6 * difficulty  # maximum height increasing with difficulty
    gap_length_base = 0.2  # base gap length in meters
    gap_length_incr = 0.2 * difficulty  # gap length increment based on difficulty

    def add_platform(start_x, end_x, y_center, is_narrow=False):
        """Adds a platform with specified width and height to the height_field."""
        width = np.random.uniform(platform_min_width, platform_max_width if not is_narrow else 0.6)
        half_width = m_to_idx(width) // 2
        x1, x2 = start_x, end_x
        y1, y2 = y_center - half_width, y_center + half_width
        height = np.random.uniform(platform_min_height, platform_max_height)
        height_field[x1:x2, y1:y2] = height

    def add_step(start_x, mid_y):
        """Adds an offset step to the height_field."""
        width = np.random.uniform(platform_min_width, platform_max_width)
        length = m_to_idx(0.4)  # step length
        height = np.random.uniform(platform_min_height, platform_max_height)
        
        half_width = m_to_idx(width) // 2
        y1, y2 = mid_y - half_width, mid_y + half_width
        
        for sign in [-1, 1]:
            offset_y = y2 if sign == 1 else y1 - length
            height_field[start_x:start_x + length, offset_y:offset_y + length] = height * sign

    mid_y = m_to_idx(width) // 2
    spawn_length = m_to_idx(2)
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Set the spawn area to flat ground
    height_field[0:spawn_length, :] = 0

    cur_x = spawn_length
    segments = 7  # Number of segments

    for i in range(segments):
        is_narrow = (i % 2 == 0)
        segment_length = np.random.uniform(0.8, 1.4)
        segment_length_idx = m_to_idx(segment_length)
        add_platform(cur_x, cur_x + segment_length_idx, mid_y, is_narrow)

        # Place goal appropriately at each segment.
        goals[i+1] = [cur_x + segment_length_idx // 2, mid_y]

        # Between platforms, add steps periodically for more challenges
        if i % 2 == 1:
            add_step(cur_x + segment_length_idx, mid_y)
        
        # Add gap
        gap_length = gap_length_base + gap_length_incr
        cur_x += segment_length_idx + m_to_idx(gap_length)
    
    # Add the final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_1(length, width, field_resolution, difficulty):
    """Series of platforms with undulating connections for the robot to navigate and balance on."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform and undulation dimensions
    platform_length = np.random.uniform(0.8, 1.2 - 0.2 * difficulty)
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.5)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1, 0.2 + 0.4 * difficulty
    undulation_amplitude = 0.05 + 0.1 * difficulty
    gap_length = np.random.uniform(0.2, 0.4 + 0.3 * difficulty)
    gap_length = m_to_idx(gap_length)
    
    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_undulation(start_x, end_x):
        x1, x2 = start_x, end_x
        y_indices = np.arange(0, m_to_idx(width))
        undulation_heights = undulation_amplitude * np.sin(np.linspace(0, 2 * np.pi, y_indices.size))
        height_field[x1:x2, :] += undulation_heights[np.newaxis, :]
    
    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]
    
    cur_x = spawn_length

    for i in range(4):  # Set up alternating platforms and undulating terrain
        add_platform(cur_x, cur_x + platform_length, mid_y)
        goals[i+1] = [cur_x + platform_length / 2, mid_y]
        
        cur_x += platform_length
        cur_x += gap_length

        add_undulation(cur_x, cur_x + platform_length)
        goals[i+2] = [cur_x + platform_length / 2, mid_y]
        
        cur_x += platform_length
        cur_x += gap_length

    # Final goal placement
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_2(length, width, field_resolution, difficulty):
    """Staggered elevated platforms and gaps testing balance, precision, and jumping abilities."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions
    platform_length = m_to_idx(1.0 - 0.3 * difficulty)
    platform_width = m_to_idx(np.random.uniform(0.6, 1.2))
    platform_height_min = 0.0 + 0.15 * difficulty
    platform_height_max = 0.2 + 0.25 * difficulty
    gap_length = m_to_idx(0.2 + 0.5 * difficulty)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, mid_y, height):
        half_width = platform_width // 2
        end_x = start_x + platform_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[start_x:end_x, y1:y2] = height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Create staggered elevated platforms
    cur_x = spawn_length
    for i in range(6):  # Set up 6 platforms
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        add_platform(cur_x, mid_y + dy, platform_height)

        # Place goal in the center of each platform
        goals[i+1] = [cur_x + platform_length / 2 + dx, mid_y + dy]

        # Add gap
        cur_x += platform_length + gap_length + dx

    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    return height_field, goals

def set_terrain_3(length, width, field_resolution, difficulty):
    """Mixed platforms and ramps of varying heights, widths, and gap lengths for the quadruped to jump, climb or navigate through."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform and ramp dimensions
    platform_length_min = 0.8 - 0.3 * difficulty
    platform_length_max = 1.2 - 0.3 * difficulty
    platform_width_range = (1.0, 1.5)
    platform_height_min, platform_height_max = 0.0 + 0.3 * difficulty, 0.4 + 0.3 * difficulty
    ramp_height_min, ramp_height_max = 0.1 + 0.3 * difficulty, 0.35 + 0.3 * difficulty
    gap_length_min = 0.1 + 0.3 * difficulty
    gap_length_max = 0.4 + 0.6 * difficulty

    platform_length_min = m_to_idx(platform_length_min)
    platform_length_max = m_to_idx(platform_length_max)
    platform_width_range = m_to_idx(platform_width_range)
    gap_length_min = m_to_idx(gap_length_min)
    gap_length_max = m_to_idx(gap_length_max)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = np.random.randint(*platform_width_range) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_ramp(start_x, end_x, mid_y, direction):
        half_width = np.random.randint(*platform_width_range) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        slant = np.linspace(0, ramp_height, num=y2-y1)[::direction]
        slant = slant[None, :]  # Add a dimension for broadcasting to x
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.2, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.0, 0.3  # Keep dy variations to maintain platform/ramp configurations
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set the spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    for i in range(7):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        gap_length = np.random.randint(gap_length_min, gap_length_max)
        
        if i % 2 == 0:
            # Add platform
            platform_length = np.random.randint(platform_length_min, platform_length_max)
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i+1] = [cur_x + (platform_length + dx) // 2, mid_y + dy]
            cur_x += platform_length + dx + gap_length
        else:
            # Add ramp
            ramp_length = np.random.randint(platform_length_min, platform_length_max)
            direction = (-1) ** i  # Alternate left and right ramps
            add_ramp(cur_x, cur_x + ramp_length + dx, mid_y + dy, direction)
            goals[i+1] = [cur_x + (ramp_length + dx) // 2, mid_y + dy]
            cur_x += ramp_length + dx + gap_length

    # Add the final goal behind the last obstacle, filling in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_4(length, width, field_resolution, difficulty):
    """Staggered platforms with varied sizes and heights to improve navigating uneven terrain and jumps."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.9, 1.2)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 * difficulty, 0.3 * difficulty
    gap_length = 0.2 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    dx_min, dx_max = -0.2, 0.3
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Set remaining area to be a pit with varying base height
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    for i in range(6):  # Set up staggered platforms
        platform_mid_y = mid_y + np.random.randint(dy_min, dy_max)
        dx = np.random.randint(dx_min, dx_max)
        add_platform(cur_x, cur_x + platform_length + dx, platform_mid_y)

        # Put goal in the center of the platform
        goals[i+1] = [cur_x + (platform_length + dx) / 2, platform_mid_y]

        # Add gap
        cur_x += platform_length + dx + gap_length
    
    # Add final goal behind the last platform, fill in remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_5(length, width, field_resolution, difficulty):
    """Staggered platforms, uneven terrain with height variations, narrow beams, and ramps for advanced traversal techniques."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set ramp, beam, and platform dimensions based on difficulty
    platform_length = 0.8 + 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.2)
    platform_width = m_to_idx(platform_width)
    platform_height_min = 0.1 * difficulty
    platform_height_max = 0.6 * difficulty
    gap_length = 0.3 + 0.7 * difficulty
    gap_length = m_to_idx(gap_length)
    
    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, platform_width, platform_height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = platform_height

    def add_narrow_beam(start_x, end_x, mid_y, beam_width, beam_height):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = beam_height

    def add_ramp(start_x, end_x, mid_y, ramp_width, ramp_height, direction):
        half_width = ramp_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slant = np.linspace(0, ramp_height, num=x2-x1)[::direction]
        slant = slant[:, None]  # Add a dimension for broadcasting to y
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length

    # Add platforms and beams alternatingly
    for i in range(6):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        component_length = platform_length + dx

        if i % 2 == 0:  # Even indices: platforms
            platform_height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, cur_x + component_length, mid_y + dy, platform_width, platform_height)
        else:  # Odd indices: narrow beams
            beam_width = 0.4 + 0.4 * difficulty
            beam_width = m_to_idx(beam_width)
            beam_height = np.random.uniform(platform_height_min, platform_height_max)
            add_narrow_beam(cur_x, cur_x + component_length, mid_y + dy, beam_width, beam_height)
        
        goals[i+1] = [cur_x + component_length / 2, mid_y + dy]
        cur_x += component_length + gap_length
    
    # Add final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_6(length, width, field_resolution, difficulty):
    """Series of raised platforms and variable-width pathways to test the quadruped's climbing, balancing and jumping skills."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions
    # We make the platform height near 0.2 at minimum difficulty, rising at higher difficulty levels
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_height_min = 0.2
    platform_height_max = 0.7 * difficulty
    
    # Set the width of the pathways and gaps between the platforms
    platform_width_min = np.random.uniform(0.8, 1.0)
    platform_width_max = np.random.uniform(1.2, 1.4)
    platform_width_min, platform_width_max = m_to_idx([platform_width_min, platform_width_max])
    gap_length = np.random.uniform(0.2, 0.8)
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, y_start, y_end, height):
        height_field[start_x:end_x, y_start:y_end] = height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx([dx_min, dx_max])
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx([dy_min, dy_max])

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(7):  # Set up 7 platforms
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        width = np.random.randint(platform_width_min, platform_width_max)
        height = np.random.uniform(platform_height_min, platform_height_max)
        
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy - width//2, mid_y + dy + width//2, height)
        goals[i+1] = [cur_x + (platform_length + dx) // 2, mid_y + dy]
        
        cur_x += platform_length + dx + gap_length

    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_7(length, width, field_resolution, difficulty):
    """Challenging balance on narrow beams with gaps and varying heights."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Parameters (increase obstacle complexity based on difficulty)
    platform_width_min, platform_width_max = 0.3, 0.5  # Narrower beams for balance testing
    gap_width = 0.4 + 0.6 * difficulty  # Increase gap width with difficulty
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.15 + 0.35 * difficulty

    platform_width_min, platform_width_max = m_to_idx([platform_width_min, platform_width_max])
    gap_width = m_to_idx(gap_width)
    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, length, width, height, mid_y, offset_y=0):
        half_width = width // 2
        height_field[start_x:start_x+length, mid_y - half_width + offset_y : mid_y + half_width + offset_y] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at the spawn point

    # Create terrain
    cur_x = spawn_length
    obstacle_count = 0

    while obstacle_count < 7:
        # Determine platform parameters
        platform_length = m_to_idx(0.8)
        platform_width = np.random.randint(platform_width_min, platform_width_max)
        platform_height = np.random.uniform(platform_height_min, platform_height_max)

        # Create platform
        add_platform(cur_x, platform_length, platform_width, platform_height, mid_y)

        # Set goal on the platform
        goals[obstacle_count+1] = [cur_x + platform_length // 2, mid_y]

        # Add gap before the next platform leading to variability in difficulty
        cur_x += platform_length + gap_width

        obstacle_count += 1

    # Provide extra challenge before the final goal
    final_platform_height = max(platform_height_min, platform_height_max)
    cur_x += gap_width
    add_platform(cur_x, platform_length, platform_width_max, final_platform_height, mid_y)
    goals[-1] = [cur_x + platform_length // 2, mid_y]

    # Fill the rest of the terrain to flat ground
    height_field[cur_x+platform_length:, :] = 0

    return height_field, goals

def set_terrain_8(length, width, field_resolution, difficulty):
    """Zig-Zag Pathways with Staggered Blocks for balance and precise movement tests."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up block dimensions
    block_length = 0.6 + 0.2 * difficulty  # Length based on difficulty
    block_length = m_to_idx(block_length)
    block_width = 0.2 + 0.4 * difficulty  # Width based on difficulty
    block_width = m_to_idx(block_width)
    block_height_min, block_height_max = 0.1 * difficulty, 0.3 * difficulty  # Variable height based on difficulty
    pathway_width = m_to_idx(0.6)  # Slightly wider pathway for breathing room

    mid_y = m_to_idx(width) // 2

    def add_block(start_x, end_x, start_y, height):
        height_field[start_x:end_x, start_y:start_y + block_width] = height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_offset = m_to_idx(0.6)  # Zig-zag offset

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(7):  # Set up 7 blocks
        dx = np.random.randint(dx_min, dx_max)
        dy = dy_offset if i % 2 == 0 else -dy_offset  # Alternate sideways direction
        height = np.random.uniform(block_height_min, block_height_max)

        add_block(cur_x, cur_x + block_length + dx, mid_y + dy, height)

        # Put goal in the center of the block
        goals[i + 1] = [cur_x + (block_length + dx) / 2, mid_y + dy + block_width // 2]

        cur_x += block_length + dx + pathway_width
    
    # Final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_9(length, width, field_resolution, difficulty):
    """Multiple types of obstacles, including steps, jumps, and narrow beams for the quadruped to navigate through."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]
    
    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    
    # Define obstacle dimensions
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.6, 1.2)  # Narrower width for beam-like obstacles
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.05 + 0.15 * difficulty, 0.15 + 0.35 * difficulty
    gap_length = 0.1 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)
    
    mid_y = m_to_idx(width) // 2
    
    def add_platform(start_x, end_x, mid_y, height):
        """Adds a platform (rectangle) of a given height at the specified x, y coordinates."""
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height
    
    def add_beam(start_x, end_x, mid_y, height):
        """Adds a narrow beam with a given height at specified x, y coordinates."""
        beam_width = m_to_idx(0.2)
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height
    
    # Initialize terrain with flat ground and set spawn area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]
    
    cur_x = spawn_length
    
    for i in range(6):
        dx = m_to_idx(0.1 * (-1 if i % 2 == 0 else 1))
        dy = m_to_idx(0.2 * (-1 if i % 2 == 1 else 1))
        obstacle_type = np.random.choice(['platform', 'beam'], p=[0.7, 0.3])
        obstacle_height = np.random.uniform(platform_height_min, platform_height_max)
        
        if obstacle_type == 'platform':
            add_platform(cur_x, cur_x + platform_length, mid_y + dy, obstacle_height)
        else:
            add_beam(cur_x, cur_x + platform_length, mid_y + dy, obstacle_height)
        
        goals[i+1] = [cur_x + platform_length / 2, mid_y + dy]
        
        cur_x += platform_length + gap_length
    
    # Set remaining to flat ground after the last gap
    height_field[cur_x:, :] = 0
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    
    return height_field, goals

# INSERT TERRAIN FUNCTION DEFINITIONS HERE
