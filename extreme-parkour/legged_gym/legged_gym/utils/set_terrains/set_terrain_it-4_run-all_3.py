
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

def set_terrain_1(length, width, field_resolution, difficulty):
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

def set_terrain_2(length, width, field_resolution, difficulty):
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

def set_terrain_3(length, width, field_resolution, difficulty):
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

def set_terrain_4(length, width, field_resolution, difficulty):
    """Series of slopes and alternating narrow platforms, testing the robot's ability to traverse changing elevations and gaps."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.0)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.15 * difficulty, 0.3 * difficulty
    slope_height_min, slope_height_max = 0.1, 0.5 * difficulty
    gap_length = 0.1 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)
    mid_y = m_to_idx(width) // 2

    def create_slope(start_x, end_x, mid_y, slope_height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = np.linspace(0, slope_height, x2 - x1).reshape(-1, 1)

    def create_narrow_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 4
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    # Create Slopes and Platforms
    for i in range(7):
        slope_height = np.random.uniform(slope_height_min, slope_height_max)
        create_slope(cur_x, cur_x + platform_length, mid_y, slope_height)
        cur_x += platform_length
        goals[i + 1] = [cur_x - m_to_idx(0.5), mid_y]
        
        if i % 2 == 0:  # Every other goal introduces a narrow platform
            height = np.random.uniform(platform_height_min, platform_height_max)
            create_narrow_platform(cur_x, cur_x + platform_length, mid_y, height)
            cur_x += platform_length + gap_length

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_5(length, width, field_resolution, difficulty):
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

def set_terrain_6(length, width, field_resolution, difficulty):
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

def set_terrain_7(length, width, field_resolution, difficulty):
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

def set_terrain_8(length, width, field_resolution, difficulty):
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

def set_terrain_9(length, width, field_resolution, difficulty):
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

def set_terrain_10(length, width, field_resolution, difficulty):
    """Stepped platforms and narrow beams at varying heights and widths for the quadruped to navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform and beam configurations
    platform_length = 0.5  # Shorter platforms
    platform_length = m_to_idx(platform_length)
    platform_width = 0.5  # Shorter width for complexity
    platform_width = m_to_idx(platform_width)
    beam_length = 1.0 - 0.3 * difficulty  # Slightly longer beams
    beam_length = m_to_idx(beam_length)
    beam_width_factor = 1.0 - 0.7 * difficulty  # Adjustable width
    beam_width_min = max(m_to_idx(0.1), m_to_idx(beam_width_factor * 0.28))
    beam_width_max = m_to_idx(0.4)
    gap_length = 0.2 + 0.2 * difficulty  # Adjustable gaps
    gap_length = m_to_idx(gap_length)
    platform_height_min = 0.1
    platform_height_max = 0.3 + 0.3 * difficulty  # Adjustable height ranges

    mid_y = m_to_idx(width) // 2

    def add_platform_beam(start_x, end_x, mid_y, height, use_beam=False):
        half_width = beam_width_max // 2 if use_beam else platform_width // 2
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[start_x:end_x, y1:y2] = height

    dx_min, dx_max = -0.2, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.15, 0.15
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Flat start area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Create obstacles with alternating platforms and beams
    cur_x = spawn_length
    for i in range(6):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        if i % 2 == 0:
            # Platforms
            platform_height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform_beam(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height)
            
            # Place goal in the center of the platform
            goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
            cur_x += platform_length + dx + gap_length
        else:
            # Beams
            beam_width = np.random.randint(beam_width_min, beam_width_max)
            beam_height = np.random.uniform(platform_height_min, platform_height_max)
            
            half_width = beam_width // 2
            add_platform_beam(cur_x, cur_x + beam_length + dx, mid_y + dy, beam_height, use_beam=True)

            # Place goal in the center of the beam
            goals[i+1] = [cur_x + (beam_length + dx) / 2, mid_y + dy]
            cur_x += beam_length + dx + gap_length

    # Final goal placement
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_11(length, width, field_resolution, difficulty):
    """Zigzag paths with raised platforms and narrow bridges to test dexterity and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length_min = 1.0 - 0.3 * difficulty
    platform_length_max = 1.1 - 0.2 * difficulty
    platform_length_min, platform_length_max = m_to_idx(platform_length_min), m_to_idx(platform_length_max)
    platform_width = 0.3 + 0.4 * difficulty
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.05 + 0.2 * difficulty, 0.15 + 0.4 * difficulty
    bridge_length_min, bridge_length_max = 0.5 + 0.3 * difficulty, 0.7 + 0.5 * difficulty
    bridge_length_min, bridge_length_max = m_to_idx(bridge_length_min), m_to_idx(bridge_length_max)
    bridge_width = 0.25 + 0.2 * difficulty
    bridge_width = m_to_idx(bridge_width)

    dx_min, dx_max = -0.15, 0.15
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -1.0, 1.0
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, length, y_pos):
        x1, x2 = start_x, start_x + length
        y1, y2 = y_pos - platform_width // 2, y_pos + platform_width // 2
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_bridge(start_x, length, y_pos):
        x1, x2 = start_x, start_x + length
        y1, y2 = y_pos - bridge_width // 2, y_pos + bridge_width // 2
        height_field[x1:x2, y1:y2] = 0  # Bridges are at the same level as the previous platform height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    cur_y = mid_y

    for i in range(7):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        length = np.random.randint(platform_length_min, platform_length_max)

        if i % 2 == 0:  # Even indices: platforms
            add_platform(cur_x, length, cur_y + dy)
        else:  # Odd indices: bridges
            length = np.random.randint(bridge_length_min, bridge_length_max)
            add_bridge(cur_x, length, cur_y + dy)

        goals[i + 1] = [cur_x + length // 2, cur_y + dy]

        cur_y += dy
        cur_x += length

    goals[-1] = [cur_x + m_to_idx(1), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_12(length, width, field_resolution, difficulty):
    """Series of staggered beams for the robot to balance and traverse."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up beam dimensions
    # Adjust length, width, and height based on difficulty
    beam_length = 1.5 - 0.5 * difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = 0.4 - 0.1 * difficulty
    beam_width = m_to_idx(beam_width)
    beam_height_min, beam_height_max = 0.1, 0.3 * difficulty
    gap_length = 0.2 + 1.0 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, y):
        x1, x2 = start_x, end_x
        y1, y2 = y - beam_width // 2, y + beam_width // 2
        beam_height = np.random.uniform(beam_height_min, beam_height_max)
        height_field[x1:x2, y1:y2] = beam_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
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
        add_beam(cur_x, cur_x + beam_length + dx, mid_y + dy)

        # Put goal in the center of the beam
        goals[i+1] = [cur_x + (beam_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += beam_length + dx + gap_length
    
    # Add final goal behind the last beam and reset the terrain to flat ground
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals


def set_terrain_13(length, width, field_resolution, difficulty):
    """Dynamic terrain with moving platforms and varying heights for the robot to balance, climb, and jump across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length = 0.4
    platform_length = m_to_idx(platform_length)
    platform_width = 1.0
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.2 * difficulty, 0.1 + 0.3 * difficulty
    gap_length_min, gap_length_max = 0.2, 0.6 + 0.5 * difficulty
    gap_length_min, gap_length_max = m_to_idx(gap_length_min), m_to_idx(gap_length_max)

    ramp_length = 0.8
    ramp_length = m_to_idx(ramp_length)
    ramp_height_min, ramp_height_max = 0.2, 0.4 + 0.3 * difficulty
    
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

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at spawn

    cur_x = spawn_length

    for i in range(4):
        dx = np.random.randint(gap_length_min, gap_length_max)
        dy = np.random.randint(m_to_idx(0.0), m_to_idx(0.6))

        if i % 2 == 0:
            add_platform(cur_x, cur_x + platform_length, mid_y + dy)
            goals[i + 1] = [cur_x + platform_length // 2, mid_y + dy]
        else:
            add_ramp(cur_x, cur_x + ramp_length, mid_y + dy, direction=(-1) ** i)
            goals[i + 1] = [cur_x + ramp_length // 2, mid_y + dy]

        cur_x += platform_length + dx if i % 2 == 0 else ramp_length + dx

    # Adding final straight-run obstacle and a final goal
    final_run_length = m_to_idx(2.5)
    final_run_ramp = m_to_idx(2.0)
    final_run_height = np.random.uniform(0.2, 0.3 + 0.1 * difficulty)
    half_width = platform_width // 2
    y1, y2 = mid_y - half_width, mid_y + half_width
    ramp_height = np.linspace(0, final_run_height, num=final_run_ramp)
    height_field[cur_x:cur_x + final_run_ramp, y1:y2] = ramp_height[:, np.newaxis]
    cur_x += final_run_ramp

    y_current = height_field[cur_x:cur_x + final_run_length, y1:y2][-1, 0]
    height_field[cur_x:cur_x + final_run_length, y1:y2] = y_current  # Ending straight path

    goals[-1] = [cur_x + final_run_length // 2, mid_y]

    return height_field, goals

def set_terrain_14(length, width, field_resolution, difficulty):
    """Staggered platforms, narrow bridges, and mild sloped pathways for the quadruped to climb, balance, and navigate"""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions
    platform_length = m_to_idx(1.0 - 0.3 * difficulty)
    platform_height_min, platform_height_max = 0.05 * difficulty, 0.25 * difficulty
    bridge_width = m_to_idx(0.5 - 0.2 * difficulty)
    gap_length = m_to_idx(0.2 + 0.8 * difficulty)
    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, length, mid_y, height):
        half_width = m_to_idx(1.0) // 2
        height_field[start_x:start_x + length, mid_y - half_width:mid_y + half_width] = height

    def add_bridge(start_x, length, mid_y):
        half_width = bridge_width // 2
        height_field[start_x:start_x + length, mid_y - half_width:mid_y + half_width] = 0.5 * platform_height_max * difficulty

    def add_slope(start_x, length, mid_y, height):
        half_width = m_to_idx(1.0) // 2
        slope = np.linspace(0, height, length)
        slope = slope[:, None]  # Add a dimension for broadcasting to y
        height_field[start_x:start_x + length, mid_y - half_width:mid_y + half_width] = slope

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    # Let's mix platforms, slopes, and bridges
    for i in range(1, 7):  # We have 6 more goals to place
        if i % 2 == 1:
            # Add platform every other goal
            height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, platform_length, mid_y, height)
            goals[i] = [cur_x + platform_length // 2, mid_y]
            cur_x += platform_length + gap_length
        else:
            # Add alternating between bridge and slope
            if np.random.rand() > 0.5:
                add_bridge(cur_x, platform_length, mid_y)
            else:
                height = np.random.uniform(platform_height_min, platform_height_max)
                add_slope(cur_x, platform_length, mid_y, height)
            goals[i] = [cur_x + platform_length // 2, mid_y]
            cur_x += platform_length + gap_length

    # Add final goal behind the last obstacle, fill in remaining gap
    goals[-1] = [m_to_idx(11.5), mid_y]
    height_field[m_to_idx(11):, :] = 0

    return height_field, goals

def set_terrain_15(length, width, field_resolution, difficulty):
    """Combination of staggered steps, variable-height platforms, and safe landing zones for the quadruped."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Adjusted obstacle dimensions
    platform_length = 1.0 - 0.2 * difficulty  # Slightly longer platforms
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.2)  # Increase platform width
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.15 * difficulty, 0.30 * difficulty
    gap_length = 0.1 + 0.4 * difficulty  # Minimized gap length
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, length, width, height, mid_y):
        half_width = width // 2
        height_field[start_x:start_x+length, mid_y-half_width:mid_y+half_width] = height

    def add_ramp(start_x, end_x, mid_y, direction, min_height, max_height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(min_height, max_height)
        slant = np.linspace(0, ramp_height, num=y2-y1)[::direction]
        height_field[x1:x2, y1:y2] = slant
    
    dx = m_to_idx(-0.1)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Flat ground at start
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Remaining area set to low height to allow navigation onto platforms
    height_field[spawn_length:, :] = -1.0

    # First platform
    cur_x = spawn_length
    dy = np.random.randint(dy_min, dy_max)
    add_platform(cur_x, platform_length, platform_width, np.random.uniform(platform_height_min, platform_height_max), mid_y + dy)
    goals[1] = [cur_x + platform_length // 2, mid_y + dy]

    cur_x += platform_length + gap_length
    for i in range(1, 6):
        dy = np.random.randint(dy_min, dy_max)
        if i % 2 == 0:
            add_platform(cur_x, platform_length, platform_width, np.random.uniform(platform_height_min, platform_height_max), mid_y + dy)
        else:
            add_ramp(cur_x, cur_x + platform_length, mid_y + dy, (-1) ** i, platform_height_min, platform_height_max)
        
        goals[i+1] = [cur_x + platform_length // 2, mid_y + dy]
        cur_x += platform_length + gap_length
    
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_16(length, width, field_resolution, difficulty):
    """Platforms of varied heights connected by narrow bridges, with gaps for jumping."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform dimensions
    platform_length = 1.0 - 0.3 * difficulty 
    platform_length = m_to_idx(platform_length)
    platform_width = 1.0
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1, 0.4 * difficulty

    # Bridge dimensions
    bridge_length = 1.2 - 0.2 * difficulty 
    bridge_length = m_to_idx(bridge_length)
    bridge_width = 0.4
    bridge_width = m_to_idx(bridge_width)
    bridge_height = -0.1  # Bridges may have some small descent/upward angle

    # Gap dimensions
    gap_length = 0.2 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_bridge(start_x, end_x, mid_y, height):
        half_width = bridge_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slant = np.linspace(height, height + bridge_height, x2 - x1)
        height_field[x1:x2, y1:y2] = slant[:, None]

    cur_x = m_to_idx(2)  # Ensure clearing the spawn area
    height_field[0:cur_x, :] = 0

    # First goal at spawn area
    goals[0] = [m_to_idx(1), mid_y]

    for i in range(4):
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)
        goals[i + 1] = [cur_x + platform_length // 2, mid_y]
        cur_x += platform_length + gap_length

        bridge_height = np.random.uniform(-0.2, 0.2)
        add_bridge(cur_x, cur_x + bridge_length, mid_y, bridge_height)
        goals[i + 1] = [cur_x + bridge_length // 2, mid_y]
        cur_x += bridge_length + gap_length

    # Final set of platforms and goal
    final_platform_height = np.random.uniform(platform_height_min, platform_height_max)
    add_platform(cur_x, cur_x + platform_length, mid_y, final_platform_height)
    goals[6] = [cur_x + platform_length // 2, mid_y]
    cur_x += platform_length + gap_length

    # Last goal after traversing platforms and bridges
    goals[7] = [cur_x + m_to_idx(1), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_17(length, width, field_resolution, difficulty):
    """Course with alternating stepping platforms and varying-beam widths for the quadruped to balance on, step up, and navigate across gaps."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up obstacle dimensions
    platform_length = 0.8 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    beam_width_min = 0.4 - 0.1 * difficulty
    beam_width_max = 0.8 - 0.1 * difficulty
    beam_width_min = m_to_idx(beam_width_min)
    beam_width_max = m_to_idx(beam_width_max)
    platform_height_min, platform_height_max = 0.1 + 0.05 * difficulty, 0.25 + 0.15 * difficulty
    gap_length = 0.1 + 0.3 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2
    num_platforms = 4  # Alternating platforms

    def add_platform(start_x, end_x, cur_y):
        half_width = (end_x - start_x) // 2
        x1, x2 = start_x, end_x
        y1, y2 = cur_y - half_width, cur_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    # Alternating platforms for stepping
    for i in range(num_platforms):
        dx = np.random.randint(dx_min, dx_max)
        width = np.random.randint(beam_width_min, beam_width_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y)

        # Set goal in the center of the platform
        goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y]

        # Add gap
        cur_x += platform_length + dx + gap_length

    # Add beams of varied widths between platforms
    for i in range(num_platforms, 7):
        dx = np.random.randint(dx_min, dx_max)
        width = np.random.randint(beam_width_min, beam_width_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y)

        # Set goal in the center of the beam
        goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y]

        # Add gap
        cur_x += platform_length + dx + gap_length

    # Add final goal behind the last obstacle
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_18(length, width, field_resolution, difficulty):
    """Series of narrow beams and wider platforms to test precision and balance of the quadruped."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        if isinstance(m, (list, tuple)):
            return [round(i / field_resolution) for i in m]
        else:
            return np.round(m / field_resolution).astype(np.int16)

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Setting up dimensions for beams and platforms
    beam_width = 0.4  # Keep this narrow for balance test
    beam_width = m_to_idx(beam_width)
    beam_length = 1.0  # Length of each beam
    beam_length = m_to_idx(beam_length)

    platform_width = 1.2 + 0.4 * difficulty  # Slightly wider with difficulty
    platform_width = m_to_idx(platform_width)
    platform_length = 1.0
    platform_length = m_to_idx(platform_length)
    platform_height = 0.1 + 0.3 * difficulty

    gap_length = 0.3 + 0.5 * difficulty  # Increase gap with difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, mid_y):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = 0.1  # Beams are slightly above ground to require precision

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = platform_height  # Platforms are a bit higher for resting points

    # Initial flat ground for spawn area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at spawn

    cur_x = spawn_length
    alternate = True  # Alternate between beam and platform

    for i in range(6):  # Creating 6 obstacles (3 beams, 3 platforms)
        if alternate:
            add_beam(cur_x, cur_x + beam_length, mid_y)
            goals[i+1] = [cur_x + beam_length / 2, mid_y]
            cur_x += beam_length + gap_length
        else:
            add_platform(cur_x, cur_x + platform_length, mid_y)
            goals[i+1] = [cur_x + platform_length / 2, mid_y]
            cur_x += platform_length + gap_length

        alternate = not alternate

    # Last part, a wider platform followed by a beam to end
    add_platform(cur_x, cur_x + platform_length, mid_y)
    goals[7] = [cur_x + platform_length / 2, mid_y]
    height_field[cur_x + platform_length:, :] = 0

    return height_field, goals

def set_terrain_19(length, width, field_resolution, difficulty):
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


def set_terrain_20(length, width, field_resolution, difficulty):
    """Stepping stones over varying heights and distances to test stability and jumping abilities."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Stepping stone dimensions
    stone_length = 0.6 - 0.1 * difficulty
    stone_length = m_to_idx(stone_length)
    stone_width = 0.4 + 0.2 * difficulty
    stone_width = m_to_idx(stone_width)
    stone_height_min, stone_height_max = 0.0 + 0.1 * difficulty, 0.1 + 0.2 * difficulty
    gap_length = 0.3 + 0.4 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_stone(center_x, center_y, height):
        half_length = stone_length // 2
        half_width = stone_width // 2
        x_range = slice(center_x - half_length, center_x + half_length)
        y_range = slice(center_y - half_width, center_y + half_width)
        height_field[x_range, y_range] = height

    dx_min, dx_max = -gap_length // 2, gap_length // 2
    dy_min, dy_max = -stone_width // 2, stone_width // 2

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length // 2, mid_y]  # Put first goal at spawn

    cur_x = spawn_length + gap_length
    for i in range(7):  # Set up 7 stepping stones
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        stone_height = np.random.uniform(stone_height_min, stone_height_max)
        add_stone(cur_x + dx, mid_y + dy, stone_height)

        # Put goal in the center of the stone
        goals[i + 1] = [cur_x + dx, mid_y + dy]

        # Add gap
        cur_x += stone_length + gap_length

    return height_field, goals

def set_terrain_21(length, width, field_resolution, difficulty):
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

def set_terrain_22(length, width, field_resolution, difficulty):
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

def set_terrain_23(length, width, field_resolution, difficulty):
    """Series of steps and gentle slopes for the robot to climb and traverse."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define dimensions and heights for steps and slopes
    step_length = 0.6 + 0.2 * difficulty
    step_length = m_to_idx(step_length)
    step_width = 0.6 + 0.1 * difficulty
    step_width = m_to_idx(step_width)
    step_height_min, step_height_max = 0.1, 0.2 + 0.2 * difficulty
    slope_height_min = 0.05
    slope_height_max = 0.15 + 0.1 * difficulty
    
    gap_length = 0.2 + 0.3 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_step(start_x, end_x, mid_y, height):
        half_width = step_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height
    
    def add_slope(start_x, end_x, mid_y, height_change):
        half_width = step_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slope = np.linspace(0, height_change, num=x2-x1)
        slope = slope[:, None]  # Add a dimension for broadcasting to y
        height_field[x1:x2, y1:y2] += slope

    dx_min, dx_max = -0.1, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length + gap_length
    next_goal_idx = 1

    for i in range(4):  # Set up 4 steps
        step_height = np.random.uniform(step_height_min, step_height_max)
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        add_step(cur_x, cur_x + step_length + dx, mid_y + dy, step_height)

        # Put goal in the center of the step
        goals[next_goal_idx] = [cur_x + (step_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += step_length + dx + gap_length
        next_goal_idx += 1

    for i in range(3):  # Set up 3 slopes
        slope_height_change = np.random.uniform(slope_height_min, slope_height_max)
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        add_slope(cur_x, cur_x + step_length + dx, mid_y + dy, slope_height_change)

        # Put goal in the center of the slope
        goals[next_goal_idx] = [cur_x + (step_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += step_length + dx + gap_length
        next_goal_idx += 1

    # Add final goal on flat ground
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_24(length, width, field_resolution, difficulty):
    """Combination of narrow walkways, descending steps, and angled ramps to test balance, climbing, and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up dimensions for features
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    walkway_length = m_to_idx(0.8 - 0.3 * difficulty)
    walkway_width = m_to_idx(0.35 if difficulty > 0.4 else 0.5)
    ramp_length = m_to_idx(1.0 - 0.3 * difficulty)
    gap_length = m_to_idx(0.2 + 0.5 * difficulty)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        height = np.random.uniform(0.15 * difficulty, 0.4 * difficulty)
        half_width = m_to_idx(0.5) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_walkway(start_x, end_x, mid_y):
        height = np.random.uniform(0.1 * difficulty, 0.3 * difficulty)
        half_width = walkway_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

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

    # Set up the starting platform
    cur_x = spawn_length
    dx = np.random.randint(dx_min, dx_max)
    dy = np.random.randint(dy_min, dy_max)
    add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
    goals[1] = [cur_x + (platform_length + dx) // 2, mid_y + dy]
    cur_x += platform_length + dx + gap_length

    # Add a narrow walkway
    dx = np.random.randint(dx_min, dx_max)
    add_walkway(cur_x, cur_x + walkway_length + dx, mid_y)
    goals[2] = [cur_x + (walkway_length + dx) // 2, mid_y]
    cur_x += walkway_length + dx + gap_length

    # Add an alternating height ramp sequence
    for i in range(3, 6):
        dx = np.random.randint(dx_min, dx_max)
        ramp_dir = 1 if i % 2 == 0 else -1
        add_ramp(cur_x, cur_x + ramp_length + dx, mid_y, ramp_dir)
        goals[i] = [cur_x + (ramp_length + dx) // 2, mid_y]
        cur_x += ramp_length + dx + gap_length

    # Add final goal at the end
    goals[6] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_25(length, width, field_resolution, difficulty):
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

def set_terrain_26(length, width, field_resolution, difficulty):
    """Dynamic platforms, rotating beams, and inclined ramps to test the quadruped's adaptability and balance."""

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
    platform_height_min, platform_height_max = 0.0 + 0.2 * difficulty, 0.05 + 0.28 * difficulty

    # Rotating beam parameters
    beam_length = 1.5 - 0.4 * difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = 0.4  # Narrower to test balance
    beam_width = m_to_idx(beam_width)
    
    # Ramp parameters 
    ramp_height_min, ramp_height_max = 0.1 + 0.2 * difficulty, 0.1 + 0.3 * difficulty
    ramp_length = 1.2 - 0.4 * difficulty 
    ramp_length = m_to_idx(ramp_length)
    gap_length = 0.1 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_rotating_beam(start_x, length, mid_y):
        half_width = beam_width // 2
        x1, x2 = start_x, start_x + length
        y1, y2 = mid_y - half_width, mid_y + half_width
        beam_height = (platform_height_min + platform_height_max) / 2  # Fixed height for rotating beam
        height_field[x1:x2, y1:y2] = beam_height

    def add_ramp(start_x, length, mid_y, direction):
        half_width = platform_width // 2
        x1, x2 = start_x, start_x + length
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        slant = np.linspace(0, ramp_height, num=y2-y1)[::direction]
        slant = slant[None, :]  # Broadcasting to x
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.0, 0.3  # Polarity for alternating
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)
    
    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(4):  # Setting up the course with various obstacles
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        if i % 2 == 0: 
            # Add a moving platform
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        else:
            # Add a rotating beam
            add_rotating_beam(cur_x, beam_length, mid_y + dy)
            goals[i+1] = [cur_x + (beam_length) / 2, mid_y + dy]
        
        # Add gap
        cur_x += platform_length + dx + gap_length

    for i in range(4, 6):  # Adding inclined ramps for the last section
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        direction = (-1) ** i  # Alternating left and right ramps
        dy = dy * direction

        add_ramp(cur_x, ramp_length + dx, mid_y + dy, direction)
        goals[i+1] = [cur_x + (ramp_length + dx) / 2, mid_y + dy]
        cur_x += ramp_length + dx + gap_length
        
    # Add final goal behind the last obstacle, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_27(length, width, field_resolution, difficulty):
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

def set_terrain_28(length, width, field_resolution, difficulty):
    """Challenging terrain with alternating narrow beams, platforms, and tilted ramps to enhance balance and jumping skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        if isinstance(m, (list, tuple)):
            return [round(i / field_resolution) for i in m]
        return np.round(m / field_resolution).astype(np.int16)

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Adjust parameters based on difficulty
    platform_length = 1.6 - 0.5 * difficulty
    platform_length_idx = m_to_idx(platform_length)
    platform_width_min, platform_width_max = 0.9, 1.2
    platform_width_idx = m_to_idx(np.random.uniform(platform_width_min, platform_width_max))
    
    beam_width = 0.4  # Fixed narrow beam width
    beam_length = 1.0 + 1.0 * difficulty
    beam_length_idx = m_to_idx(beam_length)
    beam_width_idx = m_to_idx(beam_width)
    
    ramp_height_min, ramp_height_max = 0.3 * difficulty, 0.6 * difficulty
    gap_length = 0.4 + 0.6 * difficulty
    gap_length_idx = m_to_idx(gap_length)

    mid_y = m_to_idx(width / 2)

    def add_narrow_beam(start_x, mid_y):
        """Adds a narrow beam obstacle."""
        half_width_idx = beam_width_idx // 2
        x1, x2 = start_x, start_x + beam_length_idx
        y1, y2 = mid_y - half_width_idx, mid_y + half_width_idx
        beam_height = np.random.uniform(ramp_height_min, ramp_height_max)
        height_field[x1:x2, y1:y2] = beam_height
        return (x1 + x2) // 2, mid_y

    def add_platform(start_x, mid_y):
        """Adds a platform obstacle."""
        half_width_idx = platform_width_idx // 2
        x1, x2 = start_x, start_x + platform_length_idx
        y1, y2 = mid_y - half_width_idx, mid_y + half_width_idx
        platform_height = np.random.uniform(ramp_height_min, ramp_height_max)
        height_field[x1:x2, y1:y2] = platform_height
        return (x1 + x2) // 2, mid_y

    def add_ramp(start_x, mid_y, direction):
        """Adds a tilted ramp obstacle."""
        half_width_idx = platform_width_idx // 2
        x1, x2 = start_x, start_x + platform_length_idx
        y1, y2 = mid_y - half_width_idx, mid_y + half_width_idx
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        slant = np.linspace(0, ramp_height, num=y2-y1)[::direction]
        slant = slant[None, :]  # Add a dimension for broadcasting to x
        height_field[x1:x2, y1:y2] = slant
        return (x1 + x2) // 2, mid_y

    # Set spawn area to flat ground
    spawn_length_idx = m_to_idx(2)
    height_field[:spawn_length_idx, :] = 0
    goals[0] = [spawn_length_idx - m_to_idx(0.5), mid_y]

    # Initiate current x and step length
    cur_x = spawn_length_idx
  
    for i in range(6):  # Set up 6 challenging obstacles
        dx = np.random.randint(-m_to_idx(0.1), m_to_idx(0.1))
        if i % 3 == 0:
            # Add narrow beams
            cx, cy = add_narrow_beam(cur_x, mid_y)
        elif i % 3 == 1:
            # Add platforms
            cx, cy = add_platform(cur_x, mid_y)
        else:
            # Add tilted ramps
            dy = np.random.randint(-m_to_idx(0.2), m_to_idx(0.2))
            direction = (-1) ** i  # Alternate left and right ramps
            cx, cy = add_ramp(cur_x, mid_y + dy, direction)
            
        goals[i + 1] = [cx, cy]
        
        # Move to the next position accounting for obstacle length and gap
        if i % 3 == 2:
            cur_x = cx + gap_length_idx  # Increase gap after ramp
      
    # Add final goal after last obstacle
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_29(length, width, field_resolution, difficulty):
    '''Stepping stones across uneven terrain for the quadruped to step or jump over.'''

    def m_to_idx(m):
        '''Converts meters to quantized indices.'''
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    stone_length = 0.5 + 0.2 * difficulty
    stone_length = m_to_idx(stone_length)
    stone_width = 0.5 + 0.2 * difficulty
    stone_width = m_to_idx(stone_width)
    stone_height_min, stone_height_max = 0.1 + 0.2 * difficulty, 0.2 + 0.5 * difficulty
    gap_length = 0.5 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_stone(center_x, center_y, height):
        half_length = stone_length // 2
        half_width = stone_width // 2
        x1, x2 = center_x - half_length, center_x + half_length
        y1, y2 = center_y - half_width, center_y + half_width
        height_field[x1:x2, y1:y2] = height

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
    for i in range(7):  # Set up 7 stepping stones
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        stone_height = np.random.uniform(stone_height_min, stone_height_max)
        add_stone(cur_x + dx, mid_y + dy, stone_height)

        # Put goal in the center of the stone
        goals[i+1] = [cur_x + dx, mid_y + dy]

        # Add gap
        cur_x += stone_length + gap_length

    return height_field, goals

def set_terrain_30(length, width, field_resolution, difficulty):
    """Zigzag beams for the robot to balance on and navigate around obstacles."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up beam dimensions
    beam_length = 1.4 - 0.5 * difficulty  # Beam length decreases with difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = 0.35 + 0.1 * difficulty  # Increased width to balance challenge
    beam_width = m_to_idx(beam_width)
    beam_height_min, beam_height_max = 0.2 + 0.2 * difficulty, 0.4 + 0.2 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, mid_y, height, angle=0):
        half_width = beam_width // 2
        end_x = start_x + beam_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        if angle != 0:
            # Define angled beam by using height to form incline/decline
            for x in range(start_x, end_x):
                offset = int((x - start_x) * np.tan(angle))
                height_field[x, mid_y - half_width + offset: mid_y + half_width + offset] = height
        else:
            height_field[start_x:end_x, y1:y2] = height

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
    for i in range(6):  # Set up 6 beams
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        angle = (-1 if i % 2 == 0 else 1) * np.radians(10 + difficulty * 10)  # Alternating angles for zigzag
        beam_height = np.random.uniform(beam_height_min, beam_height_max)
        add_beam(cur_x, mid_y + dy, beam_height, angle)
        
        # Put goal in the center of each beam
        goals[i+1] = [cur_x + beam_length / 2 + dx, mid_y + dy]

        # Add gap of 0.4 meter between each beam to require maneuvering
        gap_length = m_to_idx(0.4)
        cur_x += beam_length + gap_length + dx
    
    # Add final goal in the center of the last beam, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    # Ensure the last section is on flat ground
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_31(length, width, field_resolution, difficulty):
    """Staggered elevated steps and bridges for the robot to climb, navigate and balance across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up staggered step and elevated bridge dimensions
    # We make the step height near 0 at minimum difficulty so the quadruped can learn to climb up
    step_length = 0.8 - 0.2 * difficulty
    step_length = m_to_idx(step_length)
    step_width = np.random.uniform(0.4, 0.6)
    step_width = m_to_idx(step_width)
    step_height_min, step_height_max = 0.1 * difficulty, 0.3 * difficulty
    
    bridge_length = 1.0 - 0.3 * difficulty
    bridge_length = m_to_idx(bridge_length)
    bridge_width = np.random.uniform(0.5, 0.8)
    bridge_width = m_to_idx(bridge_width)
    bridge_height_min, bridge_height_max = 0.2 * difficulty, 0.5 * difficulty

    gap_length = 0.2 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_step(start_x, end_x, mid_y, height):
        half_width = step_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_bridge(start_x, end_x, mid_y, height):
        half_width = bridge_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height
    
    dx_min, dx_max = -0.05, 0.05
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.1, 0.1
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn area
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]
    
    cur_x = spawn_length
    for i in range(3):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        step_height = np.random.uniform(step_height_min, step_height_max)
        add_step(cur_x, cur_x + step_length + dx, mid_y + dy, step_height)

        # Put goal in the center of the step
        goals[i+1] = [cur_x + (step_length + dx) / 2, mid_y + dy]

        cur_x += step_length + dx + gap_length

    for i in range(3, 7):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        bridge_height = np.random.uniform(bridge_height_min, bridge_height_max)
        add_bridge(cur_x, cur_x + bridge_length + dx, mid_y + dy, bridge_height)

        # Put goal in the center of the bridge
        goals[i+1] = [cur_x + (bridge_length + dx) / 2, mid_y + dy]

        cur_x += bridge_length + dx + gap_length
    
    # Add final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_32(length, width, field_resolution, difficulty):
    """Varying-height platforms and shallow inclines for balancing and moderate climbing."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length = 1.0 - 0.1 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 0.8
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.1 * difficulty, 0.15 + 0.2 * difficulty
    incline_length = 0.5 + 0.2 * difficulty
    incline_length = m_to_idx(incline_length)
    gap_length = 0.3 + 0.4 * difficulty  # Adjust gap length for difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_incline(start_x, end_x, mid_y, height, direction):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        incline = np.linspace(0, height, num=x2-x1)[::direction]
        incline = incline[:, None]  # Add a dimension for broadcasting to y
        height_field[x1:x2, y1:y2] = incline

    dx_range = m_to_idx([0.0, 0.2])
    dy_range = m_to_idx([0.0, 0.4])
    dy_offset_direction = (-1) ** np.arange(6)  # Alternate slope directions

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    for i in range(5):  # Set up 5 platforms and inclines
        dx = np.random.randint(*dx_range)
        dy = np.random.randint(*dy_range) * dy_offset_direction[i]

        if i % 2 == 0:
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        else:
            height = np.random.uniform(platform_height_min, platform_height_max)
            add_incline(cur_x, cur_x + incline_length + dx, mid_y + dy, height, (-1) ** i)
            goals[i+1] = [cur_x + (incline_length + dx) / 2, mid_y + dy]

        cur_x += platform_length + incline_length + dx + gap_length if i % 2 != 0 else platform_length + dx + gap_length

    # Add final goal behind the last platform/incline, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_33(length, width, field_resolution, difficulty):
    """Complex elevated and uneven terrain for enhanced difficulty, testing the robot's balance and climbing abilities."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define the size parameters based on difficulty
    min_platform_width = 0.6 + 0.1 * difficulty
    max_platform_width = 1.2 - 0.1 * difficulty
    min_height = 0.1 * difficulty
    max_height = 0.5 * difficulty
    min_gap = 0.2
    max_gap = 0.8 + 0.2 * difficulty

    mid_y = m_to_idx(width / 2)

    def add_platform_or_slope(start_x, end_x, mid_y, platform_width, height, incline=False):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        if incline:
            slope = np.linspace(0, height, num=x2-x1)[:, None]
            height_field[x1:x2, y1:y2] = np.broadcast_to(slope, (x2-x1, y2-y1))
        else:
            height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    for i in range(6):  # Set up 6 obstacles
        platform_width = np.random.uniform(min_platform_width, max_platform_width)
        platform_width = m_to_idx(platform_width)
        platform_length = 1.0 + 0.4 * difficulty
        platform_length = m_to_idx(platform_length)
        platform_height = np.random.uniform(min_height, max_height)

        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        # Randomly decide if the obstacle is an inclined ramp or flat platform
        incline = np.random.rand() > 0.5

        add_platform_or_slope(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_width, platform_height, incline)

        # Place a goal at each obstacle
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Create a gap between platforms
        gap_length = np.random.uniform(min_gap, max_gap) * difficulty + 0.2
        gap_length = m_to_idx(gap_length)

        cur_x += platform_length + dx + gap_length

    # Add final goal behind the last platform, filling in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_34(length, width, field_resolution, difficulty):
    """Raised platforms with varying heights and narrow passages to test robot's agility and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and passage dimensions
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.2 - 0.1 * difficulty)  # Slightly reduce width
    platform_width = m_to_idx(platform_width)
    
    gap_length_min = 0.2
    gap_length_max = 0.8
    gap_length_min = m_to_idx(gap_length_min)
    gap_length_max = m_to_idx(gap_length_max)
    
    platform_height_min = 0.2 * difficulty
    platform_height_max = 0.4 + 0.2 * difficulty
    
    mid_y = m_to_idx(width) // 2
    
    def add_platform(x_start, x_end, y_center, height):
        half_width = platform_width // 2
        y1, y2 = y_center - half_width, y_center + half_width
        height_field[x_start:x_end, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]
    
    cur_x = spawn_length
    for i in range(7):  # Set up 6 platforms
        height = np.random.uniform(platform_height_min, platform_height_max)
        gap_length = np.random.randint(gap_length_min, gap_length_max)
        
        add_platform(cur_x, cur_x + platform_length, mid_y, height)
        goals[i+1] = [cur_x + platform_length // 2, mid_y]
        
        cur_x += platform_length + gap_length
        
        if i % 2 == 0 and i != 6:
            # Add a narrow passageway after 2 platforms
            passage_width = m_to_idx(0.35 + 0.15 * (1 - difficulty))
            passage_start = m_to_idx(0.2 + 0.3 * difficulty)
            passage_height = np.random.uniform(0.1, 0.2) * (difficulty + 1)
            height_field[cur_x:cur_x + passage_start, (mid_y - passage_width // 2):(mid_y + passage_width // 2)] = passage_height
            
            goals[i+1][0] += passage_start // 2
            cur_x += passage_start
    
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0
    
    return height_field, goals

def set_terrain_35(length, width, field_resolution, difficulty):
    """Courses that combine narrow steps, long gaps, and complex slopes to test climbing, jumping, and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 1.0
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.2 + 0.25 * difficulty, 0.3 + 0.35 * difficulty
    gap_length = 0.4 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)
    slope_length = 1.0 + 0.5 * difficulty
    slope_length = m_to_idx(slope_length)

    mid_y = m_to_idx(width) // 2    

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_slope(start_x, mid_y, length, height, direction=1):
        half_width = platform_width // 2
        x1, x2 = start_x, start_x + length
        y1, y2 = mid_y - half_width, mid_y + half_width
        slope = np.linspace(0, height, x2 - x1)[::direction]
        slope = slope[:, None]
        height_field[x1:x2, y1:y2] += slope

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    # Sequence of Platforms
    for i in range(3):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        height = np.random.uniform(platform_height_min, platform_height_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, height)
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length
    
    # Slopes
    for i in range(3, 7):
        height = np.random.uniform(platform_height_min, platform_height_max)
        direction = np.random.choice([-1, 1])
        add_slope(cur_x, mid_y, slope_length, height, direction)
        goals[i+1] = [cur_x + slope_length // 2, mid_y]
        cur_x += slope_length + gap_length

    # Ending platform
    add_platform(cur_x, cur_x + platform_length, mid_y, 0)
    goals[-1] = [cur_x + platform_length / 2, mid_y]

    return height_field, goals

def set_terrain_36(length, width, field_resolution, difficulty):
    """Series of staggered narrow beams with height variations for the quadruped to balance and navigate through."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    # Initialize height field and goals
    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Beam dimensions and setup
    beam_width = 0.2 + 0.1 * difficulty
    beam_width = m_to_idx(beam_width)
    beam_length = 1.0 + 0.2 * difficulty
    beam_length = m_to_idx(beam_length)
    beam_height_min, beam_height_max = 0.1 + 0.1 * difficulty, 0.2 + 0.4 * difficulty
    gap_length = 0.4 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, center_y, height):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = center_y - half_width, center_y + half_width
        height_field[x1:x2, y1:y2] = height

    # Flatten the spawn area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(6):  # Create a sequence of beams with gaps
        dx = np.random.randint(-m_to_idx(0.1), m_to_idx(0.1))
        dy = np.random.randint(-m_to_idx(0.3), m_to_idx(0.3))
        beam_height = np.random.uniform(beam_height_min, beam_height_max)
        add_beam(cur_x, cur_x + beam_length + dx, mid_y + dy, beam_height)

        # Place goal in the middle of each beam
        goals[i + 1] = [cur_x + (beam_length + dx) / 2, mid_y + dy]

        # Increment current x by the length of the beam and the gap
        cur_x += beam_length + dx + gap_length

    # Place the final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_37(length, width, field_resolution, difficulty):
    """Obstacle course with staggered platforms, ramps, and gaps requiring the quadruped to balance, climb, and jump effectively."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length = m_to_idx(1.0 - 0.2 * difficulty)
    platform_width = m_to_idx(np.random.uniform(0.8, 1.2))
    platform_height_min, platform_height_max = 0.1 * difficulty, 0.3 * difficulty
    ramp_length = m_to_idx(0.5)  # keeping ramps shorter
    ramp_height_min, ramp_height_max = 0.2, 0.4 + 0.3 * difficulty
    gap_length = m_to_idx(0.3 + 0.5 * difficulty)  # Increase gap length

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

    for i in range(4):  # Create 4 main sections: 2 platforms and 2 ramps
        height = np.random.uniform(platform_height_min, platform_height_max)
        if i % 2 == 0:  # Add platforms on even iterations
            add_platform(cur_x, cur_x + platform_length, mid_y, height)
            goals[i + 1] = [cur_x + platform_length // 2, mid_y]
            cur_x += platform_length + gap_length
        else:  # Add ramps on odd iterations
            ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
            direction = 1 if i % 4 == 1 else -1
            add_ramp(cur_x, cur_x + ramp_length, mid_y, ramp_height, direction)
            goals[i + 1] = [cur_x + ramp_length // 2, mid_y]
            cur_x += ramp_length + gap_length

    final_height = np.random.uniform(platform_height_min, platform_height_max)
    add_platform(cur_x, cur_x + platform_length, mid_y, final_height)
    goals[5] = [cur_x + platform_length // 2, mid_y]
    cur_x += platform_length

    for i in range(2):  # add some simple stepping obstacles
        height = np.random.uniform(platform_height_min, platform_height_max)
        dx = m_to_idx(0.3 * (i + 1))
        dy = m_to_idx(0.5 * (i + 1))
        add_platform(cur_x + dx, cur_x + dx + platform_length, mid_y + dy, height)
        goals[6 + i] = [cur_x + dx + platform_length // 2, mid_y + dy]
        cur_x += platform_length + gap_length

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0.0

    return height_field, goals

def set_terrain_38(length, width, field_resolution, difficulty):
    """Combination of side ramps, platforms, and narrow beams to test precision, balance, and agility."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    mid_y = m_to_idx(width) // 2
    
    # General obstacle dimensions
    platform_length = m_to_idx(1.2 - 0.3 * difficulty)
    platform_width = m_to_idx(np.random.uniform(1.0, 1.5))
    platform_height_min = 0.1 + 0.2 * difficulty
    platform_height_max = 0.2 + 0.3 * difficulty

    ramp_slope = np.linspace(0, m_to_idx(0.4 + 0.4 * difficulty), platform_width)
    beam_width = m_to_idx(0.4)
    beam_length = m_to_idx(1.5)
    gap_length = m_to_idx(0.1 + 0.5 * difficulty)

    def add_platform(start_x, end_x, y, height):
        """Add a rectangular platform."""
        half_width = platform_width // 2
        height_field[start_x:end_x, y - half_width:y + half_width] = height

    def add_ramp(start_x, mid_y, direction=1):
        """Add a ramp oriented as specified by direction (1 indicates upwards, -1 indicates downwards)."""
        half_width = platform_width // 2
        ramp_height = np.random.uniform(platform_height_min, platform_height_max)
        ramp = np.outer(np.linspace(0, direction * ramp_height, platform_length), np.ones(2 * half_width))
        height_field[start_x:start_x + platform_length, mid_y - half_width:mid_y + half_width] = ramp

    def add_beam(start_x, end_x, y, height):
        """Add a narrow beam."""
        half_width = beam_width // 2
        height_field[start_x:end_x, y - half_width:y + half_width] = height

    # Initialize flat spawn area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]
    
    cur_x = spawn_length

    for i in range(3):
        # Alternating between platforms and ramps
        if i % 2 == 0:
            platform_height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)
            goals[i + 1] = [cur_x + platform_length // 2, mid_y]
        else:
            direction = (-1)**i  # Alternate ramp direction (upwards/downwards)
            add_ramp(cur_x, mid_y, direction)
            goals[i + 1] = [cur_x + platform_length // 2, mid_y]
        
        cur_x += platform_length + gap_length
    
    # Add beams in between ramps
    for j in range(3, 5):
        add_beam(cur_x, cur_x + beam_length, mid_y, 0)
        goals[j + 1] = [cur_x + beam_length // 2, mid_y]
        cur_x += beam_length + gap_length

    # Add final platform leading to the last goal
    final_platform_height = np.random.uniform(platform_height_min, platform_height_max)
    add_platform(cur_x, cur_x + platform_length, mid_y, final_platform_height)
    goals[-1] = [cur_x + platform_length // 2, mid_y]

    return height_field, goals

def set_terrain_39(length, width, field_resolution, difficulty):
    """Obstacle course with slalom ladders and varying height barriers for the robot to navigate through."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    slalom_gap = 0.8 - 0.3 * difficulty  # Slalom gap decreases with difficulty
    slalom_gap = m_to_idx(slalom_gap)
    barrier_height = 0.05 + 0.25 * difficulty  # Barrier height increases with difficulty
    barrier_width = 1.0 + 0.5 * difficulty  # Barrier width increases slightly with difficulty
    barrier_width = m_to_idx(barrier_width)
    slalom_y_positions = [m_to_idx(1.0) + m_to_idx(2.0) * i for i in range(4)]  # Positioning slalom barriers

    def add_slalom_barrier(start_x, width, height, y_positions):
        for y in y_positions:
            height_field[start_x:start_x+width, y:y + m_to_idx(0.4)] = height

    dx_min, dx_max = 2.0, 3.0
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)

    # Initial flat ground for spawning
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    mid_y = m_to_idx(width) // 2
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(4):  # Set up 4 slalom sections
        add_slalom_barrier(cur_x, barrier_width, barrier_height, slalom_y_positions)

        # Place goals to navigate the slaloms
        goals[i+1] = [cur_x + m_to_idx(0.5), mid_y - m_to_idx(1.5) * ((i+1) % 2)]
        
        # Add a clear pathway between the slalom sections
        cur_x += barrier_width + slalom_gap

    # Add final goal at the end of the course
    goals[-1] = [cur_x + m_to_idx(1.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

# INSERT TERRAIN FUNCTION DEFINITIONS HERE
