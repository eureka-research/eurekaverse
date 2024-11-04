
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
    """Mixed sequence of platforms and ramps with varying heights and moderate gaps for the robot to climb and navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and ramp dimensions
    platform_length = 1.2 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    ramp_length = 1.5 - 0.5 * difficulty
    ramp_length = m_to_idx(ramp_length)
    platform_width = np.random.uniform(1.0, 1.2)
    platform_width = m_to_idx(platform_width)

    platform_height_min, platform_height_max = 0.0 + 0.3 * difficulty, 0.1 + 0.4 * difficulty
    ramp_height_min, ramp_height_max = 0.0 + 0.4 * difficulty, 0.1 + 0.5 * difficulty
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
        slant = np.linspace(0, ramp_height, num=x2-x1)[::-1 if direction == -1 else 1]
        slant = slant[:, None]  # Add a dimension for broadcasting in y
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

    cur_x = spawn_length
    last_type = 'platform'
    for i in range(6):
        if last_type == 'platform':
            if np.random.rand() > 0.5:
                last_type = 'ramp'
                dx = np.random.randint(dx_min, dx_max)
                dy = np.random.randint(dy_min, dy_max)
                direction = (-1) ** i  # Alternate left and right ramps
                dy = dy * direction  # Alternate positive and negative y offsets

                add_ramp(cur_x, cur_x + ramp_length + dx, mid_y + dy, direction)
                goals[i + 1] = [cur_x + (ramp_length + dx) / 2, mid_y + dy]
                cur_x += ramp_length + dx + gap_length
            else:
                last_type = 'platform'
                dx = np.random.randint(dx_min, dx_max)
                dy = np.random.randint(dy_min, dy_max)

                add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
                goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
                cur_x += platform_length + dx + gap_length
        else:
            last_type = 'platform'
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)

            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
            cur_x += platform_length + dx + gap_length

    # Add final goal behind the last structure, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_1(length, width, field_resolution, difficulty):
    """Complex alternating heights course with ramps for improved navigation and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up dimensions for platforms and ramps
    platform_length = 1.2 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.4)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.3 * difficulty, 0.3 + 0.4 * difficulty
    gap_length = 0.2 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    ramp_height_min, ramp_height_max = 0.1 + 0.4 * difficulty, 0.2 + 0.5 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_ramp(start_x, end_x, mid_y, slope_direction):
        half_width = platform_width // 2
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slant = np.linspace(0, ramp_height, num=y2-y1)[::slope_direction]
        slant = slant[None, :]  # Add a dimension for broadcasting to x
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.0, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # Initialize first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Set remaining area to low depth pit
    height_field[spawn_length:, :] = -1.0

    # Add initial platform
    cur_x = spawn_length
    dx = np.random.randint(dx_min, dx_max)
    dy = np.random.randint(dy_min, dy_max)
    add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
    goals[1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
    cur_x += platform_length + dx + gap_length

    # Add alternating ramps and staggered platforms
    for i in range(2, 7):  # Set up 5 alternating obstacles
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        if i % 2 == 0:  # Even indices add a platform
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
        else:  # Odd indices add a ramp
            slope_direction = (-1) ** (i // 2)  # Alternate slope direction
            add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, slope_direction)
        
        goals[i] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

    # Add final goal at the end past the last obstacle, fill remaining area with flat ground
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_2(length, width, field_resolution, difficulty):
    """Alternating elevated platforms and sloped ramps for the robot to climb, balance, and navigate through varying challenges."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Adjusting dimensions and height ranges
    platform_length = 1.0 - 0.15 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.3)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.2 + 0.2 * difficulty, 0.3 + 0.4 * difficulty
    gap_length = 0.2 + 0.8 * difficulty
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
        slant = np.linspace(0, ramp_height, num=y2-y1)[::direction]
        slant = slant[None, :]  # Add a dimension for broadcasting to x
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = m_to_idx(-0.2), m_to_idx(0.2)
    dy_min, dy_max = m_to_idx(0.0), m_to_idx(0.4)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Set start goal
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    alternating = True  # To alternate between platforms and ramps
    for i in range(6):  # Set up platforms and ramps
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        if alternating:
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
        else:
            direction = (-1) ** i  # Alternate gradient of ramp
            add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, direction)
        
        # Set goals in center of obstacles
        goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        cur_x += platform_length + dx + gap_length
        alternating = not alternating
    
    # Add final goal behind the last obstacle, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_3(length, width, field_resolution, difficulty):
    """Combines stepping stones, wide bridges, varied-height platforms, and angular ramps to test balance, climbing, and jumping abilities."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, width, height):
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_ramp(start_x, end_x, mid_y, width, height_max, direction):
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.linspace(0, height_max, num=y2-y1)[::direction]
        ramp_height = ramp_height[None, :]  # Add a dimension for broadcasting
        height_field[x1:x2, y1:y2] = ramp_height

    # Setup platform properties
    platform_length_base = 1.2
    platform_width_base = 0.6
    platform_height_base = 0.1

    # Adjust platform properties for difficulty
    platform_length = m_to_idx(platform_length_base - 0.3 * difficulty)
    platform_width = m_to_idx(platform_width_base + 0.4 * difficulty)
    platform_height_min, platform_height_max = platform_height_base * (1 + difficulty), platform_height_base * (3 + difficulty)

    gap_distance = m_to_idx(0.5 + difficulty)

    # Set initial flat ground for spawning
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    # Create stepping stones
    for i in range(3):
        next_x = cur_x + gap_distance
        add_platform(cur_x, cur_x + platform_length, mid_y, platform_width // 2, platform_height_base + i * 0.1 * difficulty)
        goals[i + 1] = [cur_x + platform_length // 2, mid_y]
        cur_x = next_x

    # Create two wider bridges with varying heights
    platform_length_bridge = platform_length * 2
    for i in range(3, 5):
        next_x = cur_x + gap_distance
        height = platform_height_base + 0.2 * i * difficulty
        add_platform(cur_x, cur_x + platform_length_bridge, mid_y, platform_width, height)
        goals[i + 1] = [cur_x + platform_length_bridge // 2, mid_y]
        cur_x = next_x

    # Create angular ramps
    for i in range(5, 7):
        draw = (-1)**(i + 1)
        ramp_direction = draw
        ramp_height = platform_height_base + 0.3 * difficulty
        add_ramp(cur_x, cur_x + platform_length, mid_y, platform_width, ramp_height, ramp_direction)
        goals[i + 1] = [cur_x + platform_length // 2, mid_y + ramp_direction]
        cur_x += platform_length + gap_distance

    # Final goal at the end of the course
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_4(length, width, field_resolution, difficulty):
    """Zigzag elevated platforms with varying heights for the robot to balance and jump across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform parameters
    platform_length = 0.8 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.2)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.3 * difficulty, 0.1 + 0.5 * difficulty
    gap_length = 0.1 + 0.4 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.0, 0.5
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)
    
    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(6):  # Setting up 6 zigzag platforms
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max) * (-1) ** i  # Alternate left and right
        height = np.random.uniform(platform_height_min, platform_height_max)

        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, height)
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += platform_length + dx + gap_length

    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_5(length, width, field_resolution, difficulty):
    """Combination of varied-width platforms and tilted platforms to increase navigation challenge."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    length_idx = m_to_idx(length)
    width_idx = m_to_idx(width)
    height_field = np.zeros((length_idx, width_idx))
    goals = np.zeros((8, 2))

    platform_width_min = 0.8
    platform_width_max = 1.6
    platform_length = 1.2 - 0.5 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_height_min = 0.1
    platform_height_max = 0.5 * difficulty
    slope_length = 0.8 + 0.2 * difficulty
    slope_length = m_to_idx(slope_length)
    gap_length = 0.4 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)
    
    mid_y = width_idx // 2

    def add_platform(start_x, end_x, mid_y, platform_width, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_tilted_platform(start_x, end_x, mid_y, tilt_angle):
        platform_width = m_to_idx(np.random.uniform(platform_width_min, platform_width_max))
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        # Create a slope within this range
        slope_direction = 1 if np.random.rand() > 0.5 else -1
        tilt = np.linspace(0, tilt_angle, x2 - x1)[:, None] * slope_direction
        height_field[x1:x2, y1:y2] += tilt

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to a flat ground
    spawn_length = m_to_idx(2)
    height_field[:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(6):
        platform_width = m_to_idx(np.random.uniform(platform_width_min, platform_width_max))
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        if i % 2 == 0:
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_width, platform_height)
        else:
            tilt_angle = platform_height_max
            add_tilted_platform(cur_x, cur_x + slope_length + dx, mid_y + dy, tilt_angle)
        
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_6(length, width, field_resolution, difficulty):
    """Series of alternating inclined ramps and narrow platforms to test precision, climbing, and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up ramp and narrow platform dimensions
    ramp_length = 0.8 + 0.4 * difficulty  # increasing length with difficulty
    ramp_length = m_to_idx(ramp_length)
    ramp_width = np.random.uniform(0.4, 0.6)
    ramp_width = m_to_idx(ramp_width)
    ramp_height_min, ramp_height_max = 0.1 + 0.2 * difficulty, 0.2 + 0.4 * difficulty
    
    platform_length = 0.7 + 0.3 * difficulty  # narrow platforms
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.5, 0.7)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.2 + 0.4 * difficulty

    gap_length = 0.2 + 0.5 * difficulty  # increased gap length
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_ramp(start_x, end_x, mid_y, inclination):
        half_width = ramp_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        slant = np.linspace(0, ramp_height * inclination, num=x2-x1)
        slant = slant[:, None]  # for broadcasting to y
        height_field[x1:x2, y1:y2] = slant

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    dx_min, dx_max = m_to_idx(-0.1), m_to_idx(0.1)
    dy_min, dy_max = m_to_idx(-0.4), m_to_idx(0.4)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(7):  # 4 ramps and 3 platforms
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        if i % 2 == 0:  # Add ramp
            add_ramp(cur_x, cur_x + ramp_length + dx, mid_y + dy, inclination=1 if i % 4 == 0 else -1)
            goals[i + 1] = [cur_x + (ramp_length + dx) // 2, mid_y + dy]
            cur_x += ramp_length + dx + gap_length
        else:  # Add platform
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i + 1] = [cur_x + (platform_length + dx) // 2, mid_y + dy]
            cur_x += platform_length + dx + gap_length

    # Add final goal behind the last obstacle, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_7(length, width, field_resolution, difficulty):
    """Series of inclined ramps, narrow passageways, and platforms to test climbing, balancing, and navigation skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform and ramp dimensions
    platform_length = m_to_idx(1.2 - 0.2 * difficulty)
    platform_width = m_to_idx(0.6)
    platform_height_min = 0.2 * difficulty
    platform_height_max = 0.4 * difficulty
    gap_length = m_to_idx(0.3 + 0.5 * difficulty)
    ramp_length = m_to_idx(1.0 - 0.3 * difficulty)
    ramp_height_min = 0.2 * difficulty
    ramp_height_max = 0.5 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, start_y, height):
        y1, y2 = start_y - platform_width // 2, start_y + platform_width // 2
        height_field[start_x:end_x, y1:y2] = height

    def add_ramp(start_x, end_x, start_y, max_height, ascending=True):
        y1, y2 = start_y - platform_width // 2, start_y + platform_width // 2
        height_diff = np.linspace(0, max_height, end_x - start_x) if ascending else np.linspace(max_height, 0, end_x - start_x)
        height_field[start_x:end_x, y1:y2] = height_diff[:, None]

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    alternating_plateforms = m_to_idx(0.2)
    for i in range(6):
        if i % 2 == 0:  # Add platforms
            platform_height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)
            goals[i+1] = [cur_x + platform_length // 2, mid_y]
            cur_x += platform_length + gap_length
        else:  # Add ramps
            ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
            add_ramp(cur_x, cur_x + ramp_length, mid_y, ramp_height, ascending=i % 4 == 1)
            goals[i+1] = [cur_x + ramp_length // 2, mid_y]
            cur_x += ramp_length + gap_length

    # Final platform
    add_platform(cur_x, m_to_idx(length), mid_y, 0)
    goals[-1] = [m_to_idx(11.0), mid_y]

    return height_field, goals

def set_terrain_8(length, width, field_resolution, difficulty):
    """Multiple varied-height platforms, angled ramps, and wider gaps for the quadruped to navigate, climb, and jump across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length = m_to_idx(1.0 - 0.2 * difficulty)
    platform_width = m_to_idx(np.random.uniform(1.0, 1.5))
    platform_height_min, platform_height_max = 0.2 * difficulty, 0.4 + 0.2 * difficulty
    gap_length = m_to_idx(0.2 + 0.4 * difficulty)
    
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

    for i in range(3):  # Set up a pattern with platforms and ramp
        height = np.random.uniform(platform_height_min, platform_height_max)
        add_platform(cur_x, cur_x + platform_length, mid_y, height)
        goals[i + 1] = [cur_x + platform_length // 2, mid_y]
        cur_x += platform_length + gap_length

        ramp_height = np.random.uniform(platform_height_min, platform_height_max)
        direction = 1 if i % 2 == 0 else -1
        add_ramp(cur_x, cur_x + platform_length // 2, mid_y, ramp_height, direction)
        goals[(i + 1) * 2] = [cur_x + (platform_length // 4), mid_y]
        cur_x += platform_length + gap_length
        
    final_height = np.random.uniform(platform_height_min, platform_height_max)
    add_platform(cur_x, cur_x + platform_length, mid_y, final_height)
    goals[6] = [cur_x + platform_length // 2, mid_y]
    cur_x += platform_length

    height = np.random.uniform(platform_height_min, platform_height_max)
    add_platform(cur_x, cur_x + platform_length, mid_y, height)
    goals[7] = [cur_x + platform_length // 2, mid_y]

    return height_field, goals

def set_terrain_9(length, width, field_resolution, difficulty):
    """Combination of narrow walkways with gentle turns, steep ramps, and tilted platforms for balance, climbing, and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up dimensions for features
    narrow_walkway_length = m_to_idx(1.0 - 0.3 * difficulty)
    narrow_walkway_width = m_to_idx(0.35 if difficulty > 0.4 else 0.5)
    ramp_length = m_to_idx(1.0 - 0.3 * difficulty)
    gap_length = m_to_idx(0.2 + 0.5 * difficulty)
    platform_tilt = 0.1 + 0.3 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, incline=0):
        height = np.random.uniform(0.15 * difficulty, 0.4 * difficulty)
        half_width = m_to_idx(0.5) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width

        height_field[x1:x2, y1:y2] = height + incline * np.linspace(0, 1, x2 - x1)[:, None]

    def add_walkway(start_x, end_x, mid_y):
        height = np.random.uniform(0.1 * difficulty, 0.3 * difficulty)
        half_width = narrow_walkway_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width

        for row in range(x1, x2):
            height_field[row, y1:y2] = height

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

    # Start with a narrow walkway
    cur_x = spawn_length
    dx = np.random.randint(dx_min, dx_max)
    dy = np.random.randint(dy_min, dy_max)
    add_walkway(cur_x, cur_x + narrow_walkway_length + dx, mid_y + dy)
    goals[1] = [cur_x + (narrow_walkway_length + dx) // 2, mid_y + dy]
    cur_x += narrow_walkway_length + dx + gap_length

    # Add a turning point with a platform
    dx = np.random.randint(dx_min, dx_max)
    dy = np.random.randint(dy_min, dy_max)
    add_platform(cur_x, cur_x + narrow_walkway_length + dx, mid_y + dy, platform_tilt)
    goals[2] = [cur_x + (narrow_walkway_length + dx) // 2, mid_y + dy]
    cur_x += narrow_walkway_length + dx + gap_length

    # Add inclined narrow walkways
    for i in range(3, 5):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        direction = 1 if i % 2 == 0 else -1

        add_ramp(cur_x, cur_x + ramp_length + dx, mid_y + dy, direction)
        goals[i] = [cur_x + (ramp_length + dx) // 2, mid_y + dy]
        cur_x += ramp_length + dx + gap_length

    # Add final goal behind a narrow platform, fill in the remaining gap
    dx = np.random.randint(dx_min, dx_max)
    dy = np.random.randint(dy_min, dy_max)
    add_walkway(cur_x, cur_x + narrow_walkway_length + dx, mid_y + dy)
    goals[5] = [cur_x + (narrow_walkway_length + dx) // 2, mid_y + dy]
    cur_x += narrow_walkway_length + dx

    # Place final goal
    goals[6] = [cur_x + m_to_idx(0.5), mid_y]
    goals[7] = [cur_x + m_to_idx(1.0), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

# INSERT TERRAIN FUNCTION DEFINITIONS HERE
