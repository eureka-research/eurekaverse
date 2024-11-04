
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
    """Complex terrain with alternating platforms and ramps to challenge climbing, jumping, and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up obstacle dimensions
    platform_length = 0.8 + 0.5 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.2)  # Reduce platform width slightly for added challenge
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.15 + 0.25 * difficulty, 0.25 + 0.3 * difficulty
    gap_length = 0.3 + 0.8 * difficulty
    gap_length = m_to_idx(gap_length)

    ramp_height_min, ramp_height_max = 0.1 + 0.4 * difficulty, 0.2 + 0.5 * difficulty

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
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn position
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(1, 7):  # Set up alternating platforms and ramps
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        if i % 2 == 0:
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
        else:
            direction = 1 if i % 4 == 1 else -1
            add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, direction)

        # Put goal in the center of the obstacle
        goals[i] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += platform_length + dx + gap_length
    
    # Add final goal behind the last obstacle, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_1(length, width, field_resolution, difficulty):
    """Higher platforms and narrow pathways with turning points to test agility, precise movement, and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform dimensions
    platform_length = 1.0 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.2)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.3 + 0.4 * difficulty
    
    # Beam dimensions
    beam_width = np.random.uniform(0.4, 0.6)
    beam_width = m_to_idx(beam_width)
    beam_height = 0.05 + 0.25 * difficulty
    
    # Gap dimensions
    gap_length = 0.1 + 0.3 * difficulty
    gap_length = m_to_idx(gap_length)
    
    mid_y = m_to_idx(width) // 2

    def add_platform(center_x, center_y, height, length, width):
        half_length = length // 2
        half_width = width // 2
        x1, x2 = center_x - half_length, center_x + half_length
        y1, y2 = center_y - half_width, center_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_beam(start_x, start_y, end_x, width, height):
        x1, x2 = start_x, end_x
        y1, y2 = start_y - width // 2, start_y + width // 2
        height_field[x1:x2, y1:y2] = height

    # Initialize the spawn area as flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    goal_idx = 1

    # Create the obstacle layout
    while goal_idx < 8:
        # Add platforms with increasing heights
        platform_height = np.random.uniform(platform_height_min, platform_height_max) * (goal_idx / 7)
        add_platform(cur_x + platform_length // 2, mid_y, platform_height, platform_length, platform_width)
        goals[goal_idx] = [cur_x + platform_length // 2, mid_y]
        cur_x += platform_length + gap_length
        goal_idx += 1
        
        if goal_idx >= 8:
            break
        
        # Add narrow beams
        beam_start_y = mid_y + np.random.choice([-1, 1]) * (platform_length // 2)
        add_beam(cur_x, beam_start_y, cur_x + platform_length, beam_width, beam_height)
        goals[goal_idx] = [cur_x + platform_length // 2, beam_start_y]
        cur_x += platform_length + gap_length
        goal_idx += 1
    
    # Fill the remaining area
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_2(length, width, field_resolution, difficulty):
    """Mixed terrain with stepped platforms, narrow beams, and alternating elevations to challenge jumping, balance, and agility."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length = 0.8 - 0.4 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.2)  # Random width for variety
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 * difficulty, 0.3 * difficulty
    gap_length = 0.3 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)
    beam_length = 0.4 + 0.2 * difficulty  # For narrow beams
    beam_length = m_to_idx(beam_length)

    mid_y = m_to_idx(width) // 2
    
    def add_platform(start_x, end_x, mid_y):
        """Add a flat platform to the terrain."""
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_beam(start_x, end_x, mid_y):
        """Add a narrow beam to the terrain."""
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - m_to_idx(0.1), mid_y + m_to_idx(0.1)  # Ensure minimum width of 0.2 meters
        beam_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = beam_height

    dx_min, dx_max = -0.2, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Set remaining area to be a pit
    height_field[spawn_length:, :] = -1.0  # Initially set all to pit

    cur_x = spawn_length
    
    # Add first platform
    dx = np.random.randint(dx_min, dx_max)
    dy = np.random.randint(dy_min, dy_max)
    add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
    goals[1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
    cur_x += platform_length + dx + gap_length

    for i in range(2, 7):  # Create mixed obstacles
        obstacle_type = np.random.choice(['platform', 'beam'])  # Mix platforms and beams
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        if obstacle_type == 'platform':
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        elif obstacle_type == 'beam':
            add_beam(cur_x, cur_x + beam_length + dx, mid_y + dy)
            goals[i] = [cur_x + (beam_length + dx) / 2, mid_y + dy]
        cur_x += (platform_length if obstacle_type == 'platform' else beam_length) + dx + gap_length

    # Add final goal and fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_3(length, width, field_resolution, difficulty):
    """Series of tilting platforms and ramps with gaps, to test balancing, climbing, jumping, and adaptability."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform and ramp dimensions
    platform_length = 0.9 - 0.3 * difficulty  # Slightly varied platform length
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.2)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 * difficulty, 0.25 + 0.25 * difficulty
    ramp_height_min, ramp_height_max = 0.15 * difficulty, 0.4 + 0.3 * difficulty
    gap_length_min, gap_length_max = 0.3 + 0.2 * difficulty, 0.6 + 0.4 * difficulty
    gap_length_min, gap_length_max = m_to_idx([gap_length_min, gap_length_max])

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_tilting_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        tilt_height = np.linspace(0, np.random.uniform(platform_height_min, platform_height_max), x2 - x1)[:, None]
        height_field[x1:x2, y1:y2] = tilt_height

    def add_ramp(start_x, end_x, mid_y, direction):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        slant = np.linspace(0, ramp_height, num=y2 - y1)[::direction]
        slant = slant[None, :]  # Adds a dimension for broadcasting to x
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.15, 0.15
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.0, 0.45
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Place the first goal at spawn point
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Set the remaining area to be a pit to force jumping from platform to platform
    height_field[spawn_length:, :] = -0.5

    cur_x = spawn_length
    for i in range(6):  # Set up 6 diverse obstacles including platforms, tilting platforms, and ramps
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        if i % 3 == 0:
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
        elif i % 3 == 1:
            add_tilting_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
        else:
            direction = (-1) ** i
            add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, direction)

        # Set goals at the center of each obstacle
        goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Add a gap between obstacles
        gap_length = np.random.randint(gap_length_min, gap_length_max)
        cur_x += platform_length + dx + gap_length

    # Final goal beyond the last obstacle
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_4(length, width, field_resolution, difficulty):
    """
    Multiple platforms with slight inclines and narrow pathways, traversing shallow pits
    to test the quadruped's precision walking, slight agility, and balance across small gaps.
    """

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define dimensions of obstacles relative to the robot's size and course specifications
    platform_length = 1.0 - 0.2 * difficulty  # slightly bigger platforms for moderate difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.2)  # varying width for challenge
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.02 + 0.1 * difficulty, 0.1 + 0.2 * difficulty
    gap_length = 0.1 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)
    
    inclined_modifier = 0.1 + 0.3 * difficulty  # added slight inclines

    mid_y = m_to_idx(width) // 2

    def add_inclined(start_x, end_x, mid_y, incl_dir=1):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        incline = np.linspace(0, inclined_modifier * incl_dir, num=x2 - x1)
        incline = incline[:, None]  # Add a dimension for broadcasting
        height_field[x1:x2, y1:y2] = incline

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(7):
        dx = np.random.uniform(-0.1, 0.1)
        dx = m_to_idx(dx)
        dy = np.random.uniform(-0.3, 0.3)
        dy = m_to_idx(dy)

        if i % 2 == 0:
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
        else:
            incl_dir = (-1) ** ((i - 1) // 2)
            add_inclined(cur_x, cur_x + platform_length + dx, mid_y + dy, incl_dir)

        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        cur_x += platform_length + dx + gap_length

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_5(length, width, field_resolution, difficulty):
    """Series of diagonally placed ramps and gaps with variable heights and widths to challenge adaptability and precise movements."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length_base = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length_base)
    platform_height_min, platform_height_max = 0.1 * difficulty, 0.4 * difficulty
    gap_length_min = 0.2
    gap_length_max = 0.5
    gap_length_min = m_to_idx(gap_length_min)
    gap_length_max = m_to_idx(gap_length_max)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[start_x:end_x, mid_y - m_to_idx(0.5):mid_y + m_to_idx(0.5)] = height
    
    def add_ramp(start_x, end_x, mid_y, height_diff):
        ramp_length = end_x - start_x
        slant = np.linspace(0, height_diff, num=ramp_length)[:, None]
        height_field[start_x:end_x, mid_y - m_to_idx(0.5):mid_y + m_to_idx(0.5)] = slant

    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    current_x = spawn_length

    for i in range(1, 7):
        dx = np.random.randint(-m_to_idx(0.2), m_to_idx(0.2))
        add_platform(current_x, current_x + platform_length + dx, mid_y)

        if i % 2 == 0:
            gap_length = np.random.randint(gap_length_min, gap_length_max)
            current_x += platform_length + dx + gap_length
            height_diff = np.random.uniform(platform_height_min, platform_height_max)
            add_ramp(current_x, current_x + platform_length + dx, mid_y, height_diff)
        
        height_field[current_x:current_x + platform_length + dx, :] = np.random.uniform(-0.1, 0.1)

        goals[i] = [current_x + (platform_length + dx) / 2, mid_y]

        current_x += platform_length + dx + gap_length_min

    goals[-1] = [current_x + m_to_idx(0.5), mid_y]
    height_field[current_x:, :] = 0

    return height_field, goals

def set_terrain_6(length, width, field_resolution, difficulty):
    """Series of stepped platforms and narrow pathways with turns to test precision and agility."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Setup terrain dimensions
    platform_length_min = 1.0 - 0.5 * difficulty
    platform_length_max = 1.0 + 0.5 * difficulty
    platform_width_min = 0.4
    platform_width_max = 1.2
    gap_length_min = 0.1 + 0.3 * difficulty
    gap_length_max = 1.0 * difficulty

    platform_height_min, platform_height_max = 0.1, 0.6 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = (m_to_idx(platform_width_min) + m_to_idx(platform_width_max)) // 2
        x1, x2 = start_x, end_x
        y1 = mid_y - half_width
        y2 = mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = -0.1, 0.1
    dy = 0.3 * difficulty

    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy = m_to_idx(dy)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Initialize starting x position
    cur_x = spawn_length

    for i in range(7):  # Create 7 platforms with varying lengths, heights, and gaps
        platform_length = np.random.uniform(platform_length_min, platform_length_max)
        platform_length_idx = m_to_idx(platform_length)
        platform_height = np.random.uniform(platform_height_min, platform_height_max)

        gap_length = np.random.uniform(gap_length_min, gap_length_max)
        gap_length_idx = m_to_idx(gap_length)
        
        dx = np.random.randint(dx_min, dx_max)
        direction = (-1) ** i

        # Add current platform
        add_platform(cur_x, cur_x + platform_length_idx + dx, mid_y + direction * dy, platform_height)
        
        # Place goal in the center of the platform
        goals[i+1] = [cur_x + (platform_length_idx + dx) / 2, mid_y + direction * dy]
        
        # Prepare for the gap
        cur_x += platform_length_idx + dx + gap_length_idx

    # Last stretch to finish line
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_7(length, width, field_resolution, difficulty):
    """Mixed platforms and ramps traversing a pit for the robot to climb, balance, and jump across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and ramp dimensions
    platform_length = 1.2 - 0.4 * difficulty  # Slightly longer platforms
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.2)  # Keep platform width challenging
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.2 + 0.3 * difficulty, 0.25 + 0.35 * difficulty  # Higher platforms
    ramp_height_min, ramp_height_max = 0.2 + 0.5 * difficulty, 0.25 + 0.6 * difficulty  # Higher ramps
    gap_length = 0.3 + 0.6 * difficulty  # Wider gaps
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        """Adds a platform to the height field."""
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_ramp(start_x, end_x, mid_y, direction):
        """Adds a sideways-facing ramp to the height field."""
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        slant = np.linspace(0, ramp_height, num=y2-y1)[::direction]
        slant = slant[None, :]  # Add a dimension for broadcasting to x
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.2, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.0, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set the spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Set the first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Set the remaining area to be a pit
    height_field[spawn_length:, :] = -1.0

    # Add the first platform
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

        # Put the goal in the center of the ramp
        goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += platform_length + dx + gap_length

    # Add the final goal behind the last ramp, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_8(length, width, field_resolution, difficulty):
    """Combination of raised platforms, narrow beams, and varied-height steps to challenge climbing, balancing, and jumping abilities."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform, beam, and step dimensions
    platform_length = 1.2 - 0.4 * difficulty  # Increase platform length
    platform_length = m_to_idx(platform_length)
    platform_width = m_to_idx(np.random.uniform(1.0, 1.2))  # Narrower platforms
    platform_height_min, platform_height_max = 0.15 + 0.1 * difficulty, 0.40 + 0.2 * difficulty
    
    beam_length = 1.0 - 0.3 * difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = m_to_idx(0.4)
    beam_height_min, beam_height_max = 0.05 + 0.1 * difficulty, 0.25 + 0.25 * difficulty

    step_height_min, step_height_max = 0.10 + 0.1 * difficulty, 0.25 + 0.25 * difficulty

    gap_length = 0.2 + 0.6 * difficulty  # Bigger gaps
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_beam(start_x, end_x, mid_y, height):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_step_platform(x, mid_y, height_min, height_max, width_step, depth_step, n_steps):
        """Creates a stepped platform by stacking smaller platforms."""
        for i in range(n_steps):
            step_height = np.random.uniform(height_min, height_max)
            x1, x2 = x + m_to_idx(i * depth_step), x + m_to_idx((i + 1) * depth_step)
            y1, y2 = mid_y - width_step // 2, mid_y + width_step // 2
            height_field[x1:x2, y1:y2] = step_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Set the remaining area to be a pit
    height_field[spawn_length:, :] = -1.0
    
    cur_x = spawn_length
    for i in range(4):
        if i % 2 == 0:
            # Add a higher platform
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)
            platform_height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height)
            goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
            cur_x += platform_length + dx + gap_length
        else:
            # Add a balance beam
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)
            beam_height = np.random.uniform(beam_height_min, beam_height_max)
            add_beam(cur_x, cur_x + beam_length + dx, mid_y + dy, beam_height)
            goals[i+1] = [cur_x + (beam_length + dx) / 2, mid_y + dy]
            cur_x += beam_length + dx + gap_length

    # Add stepped platform as the last obstacle
    add_step_platform(cur_x, mid_y + dy, step_height_min, step_height_max, platform_width, platform_length / 4, 3)
    goals[5] = [cur_x + platform_length, mid_y + dy]

    cur_x += platform_length + gap_length
    goals[6] = [cur_x + m_to_idx(0.5), mid_y]  # Add goal after stepped platform

    cur_x += m_to_idx(0.1)
    height_field[cur_x:, :] = 0  # Flatten the remaining area for final goal

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    
    return height_field, goals

