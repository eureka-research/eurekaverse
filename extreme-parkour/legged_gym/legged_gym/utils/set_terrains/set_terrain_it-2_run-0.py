
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

def set_terrain_1(length, width, field_resolution, difficulty):
    """Series of staggered small steps and narrow beams for the quadruped to balance and navigate across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define the characteristics of beams and steps
    step_width_min = 0.4
    step_width_max = 0.6
    step_height_min = 0.1
    step_height_max = 0.4 * difficulty
    gap_length_min = 0.1 + 0.2 * difficulty
    gap_length_max = 0.3 + 0.3 * difficulty

    step_length = m_to_idx(1.0)
    beam_width = m_to_idx(0.4)
    step_y_range = np.arange(m_to_idx(step_width_min), m_to_idx(step_width_max) + 1)
    gap_range = np.arange(m_to_idx(gap_length_min), m_to_idx(gap_length_max) + 1)

    mid_y = m_to_idx(width) // 2

    # Place obstacles
    cur_x = m_to_idx(2)
    height_field[0:cur_x, :] = 0
    goals[0] = [1, mid_y]

    for i in range(7):
        step_y_offset = np.random.choice(step_y_range)
        gap_x_offset = np.random.choice(gap_range)

        step_height = np.random.uniform(step_height_min * difficulty, step_height_max * difficulty)
        beam_height = np.random.uniform(step_height_min, step_height_max)

        # Adding staggered steps
        y1 = mid_y - step_y_offset // 2
        y2 = mid_y + step_y_offset // 2

        height_field[cur_x:cur_x + step_length, y1:y2] = step_height

        # Adding gap and beams
        cur_x += step_length + gap_x_offset

        beam_y1 = mid_y - beam_width // 2
        beam_y2 = mid_y + beam_width // 2

        height_field[cur_x:cur_x + step_length, beam_y1:beam_y2] = beam_height

        # Set goal at the middle of steps
        goals[i+1] = [cur_x + step_length // 2, mid_y]

        cur_x += step_length

    # Final section (flat area)
    height_field[cur_x:, :] = 0
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    return height_field, goals

def set_terrain_2(length, width, field_resolution, difficulty):
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

def set_terrain_3(length, width, field_resolution, difficulty):
    """Series of varied height platforms interconnected by narrow beams and small ramps, testing balance and coordination."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up obstacle dimensions
    platform_length = np.random.uniform(0.8, 1.2 - 0.1 * difficulty)
    platform_width = np.random.uniform(0.5, 1.0)
    platform_height_range = [0.0, 0.15 + 0.2 * difficulty]
    beam_length = np.random.uniform(1.0, 2.0 - 0.1 * difficulty)
    beam_width = 0.4

    platform_length = m_to_idx(platform_length)
    platform_width = m_to_idx(platform_width)
    beam_length = m_to_idx(beam_length)
    beam_width = m_to_idx(beam_width)
    gap_length = m_to_idx(0.1 + 0.3 * difficulty)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, length, center_y):
        half_width = platform_width // 2
        x1, x2 = start_x, start_x + length
        y1, y2 = center_y - half_width, center_y + half_width
        platform_height = np.random.uniform(*platform_height_range)
        height_field[x1:x2, y1:y2] = platform_height
        return platform_height
    
    def add_beam(start_x, length, center_y, height_offset):
        half_width = beam_width // 2
        x1, x2 = start_x, start_x + length
        y1, y2 = center_y - half_width, center_y + half_width
        height_field[x1:x2, y1:y2] = height_offset

    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0  # Set spawn area to flat ground
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    current_height = 0.0

    for i in range(7):
        # Adding platforms
        platform_height = add_platform(cur_x, platform_length, mid_y)
        goals[i+1] = [cur_x + platform_length // 2, mid_y]
        cur_x += platform_length + gap_length

        # Adding connecting beams
        random_offset = np.random.uniform(-0.2, 0.2) * ((i % 2) * 2 - 1)  # Alternating offset for balance challenge
        goal_y = mid_y + m_to_idx(random_offset)
        add_beam(cur_x, beam_length, goal_y, platform_height)
        current_height = platform_height
        cur_x += beam_length + gap_length

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]  # Final goal

    return height_field, goals

