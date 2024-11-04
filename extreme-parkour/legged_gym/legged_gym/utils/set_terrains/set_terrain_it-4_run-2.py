
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
    """Narrow balance beams, inclined platforms, and hopping gaps to test balance and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Constants sizing and initial setup
    balance_beam_width = m_to_idx(0.4)  # Narrower balance beam
    incline_length = m_to_idx(1.0)
    incline_height_range = [0.2 * difficulty, 0.4 * difficulty]
    gap_length = m_to_idx(0.3 * (1 + difficulty))  # Increased gap lengths with difficulty
    mid_y = m_to_idx(width) // 2

    def add_balance_beam(start_x, end_x, y_center):
        y1 = y_center - balance_beam_width // 2
        y2 = y_center + balance_beam_width // 2
        height_field[start_x:end_x, y1:y2] = 0.2 * difficulty  # Balance beam's height

    def add_incline_platform(start_x, end_x, y_center, incline_height):
        y1 = y_center - balance_beam_width // 2
        y2 = y_center + balance_beam_width // 2
        incline = np.linspace(0, incline_height, end_x-start_x)
        incline = incline[:, None]
        height_field[start_x:end_x, y1:y2] = incline

    cur_x = m_to_idx(2)  # Initial spawn area
    height_field[:cur_x, :] = 0
    goals[0] = [cur_x - m_to_idx(0.5), mid_y]

    obstacles = [
        {'type': 'balance_beam', 'length': m_to_idx(1.5)},
        {'type': 'gap', 'length': gap_length},
        {'type': 'incline', 'length': incline_length, 'height': np.random.uniform(*incline_height_range)},
        {'type': 'gap', 'length': gap_length},
        {'type': 'balance_beam', 'length': m_to_idx(2.0)},
        {'type': 'gap', 'length': gap_length},        
        {'type': 'incline', 'length': incline_length, 'height': np.random.uniform(*incline_height_range)}
    ]

    for i, obs in enumerate(obstacles):
        if obs['type'] == 'balance_beam':
            add_balance_beam(cur_x, cur_x + obs['length'], mid_y)
            goals[i + 1] = [cur_x + obs['length'] // 2, mid_y]

        elif obs['type'] == 'incline':
            add_incline_platform(cur_x, cur_x + obs['length'], mid_y, obs['height'])
            goals[i + 1] = [cur_x + obs['length'] // 2, mid_y]
        
        cur_x += obs['length']

    # Spread goals apart adequately
    cur_x += m_to_idx(0.5)
    goals[-1] = [cur_x, mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_1(length, width, field_resolution, difficulty):
    """Series of staggered platforms with varying heights and irregular gaps to test stability, balance, and precise movements."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length = 0.8 - 0.2 * difficulty  # Slightly shorter platforms
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.2)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.3 + 0.4 * difficulty
    gap_length = 0.3 + 0.5 * difficulty  # Irregular and larger gaps
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2
    np.random.seed(42)  # For reproducibility

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    dx_min, dx_max = -0.15, 0.15
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(6):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
        
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        cur_x += platform_length + dx + gap_length

    # Add final goal after the last platform
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_2(length, width, field_resolution, difficulty):
    """Narrow beams, staggered platforms, and sideways ramps to test balance, precision, and gap traversal."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define obstacle dimensions based on difficulty
    min_beam_width = 0.4
    max_beam_width = 1.0 - 0.2 * difficulty
    min_platform_width = 1.0
    max_platform_width = 1.6 - 0.2 * difficulty
    min_ramp_height = 0.0 + 0.2 * difficulty
    max_ramp_height = 0.55 * difficulty
    gap_min = 0.2
    gap_max = 1.0 * difficulty

    mid_y = m_to_idx(width / 2)

    def add_beam(start_x, end_x, mid_y, beam_width, height):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_platform(start_x, end_x, mid_y, platform_width, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_ramp(start_x, end_x, mid_y, direction, height):
        half_width = m_to_idx(1.0) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slant_height = np.linspace(0, height, num=x2-x1)[::direction]
        slant_height = slant_height[:, None]  # Add a dimension for broadcasting to y
        height_field[x1:x2, y1:y2] = slant_height

    dx_min = m_to_idx(-0.1)
    dx_max = m_to_idx(0.1)
    dy_min = m_to_idx(0.0)
    dy_max = m_to_idx(0.4)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    # Define different types of obstacles
    num_obstacles = 6
    for i in range(num_obstacles):
        if i % 3 == 0:
            # Add beams for balance
            beam_width = np.random.uniform(min_beam_width, max_beam_width)
            beam_length = 1.0 + 0.4 * difficulty
            beam_length = m_to_idx(beam_length)
            height = np.random.uniform(min_ramp_height, max_ramp_height)
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)

            add_beam(cur_x, cur_x + beam_length + dx, mid_y + dy, m_to_idx(beam_width), height)
            goals[i+1] = [cur_x + (beam_length + dx) / 2, mid_y + dy]

            cur_x += beam_length + dx + m_to_idx(np.random.uniform(gap_min, gap_max))
        
        elif i % 3 == 1:
            # Add staggered platforms
            platform_width = np.random.uniform(min_platform_width, max_platform_width)
            platform_length = 1.5 + 0.3 * difficulty
            platform_length = m_to_idx(platform_length)
            height = np.random.uniform(min_ramp_height, max_ramp_height)
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)

            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, m_to_idx(platform_width), height)
            goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

            cur_x += platform_length + dx + m_to_idx(np.random.uniform(gap_min, gap_max))
        
        else:
            # Add ramps facing alternating directions
            ramp_length = 1.0 + 0.4 * difficulty
            ramp_length = m_to_idx(ramp_length)
            ramp_height = np.random.uniform(min_ramp_height, max_ramp_height)
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)
            direction = (-1)**i  # Alternate ramp direction

            add_ramp(cur_x, cur_x + ramp_length + dx, mid_y + dy, direction, ramp_height)
            goals[i+1] = [cur_x + (ramp_length + dx) / 2, mid_y + dy]

            cur_x += ramp_length + dx + m_to_idx(np.random.uniform(gap_min, gap_max))

    # Add final goal beyond the last obstacle
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0
    
    return height_field, goals

def set_terrain_3(length, width, field_resolution, difficulty):
    """Obstacle course with raised platforms, narrow beams, and sloped ramps for a balance of jumping, climbing, and balancing skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Adjust course parameters based on difficulty
    platform_length = m_to_idx(1.0 - 0.3 * difficulty)
    platform_width = m_to_idx(random.uniform(0.4, 0.8))
    beam_length = m_to_idx(1.0)
    beam_width = m_to_idx(0.2)  # Narrower beam for balancing
    ramp_length = m_to_idx(1.5)
    gap_length = m_to_idx(0.3 + 0.5 * difficulty)
    platform_height_min = 0.2 * difficulty
    platform_height_max = 0.5 * difficulty
    ramp_height_max = 0.5 * difficulty

    mid_y = m_to_idx(width / 2)
    
    def add_platform(start_x, end_x, mid_y, width):
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_beam(start_x, end_x, mid_y):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = np.random.uniform(platform_height_min, platform_height_max)

    def add_ramp(start_x, end_x, mid_y, direction):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(0.2, ramp_height_max)
        slant = np.linspace(0, ramp_height, num=end_x - start_x)[::direction]
        height_field[x1:x2, y1:y2] = slant[:, None]  # Gradual incline or decline

    dx_min, dx_max = m_to_idx(-0.1), m_to_idx(0.1)
    dy_min, dy_max = m_to_idx(-0.4), m_to_idx(0.4)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(6):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        if i % 3 == 0:
            add_platform(cur_x, cur_x + platform_length, mid_y + dy, platform_width)
            goals[i + 1] = [cur_x + platform_length // 2, mid_y + dy]
            cur_x += platform_length + gap_length
        elif i % 3 == 1:
            add_beam(cur_x, cur_x + beam_length, mid_y + dy)
            goals[i + 1] = [cur_x + beam_length // 2, mid_y + dy]
            cur_x += beam_length + gap_length
        else:
            direction = 1 if i % 2 == 0 else -1
            add_ramp(cur_x, cur_x + ramp_length, mid_y + dy, direction)
            goals[i + 1] = [cur_x + ramp_length // 2, mid_y + dy]
            cur_x += ramp_length + gap_length

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0
    
    return height_field, goals

def set_terrain_4(length, width, field_resolution, difficulty):
    """Alternating narrow beams, wide platforms, and sloped ramps for varied challenges."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform sizes and parameters
    narrow_width = 0.4 + 0.2 * difficulty  # Narrow beams
    wide_width = 1.0 + 0.4 * difficulty  # Wider platforms
    slope_height = 0.0 + 0.2 * difficulty  # Heights for sloped ramps
    platform_min_height, platform_max_height = 0.05 * difficulty, 0.35 * difficulty

    narrow_width, wide_width = m_to_idx(narrow_width), m_to_idx(wide_width)
    slope_height = m_to_idx(slope_height)
    gap_length = 0.1 + 0.4 * difficulty  # Varied gap lengths
    gap_length = m_to_idx(gap_length)
    
    mid_y = m_to_idx(width) // 2

    def add_narrow_beam(start_x, end_x, mid_y):
        half_width = narrow_width // 2
        height = np.random.uniform(platform_min_height, platform_max_height)
        height_field[start_x:end_x, mid_y - half_width:mid_y + half_width] = height

    def add_wide_platform(start_x, end_x, mid_y):
        half_width = wide_width // 2
        height = np.random.uniform(platform_min_height, platform_max_height)
        height_field[start_x:end_x, mid_y - half_width:mid_y + half_width] = height

    def add_ramp(start_x, end_x, mid_y):
        half_width = wide_width // 2
        slant_height = np.random.uniform(platform_min_height, platform_max_height)
        slant = np.linspace(0, slant_height, num=end_x - start_x)
        slant = slant[:, None]  # Add a dimension for broadcasting to y
        height_field[start_x:end_x, mid_y-half_width:mid_y+half_width] = slant

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(1), mid_y]  # First goal at the spawn point

    cur_x = spawn_length
    # Define the alternating course patterns
    course_components = [add_narrow_beam, add_wide_platform, add_ramp]
    
    for i in range(6):
        component = course_components[i % len(course_components)]
        component(cur_x, cur_x + gap_length, mid_y)
        goals[i+1] = [cur_x + gap_length // 2, mid_y]
        cur_x += gap_length
        
        # Add varied gaps
        cur_x += gap_length

    # Add final goal behind the last obstacle, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(1), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_5(length, width, field_resolution, difficulty):
    """Combination of narrow beams, angled ramps, and varying-height platforms to test the robot's balance, climbing, and precision."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length = 1.0 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.2)  # Wider for narrow beams
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.3 * difficulty, 0.3 + 0.5 * difficulty
    gap_length = 0.3 + 0.7 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        beam_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = beam_height

    def add_ramp(start_x, end_x, mid_y, direction):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(platform_height_min, platform_height_max)
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
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    for i in range(3):  # Add a sequence of narrow beams
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_beam(cur_x, cur_x + platform_length + dx, mid_y + dy)

        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        cur_x += platform_length + dx + gap_length

    for i in range(3,6):  # Add a sequence of angled ramps
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        direction = (-1) ** i  # Alternate left and right ramps
        dy = dy * direction  # Alternate positive and negative y offsets

        add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, direction)

        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        cur_x += platform_length + dx + gap_length

    # Final wide platform
    add_beam(cur_x, cur_x + platform_length, mid_y)
    goals[-1] = [cur_x + platform_length / 2, mid_y]

    height_field[cur_x + platform_length:, :] = 0  # Flatten remaining area

    return height_field, goals

def set_terrain_6(length, width, field_resolution, difficulty):
    """Multiple angled ramps and varied-height platforms to enhance difficulty for the quadruped."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and ramp dimensions based on difficulty
    platform_length = 1.1 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.2)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.15 * difficulty, 0.05 + 0.30 * difficulty
    ramp_height_min, ramp_height_max = 0.0 + 0.3 * difficulty, 0.2 + 0.55 * difficulty
    gap_length = 0.1 + 0.5 * difficulty
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
        slant = np.linspace(0, ramp_height, num=y2 - y1)[::direction]
        slant = slant[None, :]  # Add a dimension for broadcasting to x
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Initialize the remaining area with pits
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    dx = np.random.randint(dx_min, dx_max)
    dy = np.random.randint(dy_min, dy_max)
    add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
    goals[1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
    cur_x += platform_length + dx + gap_length

    def alternate_polarity(val, index):
        return val * ((-1) ** index)

    for i in range(1, 6):  # Set up 5 platforms and ramps with alternating polarities
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        direction = (-1) ** i  # Alternating direction for ramps
        dy = alternate_polarity(dy, i)

        if i % 2 == 0:
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
        else:
            add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, direction)

        goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_7(length, width, field_resolution, difficulty):
    """Obstacle course with staggered platforms and diagonal beams to test balance, climbing, and orientation adjustments."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and beam dimensions
    platform_length = 1.0 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.9, 1.2)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.3 * difficulty, 0.2 + 0.4 * difficulty

    beam_length = 1.2  # Slightly longer to increase difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = 0.4  # Narrow beams for balance
    beam_width = m_to_idx(beam_width)
    beam_height_min, beam_height_max = 0.2, 0.4 + 0.4 * difficulty

    gap_length = 0.2 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_beam(start_x, end_x, mid_y, slope_direction):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        beam_slope = np.linspace(0, slope_direction * (beam_height_max - beam_height_min), num=x2 - x1)
        height_field[x1:x2, y1:y2] = beam_slope[:, np.newaxis]

    dx_min, dx_max = -0.15, 0.15
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.25, 0.25
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0.0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    next_height = np.random.uniform(platform_height_min, platform_height_max)

    for i in range(4):  # First set 4 platforms in a staggered pattern
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, next_height)

        goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length
        next_height = np.random.uniform(platform_height_min, platform_height_max)

    previous_height = next_height

    for i in range(4, 7):  # Now set 3 diagonal beams for balance challenges
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        direction = (-1) ** i  # Alternate slope direction

        add_beam(cur_x, cur_x + beam_length + dx, mid_y + dy, direction)
        goals[i + 1] = [cur_x + (beam_length + dx) / 2, mid_y + dy]
        cur_x += beam_length + dx + gap_length
        previous_height = np.random.uniform(beam_height_min, beam_height_max)

    # Add final goal behind the last beam 
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0.0

    return height_field, goals

