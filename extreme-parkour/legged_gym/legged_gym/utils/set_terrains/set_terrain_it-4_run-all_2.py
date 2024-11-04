
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
    """Narrow beams and larger platforms for balance and transition skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Terrain dimensions and parameters
    mid_y = m_to_idx(width) // 2
    beam_height_min, beam_height_max = 0.05, 0.4 * difficulty
    beam_width = m_to_idx(0.2)  # Narrow beam, 0.2 meters
    platform_width = m_to_idx(1.2)  # Broad platform, 1.2 meters
    platform_length = m_to_idx(1.0 - 0.3 * difficulty)
    gap_length = m_to_idx(0.5 + 0.5 * difficulty)

    def add_beam(start_x, end_x, mid_y):
        """Add a narrow beam to the terrain."""
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        beam_height = np.random.uniform(beam_height_min, beam_height_max)
        height_field[x1:x2, y1:y2] = beam_height

    def add_platform(start_x, end_x, mid_y):
        """Add a broad platform to the terrain."""
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(beam_height_min, beam_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    cur_x = m_to_idx(2)
    height_field[:cur_x, :] = 0
    goals[0] = [cur_x / 2, mid_y]

    def add_goal(i, cur_x, length, mid_y):
        """Add a goal at the center of the current surface."""
        goals[i] = [cur_x + length // 2, mid_y]

    # Place obstacles and goals
    for i in range(7):
        if i % 2 == 0:  # Add a narrow beam
            beam_length = platform_length if i == 0 else platform_length - m_to_idx(0.2)
            add_beam(cur_x, cur_x + beam_length, mid_y)
            add_goal(i + 1, cur_x, beam_length, mid_y)
            cur_x += beam_length + gap_length
        else:  # Add a broad platform
            add_platform(cur_x, cur_x + platform_length, mid_y)
            add_goal(i + 1, cur_x, platform_length, mid_y)
            cur_x += platform_length + gap_length

    goals[-1] = [cur_x - gap_length / 2, mid_y]
    
    # Final area should be flat
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_1(length, width, field_resolution, difficulty):
    """A series of varying steps to test the robot's climbing and descending capabilities."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Step characteristics
    step_heights = [0.05, 0.1, 0.15, 0.2]  # Heights in meters 
    step_width_range = (1.0, 1.6)  # Range of step widths in meters
    step_length = 0.4  # Length of each step in meters

    step_length = m_to_idx(step_length)
    step_width_min, step_width_max = m_to_idx(step_width_range[0]), m_to_idx(step_width_range[1])
    mid_y = m_to_idx(width) // 2

    def add_step(start_x, start_y, step_height, step_width):
        x2 = start_x + step_length
        y1 = start_y - step_width // 2
        y2 = start_y + step_width // 2
        height_field[start_x:x2, y1:y2] = step_height

    # Setting initial flat area for spawn
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(7):  # Create 7 steps
        step_height = random.choice(step_heights) * difficulty
        step_width = random.randint(step_width_min, step_width_max)
        
        add_step(cur_x, mid_y, step_height, step_width)
        
        # Place goal at the top of each step
        goals[i + 1] = [cur_x + step_length // 2, mid_y]

        cur_x += step_length

    # Set the height at the end to zero (flat ground)
    height_field[cur_x:, :] = 0
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    return height_field, goals

def set_terrain_2(length, width, field_resolution, difficulty):
    """Multiple platforms, ramps, and gaps of increasing difficulty"""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set platform, ramp dimensions and gap lengths
    platform_length = 1.2 - 0.4 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 0.6  # Keep the platform width fixed
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.2 + 0.2 * difficulty, 0.3 + 0.4 * difficulty
    gap_length = 0.5 + 0.5 * difficulty  # Increase gap length with difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(x_start, x_end, mid_y, height):
        y_half_width = platform_width // 2
        y1, y2 = mid_y - y_half_width, mid_y + y_half_width
        height_field[x_start:x_end, y1:y2] = height

    def add_ramp(start_x, end_x, mid_y, height, direction):
        y_half_width = platform_width // 2
        y1, y2 = mid_y - y_half_width, mid_y + y_half_width
        ramp_height = np.linspace(0, height, num=end_x-start_x)
        ramp_height = ramp_height[None, :]  # add a new axis for broadcasting to y
        ramp_height = ramp_height[::direction]  # reverse the ramp if direction is -1
        height_field[start_x:end_x, y1:y2] = ramp_height.T

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    for i in range(6):
        height = np.random.uniform(platform_height_min, platform_height_max)

        if i % 2 == 0:
            # Add a platform
            add_platform(cur_x, cur_x + platform_length, mid_y, height)
            goals[i+1] = [cur_x + platform_length / 2, mid_y]
        else:
            # Add a ramp
            direction = (-1) ** i  # Alternate slope directions
            add_ramp(cur_x, cur_x + platform_length, mid_y, height, direction)
            goals[i+1] = [cur_x + platform_length / 2, mid_y]
        
        # Adding a gap between obstacles
        cur_x += platform_length + dx_min + np.random.randint(dx_max) + gap_length

    # Add final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_3(length, width, field_resolution, difficulty):
    """Multiple platforms and narrow beams traversing a pit for the robot to navigate across."""
   
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and beam dimensions
    platform_length = 0.8 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 0.7 + 0.3 * difficulty
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.3 * difficulty, 0.2 + 0.5 * difficulty
    
    beam_length = 0.6 + 0.2 * difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = 0.3 + 0.1 * difficulty
    beam_width = m_to_idx(beam_width)
    beam_height = 0.15 + 0.2 * difficulty

    gap_length = 0.2 + 0.4 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_beam(start_x, end_x, mid_y, height):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = -0.05, 0.1  # Smaller variance to keep a challenging but manageable terrain
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Set remaining area to be a pit to ensure navigation from platform to platform
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    for i in range(4):  # Set up 4 platforms with gaps
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + platform_length, mid_y + dy)

        # Put goal in the center of the platform
        goals[i+1] = [cur_x + (platform_length // 2), mid_y + dy]

        # Add gap
        cur_x += platform_length + dx + gap_length

    for i in range(2):  # Set up 2 beams with gaps
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_beam(cur_x, cur_x + beam_length, mid_y + dy, beam_height)

        # Put goal at the start of the beam
        goals[5 + i] = [cur_x + (beam_length // 2), mid_y + dy]

        # Add gap
        cur_x += beam_length + dx + gap_length
    
    # Add final goal at the end
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_4(length, width, field_resolution, difficulty):
    """Mixed course with platforms, narrow beams, and tilted beams for agility and stability."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Course parameters
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width_specs = [np.random.uniform(1.0, 1.1), np.random.uniform(0.4, 0.7)]
    platform_width_specs = [m_to_idx(pw) for pw in platform_width_specs]
    platform_height_min, platform_height_max = 0.1 * difficulty, 0.4 * difficulty
    gap_length = 0.2 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)
    ramp_length = m_to_idx(1.5 - 0.5 * difficulty)

    mid_y = m_to_idx(width / 2)

    def add_platform(start_x, end_x, mid_y, width_spec):
        half_width = width_spec // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_beam(start_x, end_x, mid_y, width_spec):
        half_width = width_spec // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = np.random.uniform(0.1 * difficulty, 0.4 * difficulty)

    def add_tilted_beam(start_x, end_x, mid_y, direction, width_spec):
        half_width = width_spec // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(0.2, 0.6) * difficulty
        slant = np.linspace(0, ramp_height, num=end_x - start_x)[::direction]  # Create gradient
        height_field[x1:x2, y1:y2] = slant[:, None]

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.0, 0.5
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(7):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        if i % 3 == 0:
            obstacle = add_platform
            width_spec = platform_width_specs[0]
        elif i % 3 == 1:
            obstacle = add_beam
            width_spec = platform_width_specs[1]
        else:
            obstacle = add_tilted_beam
            width_spec = platform_width_specs[1]
            direction = 1 if i % 2 == 0 else -1

        if obstacle == add_tilted_beam:
            obstacle(cur_x, cur_x + ramp_length + dx, mid_y + dy, direction, width_spec)
            goals[i+1] = [cur_x + ramp_length // 2 + dx // 2, mid_y + dy]
            cur_x += ramp_length + dx + gap_length
        else:
            obstacle(cur_x, cur_x + platform_length + dx, mid_y + dy, width_spec)
            goals[i+1] = [cur_x + platform_length // 2, mid_y + dy]
            cur_x += platform_length + dx + gap_length

    # Set the final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_5(length, width, field_resolution, difficulty):
    """Multiple platforms connected by ramps and small gaps for balancing and climbing."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and ramp dimensions
    platform_length = 1.0 - 0.15 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.4) 
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.1 * difficulty, 0.2 + 0.25 * difficulty
    ramp_height_min, ramp_height_max = 0.0 + 0.3 * difficulty, 0.2 + 0.35 * difficulty
    gap_length = 0.1 + 0.3 * difficulty  
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_ramp(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        slant = np.linspace(0, ramp_height, num=y2-y1)
        slant = slant[None, :]  # Add a dimension for broadcasting to x
        height_field[x1:x2, y1:y2] = slant

    def add_safe_zone(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = 0

    dx_min, dx_max = -0.1, 0.1 
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.0, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    dx = np.random.randint(dx_min, dx_max)
    dy = np.random.randint(dy_min, dy_max)
    
    add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
    goals[1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
    cur_x += platform_length + dx + gap_length

    for i in range(1, 6):  # Set up 5 ramps
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        if i % 2 == 1:
            add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy)
        else:
            add_safe_zone(cur_x, cur_x + platform_length + dx, mid_y + dy)

        goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

    # Add final goal to the flat area beyond last obstacle
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0.0

    return height_field, goals

def set_terrain_6(length, width, field_resolution, difficulty):
    """Varying-width platforms and balance beams with small gaps, testing balance and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    balance_beam_length = 1.0 - 0.4 * difficulty
    balance_beam_length = m_to_idx(balance_beam_length)
    platform_width_min, platform_width_max = 0.4, 0.8 + 0.6 * difficulty
    beam_width = 0.3
    beam_width = m_to_idx(beam_width)
    platform_height_min, platform_height_max = 0.0 + 0.2 * difficulty, 0.05 + 0.25 * difficulty
    gap_length = 0.1 + 0.4 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, mid_y):
        width = np.random.uniform(platform_width_min, platform_width_max)
        width = m_to_idx(width)
        half_width = width // 2
        x1 = start_x
        x2 = start_x + platform_length
        y1 = mid_y - half_width
        y2 = mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height
        
    def add_balance_beam(start_x, mid_y):
        half_width = beam_width // 2
        x1 = start_x
        x2 = start_x + balance_beam_length
        y1 = mid_y - half_width
        y2 = mid_y + half_width
        beam_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = beam_height

    dx_min, dx_max = m_to_idx(-0.05), m_to_idx(0.05)  # Slight horizontal variability
    dy_min, dy_max = m_to_idx(-0.2), m_to_idx(0.2)  # Slight vertical variability

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    for i in range(4):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        # Add platform or balance beam alternately
        if i % 2 == 0:
            add_platform(cur_x, mid_y + dy)
            goals[i + 1] = [cur_x + platform_length / 2, mid_y + dy]
            cur_x += platform_length + dx + gap_length
        else:
            add_balance_beam(cur_x, mid_y + dy)
            goals[i + 1] = [cur_x + balance_beam_length / 2, mid_y + dy]
            cur_x += balance_beam_length + dx + gap_length

    # Add extra challenges towards the end to increase difficulty
    for i in range(4, 6):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        # Add platform or balance beam alternately with increased width variability
        if i % 2 == 0:
            platform_width_min += difficulty
            platform_width_max += difficulty
            add_platform(cur_x, mid_y + dy)
            goals[i + 1] = [cur_x + platform_length / 2, mid_y + dy]
            cur_x += platform_length + dx + gap_length
        else:
            add_balance_beam(cur_x, mid_y + dy)
            goals[i + 1] = [cur_x + balance_beam_length / 2, mid_y + dy]
            cur_x += balance_beam_length + dx + gap_length

    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_7(length, width, field_resolution, difficulty):
    """Narrow paths, higher platforms, and wider gaps for comprehensive balance, navigation, and jumping challenges."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform and gap dimension variables
    platform_length = 0.8 - 0.3 * difficulty  # Increasing difficulty decreases platform size
    platform_length = m_to_idx(platform_length)
    platform_width = 0.6 + 0.3 * difficulty  # Making the platform width narrower with increased difficulty
    platform_width = m_to_idx(platform_width)
    platform_height_min = 0.2 + 0.3 * difficulty  # Taller platforms
    platform_height_max = 0.4 + 0.4 * difficulty
    gap_length = 0.2 + 0.8 * difficulty  # Wider gaps
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, center_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = center_y - half_width, center_y + half_width
        height_field[x1:x2, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[:spawn_length, :] = 0  # Ensuring flat spawn area
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at spawn

    last_x = spawn_length
    for i in range(1, 8):
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        start_x = last_x + gap_length
        end_x = start_x + platform_length

        center_y_offset = (-1) ** i * np.random.randint(0, m_to_idx(0.3))  # alternating offsets

        add_platform(start_x, end_x, mid_y + center_y_offset, platform_height)

        goals[i] = [start_x + platform_length / 2, mid_y + center_y_offset]

        last_x = end_x

    return height_field, goals

def set_terrain_8(length, width, field_resolution, difficulty):
    """Mixed obstacles including wide platforms, uneven stepping stones, and gentle slopes for agility and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform parameters
    platform_width = np.random.uniform(1.2, 1.8)
    platform_width = m_to_idx(platform_width)
    platform_length = 1.5 - 0.5 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_height_min, platform_height_max = 0.1 * difficulty, 0.3 * difficulty

    # Stepping stone parameters
    stepping_stone_size = 0.5
    stepping_stone_size = m_to_idx(stepping_stone_size)
    stepping_stone_height_min, stepping_stone_height_max = 0.05 * difficulty, 0.2 * difficulty

    # Slope parameters
    slope_width = platform_width
    slope_length = 1.5 - 0.5 * difficulty
    slope_length = m_to_idx(slope_length)
    slope_height_min, slope_height_max = 0.1 * difficulty, 0.25 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_stepping_stone(mid_x, mid_y, height):
        half_size = stepping_stone_size // 2
        x1, x2 = mid_x - half_size, mid_x + half_size
        y1, y2 = mid_y - half_size, mid_y + half_size
        height_field[x1:x2, y1:y2] = height

    def add_slope(start_x, end_x, mid_y, height):
        half_width = slope_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slope = np.linspace(0, height, num=x2-x1)[:, None]  # Creating gradual slope
        height_field[x1:x2, y1:y2] = slope

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # First goal at the end of the flat area
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    dx_min, dx_max = m_to_idx(-0.1), m_to_idx(0.1)
    dy_min, dy_max = m_to_idx(-0.4), m_to_idx(0.4)

    # Add first wide platform
    add_platform(cur_x, cur_x + platform_length, mid_y, np.random.uniform(platform_height_min, platform_height_max))
    goals[1] = [cur_x + platform_length // 2, mid_y]
    cur_x += platform_length + m_to_idx(0.5)

    # Add series of stepping stones
    for i in range(2, 6):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_stepping_stone(cur_x + dx, mid_y + dy, np.random.uniform(stepping_stone_height_min, stepping_stone_height_max))
        goals[i] = [cur_x + dx, mid_y + dy]
        cur_x += stepping_stone_size + m_to_idx(0.5)

    # Add final slope
    slope_height = np.random.uniform(slope_height_min, slope_height_max)
    add_slope(cur_x, cur_x + slope_length, mid_y, slope_height)
    goals[-2] = [cur_x + slope_length // 2, mid_y]
    cur_x += slope_length + m_to_idx(0.5)

    # Last goal at the end
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0  # Ensure no further obstacles

    return height_field, goals

def set_terrain_9(length, width, field_resolution, difficulty):
    """Stepping stones across a stream for the robot to jump and balance on."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up stepping stone dimensions
    stone_diameter_min = 0.4  # minimum diameter of stepping stones
    stone_diameter_max = 0.8  # maximum diameter of stepping stones
    stone_height_min, stone_height_max = 0.1 + 0.1 * difficulty, 0.15 + 0.25 * difficulty
    gap_length_min = 0.3  # minimum gap between stepping stones
    gap_length_max = 0.7 + 0.3 * difficulty  # maximum gap increases with difficulty

    def add_stepping_stone(center_x, center_y):
        radius = np.random.uniform(stone_diameter_min / 2, stone_diameter_max / 2)
        radius_idx = m_to_idx(radius)
        stone_height = np.random.uniform(stone_height_min, stone_height_max)

        x, y = m_to_idx(center_x), m_to_idx(center_y)
        for i in range(-radius_idx, radius_idx + 1):
            for j in range(-radius_idx, radius_idx + 1):
                if i**2 + j**2 <= radius_idx**2:
                    height_field[x + i, y + j] = stone_height

    spawn_length = m_to_idx(2)
    mid_y = m_to_idx(width / 2)

    # Set spawn area to flat ground
    height_field[0:spawn_length, :] = 0
    # Put the first goal at spawn area
    goals[0] = [m_to_idx(1), mid_y]

    cur_x = 2.0
    for i in range(1, 8):  # Set up 7 stepping stones
        stone_center_y = width / 2 + np.random.uniform(-width / 4, width / 4)
        stone_center_x = cur_x + np.random.uniform(gap_length_min, gap_length_max)
        add_stepping_stone(stone_center_x, stone_center_y)

        # Place goal on the current stepping stone
        goals[i] = [m_to_idx(stone_center_x), m_to_idx(stone_center_y)]
        
        # Update current x position for the next stone
        cur_x = stone_center_x

    return height_field, goals

def set_terrain_10(length, width, field_resolution, difficulty):
    """Series of different height platforms for the robot to jump onto and adapt its approach."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions for varying heights and gaps
    platform_length = 0.8 - 0.2 * difficulty  # Decreased length to make it jumpier
    platform_length = m_to_idx(platform_length)
    platform_width = 0.4 + 0.4 * (1 - difficulty)  # Narrow platforms
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1, 0.8 * difficulty  # Varied heights
    gap_length = 0.3 + 0.5 * difficulty  # Larger gaps
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Start creating platforms and gaps after spawn area
    cur_x = spawn_length

    for i in range(7):  # 7 platforms
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)

        # Put goal at the center of the platform
        goals[i+1] = [cur_x + platform_length // 2, mid_y]

        # Add gap
        cur_x += platform_length + gap_length
    
    # Add final goal beyond the last platform
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_11(length, width, field_resolution, difficulty):
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

def set_terrain_12(length, width, field_resolution, difficulty):
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

def set_terrain_13(length, width, field_resolution, difficulty):
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

def set_terrain_14(length, width, field_resolution, difficulty):
    """Series of interconnected platforms and tilted planes to test the quadruped's balance and navigation abilities."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and plane dimensions
    platform_length = 1.5 - 0.5 * difficulty
    platform_length = m_to_idx(platform_length)
    small_platform_length = 0.6 - 0.2 * difficulty
    small_platform_length = m_to_idx(small_platform_length)
    obstacle_width = np.random.uniform(1.0, 1.2)
    obstacle_width = m_to_idx(obstacle_width)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.3 + 0.4 * difficulty
    ramp_height_min, ramp_height_max = 0.1 + 0.3 * difficulty, 0.2 + 0.5 * difficulty
    gap_length = 0.3 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, center_y):
        half_width = obstacle_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = center_y - half_width, center_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_ramp(start_x, end_x, center_y, slope_direction):
        half_width = obstacle_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = center_y - half_width, center_y + half_width
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        slant = np.linspace(0, ramp_height, num=y2-y1)[::slope_direction]
        slant = slant[None, :]  # Add a dimension for broadcasting to x
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.2, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.1, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Set remaining area to be a pit
    height_field[spawn_length:, :] = -1.0

    # Add first large platform
    cur_x = spawn_length
    dx = np.random.randint(dx_min, dx_max)
    dy = np.random.randint(dy_min, dy_max)
    add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
    goals[1] = [cur_x + (platform_length + dx) / 2, mid_y]
    cur_x += platform_length + dx + gap_length

    # Add interconnected ramps and small platforms
    for i in range(2, 6):
        if i % 2 == 0:  # Add small platform
            add_platform(cur_x, cur_x + small_platform_length, mid_y)
            cur_x += small_platform_length
        else:  # Add ramp
            slope_direction = (-1) ** (i // 2)  # Alternate direction
            add_ramp(cur_x, cur_x + platform_length // 2, mid_y, slope_direction)
            cur_x += platform_length // 2
            add_ramp(cur_x, cur_x + platform_length // 2, mid_y, -slope_direction)
            cur_x += platform_length // 2
        
        goals[i] = [cur_x - platform_length // 4, mid_y]
        cur_x += gap_length
    
    # Add last ramp and fill in remaining area
    slope_direction = 1 if (len(goals) - 1) % 2 else -1  # Alternate direction
    add_ramp(cur_x, cur_x + platform_length, mid_y, slope_direction)
    goals[-1] = [cur_x + platform_length / 2, mid_y]
    height_field[cur_x + platform_length:, :] = 0

    return height_field, goals

def set_terrain_15(length, width, field_resolution, difficulty):
    """Combination of narrow beams, varied height platforms, and sloped ramps to test balance, precision, and incline traversal."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_width_min = 0.4 + 0.1 * difficulty
    platform_width_max = 1.5 - 0.2 * difficulty
    platform_length = 1.0 + 0.4 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.6 * difficulty
    gap_length = 0.2 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_obstacle(start_x, end_x, mid_y, obs_width, height):
        half_width = obs_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

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

    for i in range(6):  # Set up 6 obstacles of varying types
        obs_type = random.choice(["beam", "platform", "ramp"])
        obs_width = np.random.uniform(platform_width_min, platform_width_max)
        obs_width = m_to_idx(obs_width)
        obs_height = np.random.uniform(platform_height_min, platform_height_max)
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        if obs_type == "beam":
            add_obstacle(cur_x, cur_x + platform_length + dx, mid_y + dy, obs_width, obs_height)
        elif obs_type == "platform":
            add_obstacle(cur_x, cur_x + platform_length + dx, mid_y + dy, obs_width, obs_height)
        elif obs_type == "ramp":
            half_width = obs_width // 2
            x1, x2 = cur_x, cur_x + platform_length + dx
            y1, y2 = mid_y + dy - half_width, mid_y + dy + half_width
            ramp_height = np.linspace(0, obs_height, y2-y1)[None, :]
            height_field[x1:x2, y1:y2] = ramp_height

        # Place a goal at the center of the obstacle
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Create a gap after the obstacle
        cur_x += platform_length + dx + gap_length

    # Add final goal behind the last obstacle, filling in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_16(length, width, field_resolution, difficulty):
    """Hurdles and beams obstacle course for the robot to step over and balance on."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Height of the hurdles
    hurdle_height_min, hurdle_height_max = 0.1 + 0.1 * difficulty, 0.3 + 0.2 * difficulty
    hurdle_length = m_to_idx(0.4)
    hurdle_width = m_to_idx(1.0)

    # Width of the beams
    beam_length = m_to_idx(1.0)
    beam_width = m_to_idx(0.4)
    beam_height_min, beam_height_max = 0.05 + 0.1 * difficulty, 0.2 + 0.2 * difficulty

    def add_hurdle(start_x, y):
        """Add a hurdle at the specified location."""
        x1, x2 = start_x, start_x + hurdle_length
        y1, y2 = y - hurdle_width // 2, y + hurdle_width // 2
        hurdle_height = np.random.uniform(hurdle_height_min, hurdle_height_max)
        height_field[x1:x2, y1:y2] = hurdle_height

    def add_beam(start_x, y):
        """Add a narrow beam at the specified location."""
        x1, x2 = start_x, start_x + beam_length
        y1, y2 = y - beam_width // 2, y + beam_width // 2
        beam_height = np.random.uniform(beam_height_min, beam_height_max)
        height_field[x1:x2, y1:y2] = beam_height

    mid_y = m_to_idx(width) // 2

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Place first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length + m_to_idx(0.5)
    turn_offset_y = m_to_idx(0.4)
    y_positions = [
        mid_y - turn_offset_y,
        mid_y + turn_offset_y,
        mid_y - turn_offset_y,
        mid_y + turn_offset_y,
        mid_y - turn_offset_y,
        mid_y + turn_offset_y,
    ]

    # Add alternating hurdles and beams along the course
    for i, y in enumerate(y_positions[:6]):
        if i % 2 == 0:
            add_hurdle(cur_x, y)
            goals[i+1] = [cur_x + hurdle_length // 2, y]
        else:
            add_beam(cur_x, y)
            goals[i+1] = [cur_x + beam_length // 2, y]
        cur_x += m_to_idx(2)
    
    # Final goal
    goals[7] = [cur_x + m_to_idx(1), mid_y - turn_offset_y]

    return height_field, goals

def set_terrain_17(length, width, field_resolution, difficulty):
    """Stepping stones across a river with varying heights and distances."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Stepping stone parameters
    stone_diameter_min = 0.4  # meters
    stone_diameter_max = 0.8  # meters
    stone_height_min = 0.1  # meters
    stone_height_max = 0.4  # meters

    # Distance between stones varies with difficulty
    min_stone_distance = 0.5  # meters
    max_stone_distance = 1.5 + 3.5 * difficulty  # meters

    mid_y = m_to_idx(width) // 2

    def add_stone(center_x, center_y):
        x_rad = m_to_idx(random.uniform(stone_diameter_min, stone_diameter_max) / 2)
        y_rad = x_rad  # Making stones circular
        stone_height = random.uniform(stone_height_min, stone_height_max) * difficulty
        
        x1 = center_x - x_rad
        x2 = center_x + x_rad
        y1 = center_y - y_rad
        y2 = center_y + y_rad
        
        x1, x2 = max(x1, 0), min(x2, height_field.shape[0])
        y1, y2 = max(y1, 0), min(y2, height_field.shape[1])
        
        height_field[x1:x2, y1:y2] = stone_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # First goal, near the spawn area
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]
    
    # Keep track of the current position where new stones are added
    cur_x = spawn_length
    for i in range(7):  # Place 7 stepping stones
        stone_distance = random.uniform(min_stone_distance, max_stone_distance)
        center_x = cur_x + m_to_idx(stone_distance)
        center_y = mid_y + random.randint(m_to_idx(-0.5), m_to_idx(0.5))  # Allow small y deviations

        add_stone(center_x, center_y)

        # Place a goal at the middle of each stone
        goals[i + 1] = [center_x, center_y]

        cur_x = center_x  # Update the current x for the next stone
    
    # Ensure last part of terrain is flat, setting final goal
    final_running_length = m_to_idx(2)
    height_field[cur_x + m_to_idx(0.5):cur_x + final_running_length, :] = 0
    goals[-1] = [cur_x + m_to_idx(1), mid_y]

    return height_field, goals

def set_terrain_18(length, width, field_resolution, difficulty):
    """Series of stepped blocks for the robot to navigate over in a zigzag pattern."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up block dimensions
    block_length = 1.0 - 0.2 * difficulty
    block_length = m_to_idx(block_length)
    block_width = np.random.uniform(0.4, 0.8)
    block_width = m_to_idx(block_width)
    block_height_min, block_height_max = 0.1, 0.4
    block_gap = 0.2 + 0.6 * difficulty
    block_gap = m_to_idx(block_gap)

    mid_y = m_to_idx(width) // 2

    def add_block(start_x, mid_y, height):
        half_width = block_width // 2
        x1, x2 = start_x, start_x + block_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = 0.0, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    direction = 1
    for i in range(7):  # Set up 7 blocks in zigzag manner
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max) * direction
        block_height = np.random.uniform(block_height_min, block_height_max)

        add_block(cur_x, mid_y + dy, block_height)
        goals[i+1] = [cur_x + (block_length + dx) / 2, mid_y + dy]

        cur_x += block_length + dx + block_gap
        direction *= -1  # alternate direction to create a zigzag pattern

    # Add final goal after the last block
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_19(length, width, field_resolution, difficulty):
    """Combination of staggered elevated platforms, directional ramps, and narrow balance beams to challenge navigation, balance, and agility."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    mid_y = m_to_idx(width) // 2

    platform_min_len, platform_max_len = 0.8, 1.2  # meters
    platform_min_width, platform_max_width = 0.4, 0.8  # meters
    platform_height_min, platform_height_max = 0.1, 0.3 + 0.2 * difficulty  # meters
    gap_min_len, gap_max_len = 0.4, 0.8 + 0.4 * difficulty  # meters
    
    def add_platform(start_x, platform_length, platform_width, height):
        half_width = platform_width // 2
        height_field[start_x:(start_x + platform_length), (mid_y - half_width):(mid_y + half_width)] = height

    def add_ramp(start_x, ramp_length, platform_width, height_start, height_end):
        half_width = platform_width // 2
        height_field[start_x:(start_x + ramp_length), (mid_y - half_width):(mid_y + half_width)] = np.linspace(height_start, height_end, ramp_length).reshape(-1, 1)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # First goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]
    
    # Initialize current x
    cur_x = spawn_length
    for i in range(1, 8):
        # Randomize the next platform/beam parameters
        platform_length = np.random.uniform(platform_min_len, platform_max_len)
        platform_length = m_to_idx(platform_length)
        platform_width = np.random.uniform(platform_min_width, platform_max_width)
        platform_width = m_to_idx(platform_width)
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        
        if i % 3 == 0:
            # Every 3rd obstacle is a ramp
            ramp_length = platform_length
            height_start = platform_height
            height_end = np.random.uniform(platform_height_min, platform_height_max)
            add_ramp(cur_x, ramp_length, platform_width, height_start, height_end)
            platform_height = height_end
        else:
            # Add a normal platform
            add_platform(cur_x, platform_length, platform_width, platform_height)

        # Set the goal on this platform
        goals[i] = [cur_x + platform_length // 2, mid_y]

        # Advance cur_x accounting for the length of the current obstacle and a random gap
        gap_length = np.random.uniform(gap_min_len, gap_max_len)
        gap_length = m_to_idx(gap_length)
        cur_x += platform_length + gap_length

    # Add final goal after the last platform
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    
    return height_field, goals

def set_terrain_20(length, width, field_resolution, difficulty):
    """Narrow balance beams of varying widths and heights for the robot to traverse."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up beam dimensions
    beam_length = 1.0 - 0.3 * difficulty
    beam_length = m_to_idx(beam_length)
    beam_width_min, beam_width_max = 0.4, 1.0 - 0.6 * difficulty
    beam_height_min, beam_height_max = 0.1 + 0.2 * difficulty, 0.2 + 0.4 * difficulty
    gap_length = 0.1 + 0.3 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, mid_y, beam_width, beam_height):
        half_width = m_to_idx(beam_width / 2)
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = beam_height

    dx_min, dx_max = -0.05, 0.05
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
        beam_width = np.random.uniform(beam_width_min, beam_width_max)
        beam_height = np.random.uniform(beam_height_min, beam_height_max)
        
        add_beam(cur_x, cur_x + beam_length + dx, mid_y + dy, beam_width, beam_height)

        # Put goal in the center of the beam
        goals[i+1] = [cur_x + (beam_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += beam_length + dx + gap_length
    
    # Add final goal behind the last beam, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_21(length, width, field_resolution, difficulty):
    """Stepping platforms at varying heights and widths for the quadruped to step or jump up and down different levels."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform dimensions variables
    base_platform_length = 1.5 - 0.5 * difficulty
    platform_length = m_to_idx(base_platform_length)
    platform_width_low, platform_width_high = 1.0, 1.5
    platform_height_min, platform_height_max = 0.1 + 0.1 * difficulty, 0.3 + 0.5 * difficulty
    gap_length = 0.2 + 0.8 * difficulty
    gap_length = m_to_idx(gap_length)

    height_field[:m_to_idx(2),:] = 0
    
    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, center_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = center_y - half_width, center_y + half_width
        height_field[x1:x2, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at spawn

    last_x = spawn_length
    for i in range(1, 8):
        platform_length = m_to_idx(base_platform_length + 0.2 * difficulty * (i % 2))
        platform_width = np.random.uniform(platform_width_low, platform_width_high)
        platform_width = m_to_idx(platform_width)
        platform_height = np.random.uniform(platform_height_min, platform_height_max)

        if i % 2 == 0:
            current_gap_length = int(gap_length * 0.7)
        else:
            current_gap_length = gap_length

        start_x = last_x + current_gap_length
        end_x = start_x + platform_length
        center_y = mid_y + np.random.choice([-1, 1]) * np.random.randint(0, m_to_idx(0.3))

        add_platform(start_x, end_x, center_y, platform_height)

        goals[i] = [start_x + (platform_length) / 2, center_y]

        last_x = end_x

    return height_field, goals

def set_terrain_22(length, width, field_resolution, difficulty):
    """Multiple sideways-facing ramps, tall platforms, and varying pits for the robot to climb and jump across."""    

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Parameters for platforms and ramps
    platform_length = 1.2 - 0.5 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.2, 1.8)  # Increase platform width
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.3 * difficulty, 0.3 + 0.4 * difficulty
    ramp_height_min, ramp_height_max = 0.2 + 0.4 * difficulty, 0.4 + 0.5 * difficulty
    gap_length = 0.2 + 0.7 * difficulty  # Increase gap length
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
    dy_min, dy_max = 0.0, 0.5  # Increase dy range for more complexity
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at spawn

    # Set remaining area to be a pit
    height_field[spawn_length:, :] = -1.0

    # Add first platform
    cur_x = spawn_length
    dx = np.random.randint(dx_min, dx_max)
    dy = np.random.randint(dy_min, dy_max)
    add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
    goals[1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
    cur_x += platform_length + dx + gap_length

    for i in range(1, 6):  # Set up platforms and ramps
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        direction = (-1) ** i  # Alternate left/right for ramps
        dy = dy * direction

        # Insert ramps and platforms alternatively
        if i % 2: 
            add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, direction)
        else:
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
        
        # Put goal at each alternating obstacle
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length
    
    # Put the last goal behind the last obstacle
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_23(length, width, field_resolution, difficulty):
    """Inclined and Declined Ramps for testing the robot's ability to navigate sloped terrains."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Terrain Specifications
    ramp_length = 1.0 + 0.5 * difficulty  # Ramps get longer with higher difficulty
    ramp_length_idx = m_to_idx(ramp_length)
    ramp_height = 0.1 + 0.3 * difficulty  # Ramps get steeper with higher difficulty
    flat_area_length = 0.5  # Flat area between ramps
    flat_area_length_idx = m_to_idx(flat_area_length)
    
    mid_y = m_to_idx(width) // 2
    ramp_width = m_to_idx(1.2)  # Fixed width for ramps

    def add_ramp(start_x, length, height, direction):
        """Adds a ramp to the height_field, direction can be 'up' or 'down'."""
        if direction == 'up':
            for i in range(length):
                height_field[start_x + i, mid_y - ramp_width // 2 : mid_y + ramp_width // 2] = (i / length) * height
        elif direction == 'down':
            for i in range(length):
                height_field[start_x + i, mid_y - ramp_width // 2 : mid_y + ramp_width // 2] = height - (i / length) * height
    
    # Set spawn area to flat ground
    spawn_length_idx = m_to_idx(2)
    height_field[0:spawn_length_idx, :] = 0
    goals[0] = [spawn_length_idx - m_to_idx(0.5), mid_y]  # First goal at spawn area

    cur_x = spawn_length_idx
    for i in range(6):  # Create 6 ramps
        direction = 'up' if i % 2 == 0 else 'down'
        add_ramp(cur_x, ramp_length_idx, ramp_height, direction)
        
        # Place goal in the middle of the ramp
        goals[i + 1] = [cur_x + ramp_length_idx // 2, mid_y]
        
        # Move current x position to the end of the ramp and add flat area
        cur_x += ramp_length_idx
        height_field[cur_x: cur_x + flat_area_length_idx, mid_y - ramp_width // 2 : mid_y + ramp_width // 2] = ramp_height if direction == 'up' else 0
        cur_x += flat_area_length_idx

    # Final goal after the last ramp
    goals[-1] = [cur_x - m_to_idx(0.5), mid_y]
    
    return height_field, goals

def set_terrain_24(length, width, field_resolution, difficulty):
    """A challenging crisscross path with overlapping beams and platforms to promote agility, balance, and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define properties for beams and platforms
    beam_length = 0.6 + 0.4 * difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = 0.4 + 0.2 * difficulty
    beam_width = m_to_idx(beam_width)
    platform_length = 1.0 + 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 1.0 + 0.4 * difficulty
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.2 + 0.2 * difficulty, 0.4 + 0.2 * difficulty

    gap_length = 0.4 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, start_y, end_x, end_y):
        """Adds a beam to the terrain."""
        beam_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[start_x:end_x, start_y:end_y] = beam_height

    def add_platform(start_x, end_x, mid_y, height):
        """Adds a platform to the terrain."""
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    # Set up spawning area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Create a sequence of beams and platforms
    cur_x = spawn_length
    for i in range(1, 8):
        is_platform = i % 2 == 1  # Alternate between platforms and beams
        if is_platform:
            platform_height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)
            goals[i] = [cur_x + platform_length // 2, mid_y]
            cur_x += platform_length + gap_length
        else:
            add_beam(cur_x, mid_y - beam_width // 2, cur_x + beam_length, mid_y + beam_width // 2)
            goals[i] = [cur_x + beam_length // 2, mid_y]
            cur_x += beam_length + gap_length

    # Finalize terrain by leveling the rest to flat ground
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_25(length, width, field_resolution, difficulty):
    """Staircase challenge with varying step heights for the robot to climb."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define the staircase parameters
    step_height_min, step_height_max = 0.05 * difficulty, 0.2 * difficulty
    step_length = 0.5
    step_length_idx = m_to_idx(step_length)
    step_width = width
    step_width_idx = m_to_idx(step_width)

    mid_y = m_to_idx(width) // 2
    
    def add_step(start_x, height):
        x1 = start_x
        x2 = start_x + step_length_idx
        height_field[x1:x2, :] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Place the first goal at the edge of spawn area
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(7):  # We will create 7 steps
        # Determine step height
        step_height = np.random.uniform(step_height_min, step_height_max)
        
        # Add the step to the height field
        add_step(cur_x, step_height)
        
        # Set a goal at the middle of the step
        goals[i+1] = [cur_x + step_length_idx // 2, mid_y]
        
        # Move to the start of the next step
        cur_x += step_length_idx

    # Ensure the terrain fits within the specified length
    final_length = height_field.shape[0]
    cur_x = min(cur_x, final_length - step_length_idx)

    return height_field, goals

def set_terrain_26(length, width, field_resolution, difficulty):
    """Walls and narrow pathways to test precision and directional navigation."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Convert the field dimensions to indices
    field_length = m_to_idx(length)
    field_width = m_to_idx(width)
    
    # Create walls and pathways
    wall_height = 0.2 + 0.3 * difficulty  # Height of walls increases with difficulty
    wall_width = m_to_idx(0.1)  # Width for narrow walls
    pathway_width = np.random.uniform(0.4, 0.6)  # Randomize narrow pathways
    pathway_width = m_to_idx(pathway_width)
   
    # Define mid-line and boundaries
    mid_y = field_width // 2
    start_x = m_to_idx(2)
    
    def add_wall(x_start, x_end, y_center):
        half_width = wall_width // 2
        height_field[x_start:x_end, y_center - half_width:y_center + half_width] = wall_height

    def add_pathway(x_start, x_end, y_center):
        half_width = pathway_width // 2
        height_field[x_start:x_end, y_center - half_width:y_center + half_width] = 0

    # Mark the initial flat region where the robot spawns
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(1), mid_y]

    cur_x = spawn_length
    for i in range(6):  # We create 6 sections of walls and pathways
        # Alternate between adding walls and pathways
        if i % 2 == 0:
            # Add a wall section
            add_wall(cur_x, cur_x + m_to_idx(1.5), mid_y)
            # Move the current x forward
            cur_x += m_to_idx(1.5)

            # Set goal just after the wall for navigation
            goals[i+1] = [cur_x, mid_y]
            
        else:
            # Add a pathway section
            add_pathway(cur_x, cur_x + m_to_idx(1.5), mid_y)
            cur_x += m_to_idx(1.5)
            
            # Shift y-axis for narrow pathways
            shift = np.random.choice([-1, 1]) * np.random.randint(m_to_idx(0.5), m_to_idx(1))
            new_mid_y = mid_y + shift
            
            if 0 <= new_mid_y < field_width - pathway_width:
                mid_y = new_mid_y
            
            # Set goal at the end of the pathway
            goals[i+1] = [cur_x, mid_y]

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    
    # Ensure remaining area is flat
    height_field[cur_x:, :] = 0
    
    return height_field, goals

def set_terrain_27(length, width, field_resolution, difficulty):
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

def set_terrain_28(length, width, field_resolution, difficulty):
    """Stepping stone terrain for the robot to navigate with varying heights and distances."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Stepping stones dimensions and placements
    stone_length = 0.4  # Keeps minimum size due to robot's constraints
    stone_length = m_to_idx(stone_length)
    stone_height_min = 0.05 * difficulty
    stone_height_max = 0.3 + 0.4 * difficulty
    stone_spacing = 1.0  # Base gap between stones
    stone_spacing = m_to_idx(stone_spacing)

    mid_y = m_to_idx(width) // 2

    def add_stone(x_index, y_index, stone_height):
        half_length = stone_length // 2
        x1, y1 = x_index - half_length, y_index - half_length
        x2, y2 = x_index + half_length, y_index + half_length
        height_field[x1:x2, y1:y2] = stone_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at the end of spawn area

    cur_x = spawn_length
    for i in range(7):  # Setting up 7 stepping stones
        height_variation = np.random.uniform(stone_height_min, stone_height_max)
        add_stone(cur_x, mid_y, height_variation)

        # Set a goal at the center of each stepping stone
        goals[i+1] = [cur_x, mid_y]

        # Add spacing for next stone
        cur_x += stone_length + stone_spacing

    return height_field, goals

def set_terrain_29(length, width, field_resolution, difficulty):
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

def set_terrain_30(length, width, field_resolution, difficulty):
    """Narrow beams, wide platforms, and varying height ramps for the robot to balance, climb, and jump."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Parameters for platforms and beams
    platform_length = 1.0 - 0.1 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.2, 2.0)  # Wider platforms
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.1 + 0.4 * difficulty
    gap_length = 0.2 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    beam_length = 1.0 - 0.2 * difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = 0.4 - 0.1 * difficulty  # Narrow beams
    beam_width = m_to_idx(beam_width)
    beam_height_min, beam_height_max = 0.1 + 0.2 * difficulty, 0.2 + 0.4 * difficulty

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
        beam_height = np.random.uniform(beam_height_min, beam_height_max)
        height_field[x1:x2, y1:y2] = beam_height

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
    for i in range(4):  # Create 4 platforms
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)

        # Put goal in the center of the platform
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += platform_length + dx + gap_length

    for i in range(4, 7):  # Create 3 beams
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_beam(cur_x, cur_x + beam_length + dx, mid_y + dy)

        # Put goal in the center of the beam
        goals[i+1] = [cur_x + (beam_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += beam_length + dx + gap_length

    # Add final goal behind the last beam, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_31(length, width, field_resolution, difficulty):
    """Combination of narrow beams, balanced ramps, and varied-height platforms for increased difficulty and feasibility."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up obstacle dimensions
    platform_length = m_to_idx(1.0 - 0.2 * difficulty)
    platform_width = m_to_idx(np.random.uniform(0.9, 1.3))
    platform_height_min, platform_height_max = 0.0 + 0.3 * difficulty, 0.05 + 0.35 * difficulty
    ramp_length = m_to_idx(1.5 - 0.3 * difficulty)
    ramp_width = m_to_idx(0.4 - 0.05 * difficulty)
    ramp_height_min, ramp_height_max = 0.0 + 0.4 * difficulty, 0.05 + 0.45 * difficulty
    beam_width = m_to_idx(0.35 - 0.05 * difficulty)
    gap_length = m_to_idx(0.5 + 0.4 * difficulty)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_ramp(start_x, end_x, mid_y, direction):
        half_width = ramp_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        slant = np.linspace(0, ramp_height, num=end_x - start_x)[::direction]  # Create gradient
        height_field[x1:x2, y1:y2] = slant[:, None]

    def add_beam(start_x, end_x, mid_y):
        half_width = beam_width // 2
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
    obstacle_types = [add_platform, add_ramp, add_beam]
    for i in range(7):
        obstacle = obstacle_types[i % 3]
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        if obstacle == add_ramp:
            direction = 1 if i % 4 < 2 else -1  # Alternate ramp directions
            obstacle(cur_x, cur_x + ramp_length + dx, mid_y + dy, direction)
            goals[i + 1] = [cur_x + m_to_idx(0.75) + dx // 2, mid_y + dy]
            cur_x += ramp_length + dx + gap_length
        elif obstacle == add_beam:
            obstacle(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i + 1] = [cur_x + platform_length // 2, mid_y + dy]
            cur_x += platform_length + gap_length
        else:
            obstacle(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i + 1] = [cur_x + platform_length // 2, mid_y + dy]
            cur_x += platform_length + gap_length

    goals[-1] = [cur_x - m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_32(length, width, field_resolution, difficulty):
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

def set_terrain_33(length, width, field_resolution, difficulty):
    """Uneven steps with varying heights for the robot to navigate and balance on."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    
    step_length = m_to_idx(1.0)  # Length of each step
    step_width = m_to_idx(1.0)   # Width of each step, ensuring it’s wide enough
    step_height_min = 0.1 * difficulty  # Minimum step height based on difficulty
    step_height_max = 0.25 * difficulty  # Maximum step height based on difficulty
    
    def add_step(start_x, end_x, start_y, end_y, height):
        height_field[start_x:end_x, start_y:end_y] = height

    # Initial flat area for spawning
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), m_to_idx(width) // 2]  # Initial goal near the spawn

    cur_x = spawn_length
    mid_y = m_to_idx(width) // 2

    # Generate 7 uneven steps
    for i in range(7):
        step_height = random.uniform(step_height_min, step_height_max)
        add_step(cur_x, cur_x + step_length, mid_y - step_width // 2, mid_y + step_width // 2, step_height)
        
        # Set the goal in the middle of each step
        goals[i + 1] = [cur_x + step_length / 2, mid_y]
        
        # Move to the next step position
        cur_x += step_length
        
    return height_field, goals

def set_terrain_34(length, width, field_resolution, difficulty):
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

def set_terrain_35(length, width, field_resolution, difficulty):
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

def set_terrain_36(length, width, field_resolution, difficulty):
    """Mixed obstacles include taller steps, varied gaps, and angled platforms for increased difficulty."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Setup platform dimensions with increased complexity
    platform_length = 0.8 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 0.6 - 0.1 * difficulty
    platform_width = m_to_idx(platform_width)
    platform_height_base = 0.15
    platform_height_var = 0.15 * difficulty
    gap_length_min = 0.2
    gap_length_max = 0.5 + 0.5 * difficulty
    gap_length_min = m_to_idx(gap_length_min)
    gap_length_max = m_to_idx(gap_length_max)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, height, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_step(start_x, end_x, height):
        step_width = m_to_idx(0.4)
        half_width = step_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)
    
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    current_x = spawn_length
    num_obstacles = 7  # Increase number of obstacles

    for i in range(num_obstacles):
        platform_height = platform_height_base + np.random.uniform(0, platform_height_var)
        add_platform(current_x, current_x + platform_length, platform_height, mid_y)
        goals[i+1] = [current_x + platform_length // 2, mid_y]

        gap_length = random.randint(gap_length_min, gap_length_max)
        current_x += platform_length + gap_length

    # Filling in the remaining part
    height_field[current_x:, :] = 0
    goals[-1] = [m_to_idx(length - 0.5), mid_y]

    return height_field, goals

def set_terrain_37(length, width, field_resolution, difficulty):
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

def set_terrain_38(length, width, field_resolution, difficulty):
    """Irregular stepping stones and varied-height platforms with small gaps for balance and jumping."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and stepping stone dimensions
    stone_length = 0.75 - 0.15 * difficulty
    stone_length = m_to_idx(stone_length)
    stone_width = 0.35  # Narrower for balance, maintaining as feasible
    stone_width = m_to_idx(stone_width)
    stone_height_min, stone_height_max = 0.05 + 0.30 * difficulty, 0.10 + 0.4 * difficulty
    gap_length = 0.1 + 0.4 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_stepping_stone(start_x, mid_y, stone_height):
        half_width = stone_width // 2
        end_x = start_x + stone_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[start_x:end_x, y1:y2] = stone_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0    
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at spawn

    # Begin sequence of uneven stepping stones
    cur_x = spawn_length    
    for i in range(6):  # Set up 6 stepping stones
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        stone_height = np.random.uniform(stone_height_min, stone_height_max)
        add_stepping_stone(cur_x, mid_y + dy, stone_height)
        
        # Add goal at center of the stone
        goals[i+1] = [cur_x + stone_length / 2 + dx, mid_y + dy]
        
        # Add gap between stones
        cur_x += stone_length + gap_length + dx

    # Add final goal and ensure flat ground at the end
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_39(length, width, field_resolution, difficulty):
    """Narrow balance beams at varying heights and gaps for the robot to traverse."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set balance beam dimensions
    beam_width = 0.4  # minimum width of the balance beam
    beam_width_idx = m_to_idx(beam_width)
    beam_length = 2.0 - 0.3 * difficulty   # varying length of the beam based on difficulty
    beam_length_idx = m_to_idx(beam_length)
    max_beam_height = 0.6  # max height of a balance beam can be 0.6 meters
    gap_length_idx = m_to_idx(0.3 + 0.4 * difficulty)  # gaps get larger as difficulty increases

    def add_beam(start_x, end_x, mid_y, height):
        half_width_idx = beam_width_idx // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width_idx, mid_y + half_width_idx
        height_field[x1:x2, y1:y2] = height

    mid_y = m_to_idx(width) // 2
    
    # Set spawn area to flat ground
    spawn_length_idx = m_to_idx(2)
    height_field[0:spawn_length_idx, :] = 0
    
    # Put first goal at spawn
    goals[0] = [spawn_length_idx - m_to_idx(0.5), mid_y]
    
    cur_x = spawn_length_idx

    for i in range(6):
        # Determine the height of the current beam (height gets taller with difficulty)
        beam_height = max_beam_height * (i / 6 * difficulty)
        
        # Add the balance beam to the height_field
        add_beam(cur_x, cur_x + beam_length_idx, mid_y, beam_height)

        # Set goal for robot in the middle of the beam
        goals[i + 1] = [cur_x + beam_length_idx // 2, mid_y]

        # Add gap to the next beam
        cur_x += beam_length_idx + gap_length_idx

    # Add final goal after last beam, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

# INSERT TERRAIN FUNCTION DEFINITIONS HERE