def set_terrain_4(length, width, field_resolution, difficulty):
    """Series of tilted platforms, gaps, and varying heights to challenge the robot's agility and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set obstacle properties based on difficulty
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.6, 1.1)  # Smaller platforms
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.2 * difficulty, 0.05 + 0.35 * difficulty
    gap_length = 0.1 + 0.7 * difficulty  # Larger gaps
    gap_length = m_to_idx(gap_length)
    
    mid_y = m_to_idx(width) // 2
        
    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_tilted_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slant_height = np.random.uniform(platform_height_min, platform_height_max)
        slant = np.linspace(0, slant_height, num=y2-y1)
        slant = slant[None, :]  # Add a dimension for broadcasting to x
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    
    for i in range(6):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        is_tilted = random.choice([True, False])  # Randomly choose between flat or tilted platforms

        if is_tilted:
            add_tilted_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
        else:
            height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, height)

        # Put goal in the center of the platform
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += platform_length + dx + gap_length

    # Add the final goal slightly ahead of the last platform
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_5(length, width, field_resolution, difficulty):
    """Mixed platforms and gaps with varying heights for the robot to navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up variables for platforms and gaps
    platform_length_min, platform_length_max = 0.8, 1.2
    platform_length_range = platform_length_max - platform_length_min
    gap_length_min, gap_length_max = 0.3, 1.0
    platform_height_min, platform_height_max = 0.1 * difficulty, 0.5 * difficulty

    platform_width_min, platform_width_max = 0.5, 1.2
    platform_width_range = platform_width_max - platform_width_min

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = int(np.random.uniform(platform_width_min, platform_width_max) / field_resolution) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # Put first goal at spawn point
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    # Create mixed platforms and gaps
    for i in range(6):
        # Determine platform dimensions and position
        platform_length = random.uniform(platform_length_min, platform_length_max) * min(1 + 0.5 * difficulty, 1.5)
        platform_length = m_to_idx(platform_length)
        gap_length = random.uniform(gap_length_min, gap_length_max) * min(1 - 0.5 * difficulty, 1)
        gap_length = m_to_idx(gap_length)
        platform_height = random.uniform(platform_height_min, platform_height_max)

        # Add platform
        add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)
        
        # Set goal on the platform
        goals[i + 1] = [cur_x + platform_length / 2, mid_y]

        # Update position for the next platform
        cur_x += platform_length + gap_length

    # Add final goal at the end of terrain
    final_gap = m_to_idx(0.5)
    goals[-1] = [cur_x + final_gap, mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_6(length, width, field_resolution, difficulty):
    """Multiple climbing and jumping platforms with alternating orientations for the robot to navigate."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]
    
    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    
    # Set up platform and ramp dimensions
    # For higher difficulty, we increase the height and width variations and gaps
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.3)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.3 * difficulty, 0.1 + 0.35 * difficulty
    gap_length = 0.2 + 0.6 * difficulty  # Wider gaps for higher difficulty
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
    dy_min, dy_max = 0.0, 0.3  # Alternating direction
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)
    
    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  
    
    # Set the remaining area to be a pit
    height_field[spawn_length:, :] = -1.0
    
    cur_x = spawn_length
    
    for i in range(6):  # Set up 6 platforms
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        direction = (-1) ** i  # Alternate left and right
        
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy * direction)
        
        # Put goal in the center of the platform
        goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy * direction]
        
        # Add gap
        cur_x += platform_length + dx + gap_length
    
    # Add final goal behind the last platform, fill in the remaining gap
    goals[7] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0
    
    return height_field, goals

def set_terrain_7(length, width, field_resolution, difficulty):
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

def set_terrain_8(length, width, field_resolution, difficulty):
    """Discontinuous narrow pathways with varied platform heights for the robot to balance and jump across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions
    platform_length = 0.8 + 0.4 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.4, 0.6)  # Narrower paths
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.15 + 0.3 * difficulty, 0.3 + 0.5 * difficulty
    gap_length = 0.3 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, platform_height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = platform_height

    dx_min, dx_max = -0.2, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length + gap_length
    for i in range(7):  # Set up 7 platforms
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        add_platform(cur_x + dx, cur_x + platform_length + dx, mid_y + dy, platform_height)

        # Put goal in the center of the platform
        goals[i+1] = [cur_x + dx + (platform_length // 2), mid_y + dy]

        # Add gap
        cur_x += platform_length + dx + gap_length

    return height_field, goals

def set_terrain_9(length, width, field_resolution, difficulty):
    """Multi-complex obstacle course with narrow beams, wide platforms, slopes, and varied gaps."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length = 0.8 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width_min = 0.4
    platform_width_max = 1.5
    platform_height_min, platform_height_max = 0.0 + 0.2 * difficulty, 0.1 + 0.3 * difficulty
    gap_length_min = 0.1 + 0.4 * difficulty
    gap_length_max = 0.5 + 0.7 * difficulty
    gap_length_min = m_to_idx(gap_length_min)
    gap_length_max = m_to_idx(gap_length_max)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, y_center, width):
        half_width = m_to_idx(width) // 2
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[start_x:end_x, y_center - half_width:y_center + half_width] = platform_height

    def add_slope(start_x, end_x, y_center, width, direction):
        half_width = m_to_idx(width) // 2
        ramp_height = np.random.uniform(platform_height_min, platform_height_max)
        slope = np.linspace(0, ramp_height, end_x - start_x)[::direction]
        slope = slope[:, None]  # Add a dimension for broadcasting to y
        height_field[start_x:end_x, y_center - half_width:y_center + half_width] = slope

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    for i in range(6):
        platform_width = np.random.uniform(platform_width_min, platform_width_max)
        gap_length = np.random.randint(gap_length_min, gap_length_max)

        if i % 2 == 0:
            add_platform(cur_x, cur_x + platform_length, mid_y, platform_width)
        else:
            direction = 1 if i % 4 == 1 else -1
            add_slope(cur_x, cur_x + platform_length, mid_y, platform_width, direction)

        goals[i + 1] = [cur_x + platform_length // 2, mid_y]

        cur_x += platform_length + gap_length

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

# INSERT TERRAIN FUNCTION DEFINITIONS HERE