def set_terrain_8(length, width, field_resolution, difficulty):
    """Varied platforms and steps for the robot to climb and navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.3)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 * difficulty, 0.4 * difficulty
    gap_length = 0.2 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)

    step_height_min, step_height_max = 0.1, 0.3

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_step(start_x, end_x, mid_y):
        step_width = m_to_idx(0.4)
        half_width = step_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        step_height = np.random.uniform(step_height_min, step_height_max)
        height_field[x1:x2, y1:y2] = step_height

    dx_min, dx_max = np.round(-0.1/ field_resolution).astype(np.int16), np.round(0.1 /field_resolution).astype(np.int16)
    dy_min, dy_max = np.round(-0.2/ field_resolution).astype(np.int16), np.round(0.2 /field_resolution).astype(np.int16)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # First part: alternating platforms and steps
    cur_x = spawn_length
    for i in range(3):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
        goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

        add_step(cur_x, cur_x + m_to_idx(0.3), mid_y + dy)
        goals[i + 4] = [cur_x + m_to_idx(0.15), mid_y + dy]
        cur_x += m_to_idx(0.3) + gap_length

    # Final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_9(length, width, field_resolution, difficulty):
    """Balance beams, stepping stones, and slight ramps for improved balance and strategic navigation."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Stepping stones and balance beams dimensions
    step_length = 0.3 + 0.2 * difficulty
    step_length = m_to_idx(step_length)
    beam_length = 1.0 - 0.3 * difficulty
    beam_length = m_to_idx(beam_length)
    step_width = 0.3
    step_width = m_to_idx(step_width)
    beam_width = 0.2 + 0.1 * difficulty
    beam_width = m_to_idx(beam_width)
    step_height = 0.1 + 0.2 * difficulty
    ramp_height_min, ramp_height_max = 0.1, 0.2 + 0.3 * difficulty
    gap_length = 0.2 + 0.4 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_stepping_stone(start_x, end_x, start_y, end_y):
        height_field[start_x:end_x, start_y:end_y] = step_height

    def add_balance_beam(start_x, end_x, start_y, end_y):
        height_field[start_x:end_x, start_y:end_y] = step_height

    def add_ramp(start_x, end_x, start_y, end_y, direction):
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        slant = np.linspace(0, ramp_height, num=end_x-start_x)[::direction]
        height_field[start_x:end_x, start_y:end_y] = slant[:, np.newaxis]

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(2):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_stepping_stone(cur_x, cur_x + step_length + dx, mid_y + dy, mid_y + step_width + dy)
        goals[i+1] = [cur_x + (step_length + dx) / 2, mid_y + dy]
        cur_x += step_length + dx + gap_length

    for i in range(2, 4):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_balance_beam(cur_x, cur_x + beam_length + dx, mid_y - beam_width//2, mid_y + beam_width//2 + dy)
        goals[i+1] = [cur_x + (beam_length + dx) / 2, mid_y + dy]
        cur_x += beam_length + dx + gap_length

    for i in range(4, 6):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        direction = (-1) ** i
        add_ramp(cur_x, cur_x + step_length + dx, mid_y - step_width//2, mid_y + step_width//2 + dy, direction)
        goals[i+1] = [cur_x + (step_length + dx) / 2, mid_y + dy]
        cur_x += step_length + dx + gap_length

    for i in range(6, 7):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_balance_beam(cur_x, cur_x + beam_length + dx, mid_y - beam_width//2, mid_y + beam_width//2 + dy)
        goals[i+1] = [cur_x + (beam_length + dx) / 2, mid_y + dy]
        cur_x += beam_length + dx + gap_length

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

# INSERT TERRAIN FUNCTION DEFINITIONS HERE