def set_terrain_9(length, width, field_resolution, difficulty):
    """Obstacle course featuring narrow bridges, varying height platforms, and zig-zag paths."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length = 0.8 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 0.6 + 0.8 * (1 - difficulty)
    platform_width = m_to_idx(platform_width)
    platform_height_min = 0.0 + 0.3 * difficulty
    platform_height_max = 0.1 + 0.4 * difficulty
    gap_length = 0.6 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)
    beam_width = 0.4 + 0.2 * (1 - difficulty)
    beam_width = m_to_idx(beam_width)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_narrow_bridge(start_x, length, mid_y):
        half_width = beam_width // 2
        x1, x2 = start_x, start_x + length
        y1, y2 = mid_y - half_width, mid_y + half_width
        bridge_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = bridge_height

    dx_offset = m_to_idx(0.1)
    dy_offset = m_to_idx(0.2)

    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    alternate_direction = 1

    for i in range(6):
        if i % 2 == 0:
            dx = np.random.randint(-dx_offset, dx_offset)
            dy = np.random.randint(-dy_offset, dy_offset)
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
            cur_x += platform_length + dx + gap_length
        else:
            add_narrow_bridge(cur_x, platform_length, mid_y + dy * alternate_direction)
            goals[i+1] = [cur_x + platform_length / 2, mid_y + dy * alternate_direction]
            alternate_direction = -alternate_direction
            cur_x += platform_length + gap_length

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

# INSERT TERRAIN FUNCTION DEFINITIONS HERE