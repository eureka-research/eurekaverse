
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
    """Staggered steps and ramps for the robot to navigate and climb."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up obstacle dimensions
    platform_height_min, platform_height_max = 0.05 + 0.2 * difficulty, 0.1 + 0.3 * difficulty
    step_height_min, step_height_max = 0.05 + 0.2 * difficulty, 0.2 + 0.4 * difficulty
    gap_length = 0.2 + 0.7 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = m_to_idx(np.random.uniform(1.0, 1.5))
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_step(start_x, end_x, mid_y, direction):
        half_width = m_to_idx(np.random.uniform(1.0, 1.5))
        step_height = np.random.uniform(step_height_min, step_height_max)
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        if direction == 'up':
            height_field[x1:x2, y1:y2] = np.linspace(0, step_height, num=x2-x1)[:, None]
        else:
            height_field[x1:x2, y1:y2] = np.linspace(step_height, 0, num=x2-x1)[:, None]

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Define spawn area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Remaining area is a pit
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    for i in range(6):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        if i % 2 == 0:
            add_platform(cur_x, cur_x + m_to_idx(1.0) + dx, mid_y + dy)
        else:
            direction = 'up' if i % 4 == 1 else 'down'
            add_step(cur_x, cur_x + m_to_idx(1.0) + dx, mid_y + dy, direction)
        
        goals[i+1] = [cur_x + (m_to_idx(1.0) + dx) / 2, mid_y + dy]
        cur_x += m_to_idx(1.0) + dx + gap_length

    # Final goal behind the last obstacle
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_1(length, width, field_resolution, difficulty):
    """Combination of narrow walkways, stepping platforms, and diagonal ramps for testing balance, climbing, and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up obstacle dimensions
    platform_width = np.random.uniform(1.0, 1.3)  # Platform width between 1.0 to 1.3 meters
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.3 + 0.4 * difficulty
    gap_length = 0.2 + 0.4 * difficulty
    gap_length = m_to_idx(gap_length)
    ramp_width = 0.6  # Narrower ramps for balancing
    ramp_width = m_to_idx(ramp_width)
    ramp_height_min, ramp_height_max = 0.1 + 0.3 * difficulty, 0.2 + 0.5 * difficulty
    
    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_ramp(start_x, end_x, start_height, end_height, angle):
        half_width = ramp_width // 2
        x1, x2 = start_x, end_x
        height_diff = end_height - start_height
        steps = abs(x2 - x1)
        ramp_slope = np.linspace(0, height_diff, num=steps)
        for step in range(steps):
            mid_y_angle = mid_y + int(step * np.tan(np.radians(angle)))
            height_field[x1 + step, mid_y - half_width:mid_y + half_width] = start_height + ramp_slope[step]

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Initial pit to ensure step up to the first platform
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    goal_idx = 1
    # Add various obstacles
    for i in range(2, 9, 2):  # Only even indices for varied obstacles
        if i % 4 == 0:  # Add stepped platforms
            add_platform(cur_x, cur_x + m_to_idx(1.0), mid_y, np.random.uniform(platform_height_min, platform_height_max))
            goals[goal_idx] = [cur_x + m_to_idx(0.5), mid_y]
            goal_idx += 1
            cur_x += m_to_idx(1.0) + gap_length
        else:  # Add ramps
            add_ramp(cur_x, cur_x + m_to_idx(1.5), np.random.uniform(platform_height_min, platform_height_max), np.random.uniform(ramp_height_max, platform_height_max), 15)
            goals[goal_idx] = [cur_x + m_to_idx(0.75), mid_y]
            goal_idx += 1
            cur_x += m_to_idx(1.5) + gap_length

    # Final goal to wrap up the course
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_2(length, width, field_resolution, difficulty):
    """Varied-width platforms and sloped bridges over widened gaps for the robot to balance, climb, and jump across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and sloped bridge dimensions
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width_min, platform_width_max = 0.8, 1.3
    gap_length = 0.2 + 0.8 * difficulty
    gap_length = m_to_idx(gap_length)
    platform_height_min, platform_height_max = 0.25 + 0.25 * difficulty, 0.4 + 0.4 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_sloped_bridge(start_x, end_x, mid_y, direction, height_diff):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slant = np.linspace(0, height_diff, num=y2 - y1) * direction
        slant = slant[None, :]  # Add a dimension for broadcasting to x
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.1, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Add a mixture of platforms and sloped bridges
    cur_x = spawn_length
    alternating = True

    for i in range(6):  # Set up 6 total platforms/sloped bridges
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        platform_width = np.random.uniform(platform_width_min, platform_width_max)
        platform_width = m_to_idx(platform_width)

        if alternating:
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
        else:
            direction = (-1) ** i  # Alternate sloped directions
            height_diff = np.random.uniform(platform_height_min, platform_height_max)
            add_sloped_bridge(cur_x, cur_x + platform_length + dx, mid_y + dy, direction, height_diff)

        # Place goal in the center of the current obstacle
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += platform_length + dx + gap_length
        alternating = not alternating

    # Add final goal behind the last obstacle
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_3(length, width, field_resolution, difficulty):
    """Spiral narrow beams with slight inclines and gaps to test the robot's balance and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Dimensions of the beams
    beam_length = 1.2 - 0.3 * difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = np.random.uniform(0.3, 0.4)
    beam_width = m_to_idx(beam_width)
    incline_height = np.random.uniform(0.1 * difficulty, 0.3 * difficulty)

    gap_length = 0.3 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, mid_y):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        beam_height = np.linspace(0, incline_height, num=x2-x1)
        beam_height = beam_height[:, None]  # Add a dimension for broadcasting to y
        height_field[x1:x2, y1:y2] = beam_height

    def add_flat_beam(start_x, end_x, mid_y):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = incline_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    for i in range(7):  # Set up 7 beams
        if i % 2 == 0:
            add_beam(cur_x, cur_x + beam_length, mid_y)
        else:
            dy = np.random.randint(dy_min, dy_max)
            add_flat_beam(cur_x, cur_x + beam_length, mid_y + dy)
            mid_y += dy

        goals[i+1] = [cur_x + beam_length // 2, mid_y]
        cur_x += beam_length + gap_length

    # Add final goal behind the last beam, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_4(length, width, field_resolution, difficulty):
    """Staggered platforms and slopes focusing on dynamic balance and adaptive movement through varying heights."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length_base = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length_base)
    platform_width_base = np.random.uniform(1.0, 1.5)
    platform_width = m_to_idx(platform_width_base)
    platform_height_min, platform_height_max = 0.05 + 0.15 * difficulty, 0.25 + 0.35 * difficulty
    slope_length = 0.5 + 0.4 * difficulty
    slope_length = m_to_idx(slope_length)
    gap_length = 0.2 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_incline(start_x, end_x, mid_y, height_start, height_end):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        incline_matrix = np.linspace(height_start, height_end, x2 - x1)[:, None]
        height_field[x1:x2, y1:y2] = incline_matrix

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn area
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    # Start creating staggered platforms and slopes
    for i in range(6):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max) * ((-1) ** i)
        height_start = np.random.uniform(platform_height_min, platform_height_max)
        height_end = np.random.uniform(platform_height_min, platform_height_max)

        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, height_start)
        goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Create slope to next platform
        cur_x += platform_length + dx + gap_length
        add_incline(cur_x, cur_x + slope_length, mid_y, height_start, height_end)

        cur_x += slope_length

    # Add final goal behind the last incline, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_5(length, width, field_resolution, difficulty):
    """Combination of narrow platforms, tilted ramps, and irregular stone-like platforms."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    length_idx = m_to_idx(length)
    width_idx = m_to_idx(width)
    height_field = np.zeros((length_idx, width_idx))
    goals = np.zeros((8, 2))

    # Structure and dimensions
    platform_width_min = 0.35 + 0.1 * difficulty
    platform_width_max = 0.7 + 0.2 * difficulty
    tilt_ramp_length = 0.8 + 0.3 * difficulty
    tilt_ramp_height = 0.2 + 0.3 * difficulty
    pit_depth = -0.5 - 0.5 * difficulty
    stone_height_min, stone_height_max = 0.1, 0.3 + 0.3 * difficulty
    stone_diameter_min, stone_diameter_max = 0.4, 0.8 + 0.4 * difficulty

    mid_y = width_idx // 2

    def add_narrow_platform(start_x, end_x, y_center, width, height):
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = y_center - half_width, y_center + half_width
        height_field[x1:x2, y1:y2] = height

    def add_tilt_ramp(start_x, end_x, mid_y, ramp_height):
        half_width = m_to_idx(np.random.uniform(platform_width_min, platform_width_max)) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        tilt = np.linspace(0, ramp_height, num=(x2 - x1))[:, None]
        height_field[x1:x2, y1:y2] += tilt

    def add_irregular_stone(start_x, mid_y, diameter, height):
        radius = diameter // 2
        x1, x2 = start_x - radius, start_x + radius
        y1, y2 = mid_y - radius, mid_y + radius
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = -0.2, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(2):
        width = m_to_idx(np.random.uniform(platform_width_min, platform_width_max))
        height = 0.2 + 0.3 * difficulty
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_narrow_platform(cur_x, cur_x + m_to_idx(1.0) + dx, mid_y + dy, width, height)
        
        goals[i+1] = [cur_x + m_to_idx(0.5) + dx / 2, mid_y + dy]
        cur_x += m_to_idx(1.0) + dx + m_to_idx(0.4)

    for i in range(2, 4):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_tilt_ramp(cur_x, cur_x + m_to_idx(1.2) + dx, mid_y + dy, tilt_ramp_height)
        
        goals[i+1] = [cur_x + m_to_idx(0.6) + dx / 2, mid_y + dy]
        cur_x += m_to_idx(1.2) + dx + m_to_idx(0.4)
    
    for i in range(4, 6):
        diameter = m_to_idx(np.random.uniform(stone_diameter_min, stone_diameter_max))
        height = np.random.uniform(stone_height_min, stone_height_max)
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_irregular_stone(cur_x + dx, mid_y + dy, diameter, height)
        
        goals[i+1] = [cur_x + dx, mid_y + dy]
        cur_x += m_to_idx(1.0) + dx + m_to_idx(0.5)

    goals[6] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_6(length, width, field_resolution, difficulty):
    """Combination of narrow beams, staggered steps, and rotating platforms to test balance, climbing, and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up narrow beam dimensions
    beam_length = 1.0 - 0.3 * difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = np.random.uniform(0.4, 0.6)  # Narrow beam width
    beam_width = m_to_idx(beam_width)
    beam_height_min, beam_height_max = 0.1 + 0.3 * difficulty, 0.2 + 0.5 * difficulty
    
    # Set up staggered steps dimensions
    step_length = 0.5 + 0.2 * difficulty
    step_length = m_to_idx(step_length)
    step_width = np.random.uniform(0.7, 1.0)
    step_width = m_to_idx(step_width)
    step_height_min, step_height_max = 0.1 + 0.3 * difficulty, 0.2 + 0.4 * difficulty
   
    # Set up rotating platform dimensions (simplified as non-rotating for height_field config)
    platform_length = 1.0 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.4)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.3 * difficulty, 0.2 + 0.4 * difficulty
   
    gap_length = 0.2 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)
   
    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, mid_y):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        beam_height = np.random.uniform(beam_height_min, beam_height_max)
        height_field[x1:x2, y1:y2] = beam_height

    def add_steps(start_x, end_x, mid_y):
        half_width = step_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        step_height = np.random.uniform(step_height_min, step_height_max)
        height_field[x1:x2, y1:y2] = step_height

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height
    
    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)
   
    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y] # Initial goal at spawn
   
    cur_x = spawn_length
    for i in range(5): # 2 beams, 2 steps, 2 platforms to generate 7 goals
   
        if i % 2 == 0:   # Add beams
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)
            add_beam(cur_x, cur_x + beam_length + dx, mid_y + dy)
            goals[i + 1] = [cur_x + (beam_length + dx) // 2, mid_y + dy]
            cur_x += beam_length + dx + gap_length
        elif i % 2 == 1:  # Add staggered steps
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)
            add_steps(cur_x, cur_x + step_length + dx, mid_y + dy)
            goals[i + 1] = [cur_x + (step_length + dx) // 2, mid_y + dy]
            cur_x += step_length + dx + gap_length
        else: # Add rotating platforms
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i + 1] = [cur_x + (platform_length + dx) // 2, mid_y + dy]
            cur_x += platform_length + dx + gap_length
   
    # Add final goal behind the last obstacle, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_7(length, width, field_resolution, difficulty):
    """Obstacles include narrow beams, varied height platforms, and inclined ramps for robot navigation, climbing, and jumping skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and ramp dimensions
    platform_length = 1.0 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width_min, platform_width_max = 0.4 - 0.2 * difficulty, 1.0 - 0.4 * difficulty
    platform_width_min, platform_width_max = m_to_idx(platform_width_min), m_to_idx(platform_width_max)
    platform_height_min, platform_height_max = 0.3 * difficulty, 0.6 * difficulty
    gap_length = 0.3 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        width = np.random.randint(platform_width_min, platform_width_max)
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = height

    def add_beam(start_x, end_x, mid_y):
        width = m_to_idx(0.28)  # width of quadruped
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = height

    def add_ramp(start_x, end_x, mid_y, ascending):
        width = np.random.randint(platform_width_min, platform_width_max)
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        max_height = np.random.uniform(platform_height_min, platform_height_max)
        if ascending:
            gradient = np.linspace(0, max_height, end_x - start_x)
        else:
            gradient = np.linspace(max_height, 0, end_x - start_x)
        height_field[x1:x2, y1:y2] = gradient[:, None]

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    obstacle_types = ['platform', 'beam', 'ramp_up', 'ramp_down']
    for i in range(6):  # Set up 6 various obstacles
        obstacle_type = np.random.choice(obstacle_types)
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        if obstacle_type == 'platform':
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
        elif obstacle_type == 'beam':
            add_beam(cur_x, cur_x + platform_length + dx, mid_y + dy)
        elif obstacle_type == 'ramp_up':
            add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, ascending=True)
        elif obstacle_type == 'ramp_down':
            add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, ascending=False)

        goals[i+1] = [cur_x + (platform_length + dx) // 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

    # Add final goal behind the last obstacle, beyond the gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_8(length, width, field_resolution, difficulty):
    """Angled beams, raised platforms, and varying gap sizes for intricate navigation, balance, and jumping."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]
    
    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length = m_to_idx(1.0 - 0.3 * difficulty)
    platform_width = m_to_idx(np.random.uniform(1.2, 1.6))
    platform_height_min, platform_height_max = 0.1 * difficulty, 0.5
    gap_length = m_to_idx(0.3 + 0.7 * difficulty)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_angled_beam(start_x, end_x, mid_y, height, angle):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slant = np.linspace(0, height, num=end_x - start_x)
        if angle > 0:
            height_field[x1:x2, y1:y2] = slant[:, np.newaxis]
        else:
            height_field[x1:x2, y1:y2] = slant[::-1, np.newaxis]

    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0.0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]
    
    cur_x = spawn_length

    platform_heights = [np.random.uniform(platform_height_min, platform_height_max) for _ in range(4)]
    
    for i in range(2):
        add_platform(cur_x, cur_x + platform_length, mid_y, platform_heights[i])
        goals[i + 1] = [cur_x + platform_length // 2, mid_y]
        cur_x += platform_length + gap_length

        angle = 1 if i % 2 == 0 else -1
        add_angled_beam(cur_x, cur_x + platform_length, mid_y, platform_heights[i+1], angle)
        goals[i + 3] = [cur_x + platform_length // 2, mid_y]
        cur_x += platform_length + gap_length

    add_platform(cur_x, cur_x + platform_length, mid_y, platform_heights[3])
    goals[6] = [cur_x + platform_length // 2, mid_y]
    cur_x += platform_length
    
    height = np.random.uniform(platform_height_min, platform_height_max)
    add_platform(cur_x, cur_x + platform_length, mid_y, height)
    goals[7] = [cur_x + platform_length // 2, mid_y]

    return height_field, goals

def set_terrain_9(length, width, field_resolution, difficulty):
    """Advanced path with narrow inclined walkways, staggered platforms, and varying gaps to test balance, jumping, and stability."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up dimensions for features
    narrow_walkway_length = m_to_idx(1.0 - 0.5 * difficulty)
    narrow_walkway_width = m_to_idx(0.2 if difficulty > 0.5 else 0.3)  # Narrower pathways
    platform_length = m_to_idx(1.0 - 0.3 * difficulty)
    platform_width = m_to_idx(0.5)
    gap_length = m_to_idx(0.3 + 0.7 * difficulty)
    platform_height_min, platform_height_max = 0.2 * difficulty, 0.5 * difficulty
    mid_y = m_to_idx(width) // 2
    
    def add_walkway(start_x, end_x, mid_y, incline=0):
        height = np.random.uniform(0.1 * difficulty, 0.3 * difficulty)
        half_width = narrow_walkway_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width

        height_field[x1:x2, y1:y2] = height + incline * np.linspace(0, 1, x2 - x1)[:, None]

    def add_platform(start_x, end_x, mid_y):
        height = np.random.uniform(platform_height_min, platform_height_max)
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width

        height_field[x1:x2, y1:y2] = height

    def add_inclined_walkway(start_x, end_x, mid_y, direction):
        height = np.random.uniform(0.2 * difficulty, 0.5 * difficulty)
        half_width = narrow_walkway_width // 2
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

    cur_x = spawn_length

    # Start with a narrow inclined walkway
    for i in range(4):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        direction = 1 if i % 2 == 0 else -1  # Alternate incline and decline directions
        
        # Add inclined walkway
        add_inclined_walkway(cur_x, cur_x + narrow_walkway_length + dx, mid_y + dy, direction)
        goals[i+1] = [cur_x + (narrow_walkway_length + dx) // 2, mid_y + dy]
        cur_x += narrow_walkway_length + dx + gap_length

        if i == 1:  # After two obstacles add a platform
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i+2] = [cur_x + (platform_length + dx) // 2, mid_y + dy]
            cur_x += platform_length + dx + gap_length

    # After obstacles, end with another platform and a walkway
    add_platform(cur_x, cur_x + platform_length, mid_y)
    goals[5] = [cur_x + platform_length // 2, mid_y]
    cur_x += platform_length + gap_length

    add_walkway(cur_x, cur_x + narrow_walkway_length, mid_y)
    goals[6] = [cur_x + narrow_walkway_length // 2, mid_y]
    cur_x += narrow_walkway_length + gap_length

    # Final goal
    goals[7] = [cur_x + m_to_idx(1.0), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

# INSERT TERRAIN FUNCTION DEFINITIONS HERE
