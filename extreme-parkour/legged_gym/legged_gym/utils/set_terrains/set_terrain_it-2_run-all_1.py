
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
    """Alternating platforms with narrow bridges and zigzag paths for advanced navigation and balance testing."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    mid_y = m_to_idx(width / 2)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Initial platform parameters
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = m_to_idx(0.4)  # Narrow platform
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.3 + 0.5 * difficulty
    gap_length = 0.1 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    cur_x = spawn_length
    for i in range(6):
        dx = random.randint(-m_to_idx(0.1), m_to_idx(0.1))
        dy = random.randint(-m_to_idx(0.4), m_to_idx(0.4))
        platform_height = random.uniform(platform_height_min, platform_height_max)

        # Add platform
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height)
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Add narrow bridge or gap
        cur_x += platform_length + dx + gap_length
        if i % 2 == 1:  # Add narrow bridge every other platform
            bridge_length = m_to_idx(0.6 + 0.5 * difficulty)
            bridge_width = m_to_idx(0.2)
            bridge_mid_y = mid_y + random.randint(-m_to_idx(0.5), m_to_idx(0.5))
            height_field[cur_x:cur_x + bridge_length, bridge_mid_y - bridge_width//2:bridge_mid_y + bridge_width//2] = platform_height

            goals[i+1] = [cur_x + bridge_length // 2, bridge_mid_y]
            cur_x += bridge_length

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_1(length, width, field_resolution, difficulty):
    """Combination of platforms and ramps to traverse a pit for the robot to climb on and jump across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define dimensions and properties of platforms and ramps
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.2)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.2 * difficulty, 0.1 + 0.3 * difficulty
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
        ramp_height = np.random.uniform(platform_height_min, platform_height_max)
        slant = np.linspace(0, ramp_height, num=x2-x1)
        slant = slant[::direction]
        slant = slant[:, None]  # Add a dimension for broadcasting to y
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy = m_to_idx(0.4)  # Consistent y offset

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Set remaining area to be a pit
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    for i in range(4):  # Set up 4 platforms
        dx = np.random.randint(dx_min, dx_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y)

        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y]

        cur_x += platform_length + dx + gap_length

    for i in range(4, 7):  # Set up 3 ramps
        dx = np.random.randint(dx_min, dx_max)
        direction = (-1) ** i  # Alternate left and right ramps
        add_ramp(cur_x, cur_x + platform_length + dx, mid_y, direction)

        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y]

        cur_x += platform_length + dx + gap_length
    
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_2(length, width, field_resolution, difficulty):
    """A series of hurdles each with varying heights for the robot to jump over."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # Starting position for the quadruped
    starting_x = spawn_length
    mid_y = m_to_idx(width/2)

    # Set first goal
    goals[0] = [starting_x, mid_y]

    # Dimensions for hurdles
    hurdle_height_min = 0.1 * difficulty  # Minimum height of hurdles
    hurdle_height_max = 0.4 * difficulty  # Maximum height of hurdles
    hurdle_width = m_to_idx(1)  # 1 meter width
    hurdle_gap_min = m_to_idx(0.5 + 0.5 * difficulty) # Minimum gap between hurdles
    hurdle_gap_max = m_to_idx(1 + 1 * difficulty) # Maximum gap between hurdles

    num_hurdles = 6  # Number of hurdles to place

    for i in range(1, num_hurdles+1):
        # Randomly determine the height of the hurdle
        height = np.random.uniform(hurdle_height_min, hurdle_height_max)

        # Place the hurdle at the current position
        height_field[starting_x:starting_x + hurdle_width, :] = height

        # Set the goal location just before the start of the next hurdle
        goals[i] = [starting_x + hurdle_width + hurdle_gap_min//2, mid_y]

        # Move starting_x to the position after the gap
        starting_x += hurdle_width + np.random.randint(hurdle_gap_min, hurdle_gap_max)

    # Final goal, positioned at the end of the terrain.
    goals[-1] = [m_to_idx(length - 1), mid_y]

    return height_field, goals

def set_terrain_3(length, width, field_resolution, difficulty):
    """Combines jumping gaps, narrow platforms, and varied-height platforms for the quadruped to navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Parameters
    platform_width_min, platform_width_max = 0.4, 1.0  # Testing balance by making platforms narrower
    gap_width = 0.2 + 0.5 * difficulty  # Increase gap width with difficulty
    platform_height_min, platform_height_max = 0.05 + 0.20 * difficulty, 0.1 + 0.35 * difficulty

    platform_width_min, platform_width_max = m_to_idx([platform_width_min, platform_width_max])
    gap_width = m_to_idx(gap_width)
    mid_y = m_to_idx(width) // 2

    # Function to create a platform
    def add_platform(start_x, length, width, height, mid_y):
        half_width = width // 2
        height_field[start_x:start_x+length, mid_y-half_width:mid_y+half_width] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at the spawn point

    # Create terrain
    cur_x = spawn_length
    for i in range(7):
        # Determine platform parameters
        platform_length = m_to_idx(1.0)  # Fixed length for uniformity
        platform_width = np.random.randint(platform_width_min, platform_width_max)
        platform_height = np.random.uniform(platform_height_min, platform_height_max)

        # Create platform
        add_platform(cur_x, platform_length, platform_width, platform_height, mid_y)

        # Set goal on the platform
        goals[i+1] = [cur_x + platform_length // 2, mid_y]
        
        # Add gap before the next platform
        cur_x += platform_length + gap_width

    # Fill the rest of the terrain to flat ground
    height_field[cur_x:, :] = 0
    goals[-1] = [m_to_idx(length) - m_to_idx(0.5), mid_y]  # Make sure final goal is within bounds

    return height_field, goals

def set_terrain_4(length, width, field_resolution, difficulty):
    """Narrow passages with varying heights for the robot to maneuver on."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define beam characteristics
    beam_length = m_to_idx(0.4 + 0.2 * difficulty)  # Varies from 0.4m to 0.6m depending on difficulty
    beam_width = m_to_idx(0.4)  # Constant width

    # Heights will have more variation with increased difficulty
    min_height = 0.05 * difficulty
    max_height = 0.2 + 0.3 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_beam(x, y_center):
        y1 = y_center - beam_width // 2
        y2 = y_center + beam_width // 2
        beam_height = np.random.uniform(min_height, max_height)
        height_field[x:x + beam_length, y1:y2] = beam_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [m_to_idx(1), mid_y]  # First goal at the spawn area

    cur_x = spawn_length
    dx_range = m_to_idx([-0.1, 0.1])  # Small variation in x direction
    dy_range = m_to_idx([-0.5 + 0.3 * difficulty, 0.5 - 0.3 * difficulty])  # Larger variation in y direction for difficulty

    for i in range(7):  # Set up 7 beams
        dx = np.random.randint(dx_range[0], dx_range[1])
        dy = np.random.randint(dy_range[0], dy_range[1])
        add_beam(cur_x + dx, mid_y + dy)

        # Place goal within each beam
        goals[i+1] = [cur_x + dx + beam_length // 2, mid_y + dy]

        # Pass to the next beam
        cur_x += beam_length + dx

    return height_field, goals

def set_terrain_5(length, width, field_resolution, difficulty):
    """Series of stepping stone platforms of varying heights for the robot to jump across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    def add_platform(start_x, start_y, platform_width, platform_length, platform_height):
        end_x = start_x + m_to_idx(platform_length)
        end_y = start_y + m_to_idx(platform_width)
        height_field[start_x:end_x, start_y:end_y] = platform_height

    # Convert sizes to indices
    course_length = m_to_idx(length)
    course_width = m_to_idx(width)
    quadruped_length = m_to_idx(0.645)
    quadruped_width = m_to_idx(0.28)

    # Initial spawn area
    height_field[0:m_to_idx(2), :] = 0
    goals[0] = [m_to_idx(1), course_width // 2]

    # Initial platform properties
    platform_length = 0.8 - 0.2 * difficulty
    platform_width = 0.5
    platform_height_min = 0.2 * difficulty
    platform_height_max = platform_height_min + 0.1
    num_platforms = 7

    cur_x = m_to_idx(2)
    platform_gap = 0.2
    platform_gap_idx = m_to_idx(platform_gap)

    for i in range(num_platforms):
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        platform_y = np.random.randint(quadruped_width, course_width - quadruped_width)
        
        add_platform(cur_x, platform_y, platform_width, platform_length, platform_height)
        
        # Set goal position on platform
        goals[i+1] = [cur_x + m_to_idx(platform_length) // 2, platform_y + m_to_idx(platform_width) // 2]

        # Prepare for next platform
        cur_x += m_to_idx(platform_length) + platform_gap_idx
        platform_height_min += 0.05
        platform_height_max += 0.05
        
        # Adjust heights for increasing difficulty
        if i < num_platforms - 1:
            height_field[cur_x:cur_x + platform_gap_idx, :] = 0

    # Final goal
    goals[-1] = [min(cur_x + m_to_idx(platform_length) // 2, course_length - 1), course_width // 2]

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

def set_terrain_8(length, width, field_resolution, difficulty):
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

def set_terrain_9(length, width, field_resolution, difficulty):
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

def set_terrain_10(length, width, field_resolution, difficulty):
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

def set_terrain_11(length, width, field_resolution, difficulty):
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

def set_terrain_12(length, width, field_resolution, difficulty):
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

def set_terrain_13(length, width, field_resolution, difficulty):
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

def set_terrain_14(length, width, field_resolution, difficulty):
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

def set_terrain_15(length, width, field_resolution, difficulty):
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

def set_terrain_20(length, width, field_resolution, difficulty):
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

def set_terrain_21(length, width, field_resolution, difficulty):
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

def set_terrain_22(length, width, field_resolution, difficulty):
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

def set_terrain_23(length, width, field_resolution, difficulty):
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

def set_terrain_24(length, width, field_resolution, difficulty):
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

def set_terrain_25(length, width, field_resolution, difficulty):
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

def set_terrain_26(length, width, field_resolution, difficulty):
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

def set_terrain_27(length, width, field_resolution, difficulty):
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

def set_terrain_28(length, width, field_resolution, difficulty):
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

def set_terrain_29(length, width, field_resolution, difficulty):
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

def set_terrain_30(length, width, field_resolution, difficulty):
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

def set_terrain_31(length, width, field_resolution, difficulty):
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

def set_terrain_32(length, width, field_resolution, difficulty):
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

def set_terrain_33(length, width, field_resolution, difficulty):
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

def set_terrain_34(length, width, field_resolution, difficulty):
    """Complex elevated and uneven terrain for enhanced difficulty, testing the robot's balance and climbing abilities."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Dimensions for platforms and uneven terrain sections
    platform_length = 0.8 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.6, 1.0)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.4 * difficulty, 0.6 * difficulty
    uneven_terrain_height_var = 0.2 * difficulty

    gap_length = 0.3 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_uneven_terrain(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        for i in range(x1, x2):
            for j in range(y1, y2):
                height_field[i, j] = np.random.uniform(-uneven_terrain_height_var, uneven_terrain_height_var)

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(4):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        if i % 2 == 0:
            # Add platforms
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        else:
            # Add uneven terrain sections instead of gaps
            add_uneven_terrain(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Add gap always after a platform
        cur_x += platform_length + dx + gap_length

    # Ensure additional difficulty by adding taller platforms towards the end
    for i in range(4, 7):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

    # Final goal behind the last platform
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_35(length, width, field_resolution, difficulty):
    """Angular platforms and tilted steps to challenge the robot's adaptability and agility."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and angular step dimensions
    platform_length = 1.2 - 0.4 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.2)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.3 * difficulty, 0.1 + 0.4 * difficulty
    step_height_min, step_height_max = 0.1 + 0.5 * difficulty, 0.2 + 0.6 * difficulty
    gap_length = 0.2 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_step(start_x, end_x, mid_y, direction):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        step_height = np.random.uniform(step_height_min, step_height_max)
        slant = np.linspace(0, step_height, num=y2-y1)[::direction]
        slant = slant[None, :]  # Add a dimension for broadcasting to x
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.05, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.0, 0.4  # Polarity of dy will alternate instead of being random
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Set remaining area to be a pit
    # We do this to force the robot to jump from platform to platform
    # Otherwise, the robot can just jump down and climb back up
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    for i in range(6):  # Set up 6 platforms and steps
        if i % 2 == 0:
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)

            # Put goal in the center of the platform
            goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        else:
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)
            direction = (-1) ** i  # Alternate left and right steps
            dy = dy * direction  # Alternate positive and negative y offsets
            add_step(cur_x, cur_x + platform_length + dx, mid_y + dy, direction)

            # Put goal in the center of the step
            goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        
        # Add gap
        cur_x += platform_length + dx + gap_length
    
    # Add final goal behind the last obstacle, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_36(length, width, field_resolution, difficulty):
    """Multiple ramps with increasing steepness for the robot to climb on."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    ramp_length = 1.2 - 0.2 * difficulty  # Ramps get shorter as difficulty increases, making climbing harder
    ramp_length = m_to_idx(ramp_length)
    ramp_width = 1.0  # Fixed width for stability
    ramp_width = m_to_idx(ramp_width)
    ramp_height_max = 0.2 + 0.3 * difficulty
    gap_length = 0.1 + 0.3 * difficulty  # Varying gap lengths to control difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_ramp(start_x, end_x, mid_y):
        half_width = ramp_width // 2
        height = np.linspace(0, np.random.uniform(0.1, ramp_height_max), end_x - start_x)
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        for i in range(len(height)):
            height_field[x1+i, y1:y2] = height[i]

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(6):  # Set up 6 ramps
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_ramp(cur_x, cur_x + ramp_length + dx, mid_y + dy)

        # Put goal in the center of the ramp
        goals[i+1] = [cur_x + (ramp_length + dx) // 2, mid_y + dy]

        # Add gap
        cur_x += ramp_length + dx + gap_length

    # Add final goal behind the last ramp, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_37(length, width, field_resolution, difficulty):
    """Narrow walkways with varying heights and widths designed to test balance and precision stepping."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Narrow walkway dimensions
    walkway_length = 1.0 + 0.5 * difficulty  # Increasing length based on difficulty
    walkway_length = m_to_idx(walkway_length)
    walkway_height_min, walkway_height_max = 0.1 + 0.3 * difficulty, 0.2 + 0.5 * difficulty
    walkway_width = np.random.uniform(0.4, 1.0)  # Narrow but within the limits
    walkway_width = m_to_idx(walkway_width)

    # Initial spawn area
    spawn_length = m_to_idx(2)
    mid_y = m_to_idx(width) // 2
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    def add_walkway(start_x, end_x, mid_y, height):
        half_width = walkway_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = -m_to_idx(0.1), m_to_idx(0.1)
    dy_min, dy_max = -m_to_idx(0.5), m_to_idx(0.5)

    # Generate walkways
    for i in range(7):  # Create 7 walkways
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        walkway_height = np.random.uniform(walkway_height_min, walkway_height_max)

        add_walkway(cur_x, cur_x + walkway_length + dx, mid_y + dy, walkway_height)

        # Set goal
        goals[i + 1] = [cur_x + (walkway_length + dx) // 2, mid_y + dy]

        # Move to the next segment
        cur_x += walkway_length + dx

    # Ensuring the last goal is placed within bounds
    goals[-1] = [m_to_idx(length-1), mid_y]

    return height_field, goals

def set_terrain_38(length, width, field_resolution, difficulty):
    """Series of narrow walkways and jumps testing balance and agility of the quadruped."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up walkway dimensions based on difficulty
    walkway_width_min, walkway_width_max = 0.4, 0.7
    walkway_width_min, walkway_width_max = m_to_idx(walkway_width_min), m_to_idx(walkway_width_max)
    walkway_height_min, walkway_height_max = 0.1, 0.5
    gap_length = 0.2 + 0.8 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_walkway(start_x, end_x, mid_y, difficulty):
        width = random.randint(walkway_width_min, walkway_width_max)
        height = np.random.uniform(walkway_height_min, walkway_height_max)
        
        if difficulty > 0.5:
            # To make it harder, vary widths along the walkway
            for i in range(start_x, end_x, width):
                height_field[i:i+width, mid_y-width//2:mid_y+width//2] = height
        else:
            height_field[start_x:end_x, mid_y-width//2:mid_y+width//2] = height

    dx_min, dx_max = m_to_idx(0.2), m_to_idx(0.4)
    dy_min, dy_max = m_to_idx(-0.5), m_to_idx(0.5)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Place the first goal at the spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(6):
        dx = random.randint(dx_min, dx_max)
        dy = random.randint(dy_min, dy_max)
        walkway_length = m_to_idx(1.5 + 0.3 * difficulty)
        add_walkway(cur_x, cur_x + walkway_length + dx, mid_y + dy, difficulty)

        # Place goal in the center of the walkway
        goals[i + 1] = [cur_x + (walkway_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += walkway_length + dx + gap_length

    # Place final goal on flat ground behind the last walkway, fill the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_39(length, width, field_resolution, difficulty):
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

# INSERT TERRAIN FUNCTION DEFINITIONS HERE
