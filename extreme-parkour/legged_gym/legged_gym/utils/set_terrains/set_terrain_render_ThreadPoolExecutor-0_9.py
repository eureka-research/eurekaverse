
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
    """Series of narrow bridges with varying width and height for balancing skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    bridge_length = 1.5  # Each bridge is 1.5 meters long
    bridge_length_idx = m_to_idx(bridge_length)
    bridge_width_min = 0.4  # Minimum width of 0.4 meters 
    bridge_width_max = 1.0  # Maximum width of 1.0 meters
    initial_height = 0.2  # Initial height of first bridge

    # Spacing and increments based on difficulty
    gap_length = 0.2 + 0.5 * difficulty  # Gap between bridges
    gap_length_idx = m_to_idx(gap_length)
    height_increment = 0.05 + 0.15 * difficulty  # Height increment for each subsequent bridge

    current_x = m_to_idx(2)  # Start after the initial 2 meters
    mid_y = m_to_idx(width / 2)  # Midpoint in y direction

    def add_bridge(start_x):
        bridge_width = np.random.uniform(bridge_width_min, bridge_width_max)
        bridge_width_idx = m_to_idx(bridge_width)
        half_width = bridge_width_idx // 2
        bridge_height = initial_height + np.random.uniform(-height_increment, height_increment)
        x1, x2 = start_x, start_x + bridge_length_idx
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = bridge_height
        return bridge_height

    # Flat spawn area
    spawn_length_idx = m_to_idx(2)
    height_field[0:spawn_length_idx, :] = 0
    goals[0] = [spawn_length_idx - m_to_idx(0.5), mid_y]  # First goal at end of spawn area

    for i in range(6):  # Add 6 bridges
        add_bridge(current_x)
        goals[i+1] = [current_x + bridge_length_idx / 2, mid_y]  # Goal at the center of each bridge
        current_x += bridge_length_idx + gap_length_idx  # Move to the next start position

    # Final goal
    goals[-1] = [current_x + m_to_idx(0.5), mid_y]
    height_field[current_x:, :] = 0  # Flat area after the last bridge

    return height_field, goals

def set_terrain_1(length, width, field_resolution, difficulty):
    """Incline-stepped platforms forcing the quadruped to carefully navigate, climb, and descend to avoid stumbling or falling off."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and stair dimensions
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 1.2 - 0.2 * difficulty
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 * difficulty, 0.3 * difficulty
    stair_height_min, stair_height_max = 0.1 * difficulty, 0.4 * difficulty
    gap_length = 0.2 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_stairs(start_x, end_x, mid_y, direction, num_steps):
        step_length = (end_x - start_x) // num_steps
        step_height = np.linspace(stair_height_min, stair_height_max, num_steps + 1)
        half_width = platform_width // 2
        
        for step in range(num_steps):
            x1 = start_x + step * step_length
            x2 = x1 + step_length
            y1, y2 = mid_y - half_width, mid_y + half_width
            height_field[x1:x2, y1:y2] = step_height[step] + direction * (step / (num_steps + 1)) * step_height[step]

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.0, 0.4  # Polarity of dy will alternate instead of being random
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Set remaining area to be a pit
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    for i in range(7):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        # Alternate direction for stairs (-1 for down, 1 for up)
        direction = (-1) ** i
        
        # Add platform section before the stairs
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height)
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx

        # Add stairs
        num_steps = np.random.randint(3, 7)
        stair_length = m_to_idx(0.3) * num_steps
        add_stairs(cur_x, cur_x + stair_length + dx, mid_y + dy, direction, num_steps)
        cur_x += stair_length + dx + gap_length

    # Add final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_2(length, width, field_resolution, difficulty):
    """Staggered stepping stones and narrow pathways with varying heights."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Parameters for stepping stones and narrow pathways
    stone_length = np.random.uniform(0.6, 1.0)
    stone_length = m_to_idx(stone_length)
    stone_width = np.random.uniform(0.4, 0.7)
    stone_width = m_to_idx(stone_width)
    pathway_width = 0.25
    pathway_width = m_to_idx(pathway_width)
    height_variation = 0.3 * difficulty

    dx_min, dx_max = -0.2, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    mid_y = m_to_idx(width) // 2

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Set first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(7):  # Set up 7 stepping stones
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        stone_height = np.random.uniform(0.05, height_variation)
        
        x_start = cur_x
        x_end = cur_x + stone_length + dx
        y_start = mid_y + dy - stone_width // 2
        y_end = mid_y + dy + stone_width // 2

        height_field[x_start:x_end, y_start:y_end] = stone_height

        # Set goal in the center of the stone
        goals[i + 1] = [cur_x + (stone_length + dx) / 2, mid_y + dy]

        cur_x = x_end + m_to_idx(0.4)  # Move to the next position, adding some spacing

        # Add narrow, connecting pathways for increased difficulty
        if i < 6:
            path_dy = np.random.randint(-pathway_width // 2, pathway_width // 2)
            pathway_height = np.random.uniform(0.02, 0.07)
            
            x_start = cur_x
            x_end = cur_x + m_to_idx(0.25)
            y_start = mid_y + dy + path_dy - pathway_width // 2
            y_end = mid_y + dy + path_dy + pathway_width // 2
            
            height_field[x_start:x_end, y_start:y_end] = pathway_height
            
            cur_x = x_end  # Move to the end of the pathway

    # Set the last goal after the last stepping stone
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    return height_field, goals

def set_terrain_3(length, width, field_resolution, difficulty):
    """Interconnected elevated platforms with narrow beams for the quadruped to navigate with occasional jumps."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length = 1.0 - 0.2 * difficulty  # Slightly decreasing length for higher difficulty
    platform_width = 0.6  # Narrow platform length for higher difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.2 + 0.2 * difficulty, 0.4 + 0.4 * difficulty
    
    beam_length = 0.6  # Narrow beams between platforms
    beam_width = 0.15  # Fixed narrow beam width
    beam_length = m_to_idx(beam_length)
    beam_width = m_to_idx(beam_width)

    beam_height = 0.2 + 0.2 * difficulty  # Beam height scaling with difficulty
    
    gap_length = 0.1 + 0.3 * difficulty  # Maintaining smaller gaps for consistency
    gap_length = m_to_idx(gap_length)
    
    mid_y = m_to_idx(width) // 2

    def add_platform(x, y, height):
        x1, x2 = x, x + platform_length
        y1, y2 = y - platform_width // 2, y + platform_width // 2
        height_field[x1:x2, y1:y2] = height

    def add_beam(x, y, height):
        x1, x2 = x, x + beam_length
        y1, y2 = y - beam_width // 2, y + beam_width // 2
        height_field[x1:x2, y1:y2] = height
    
    cur_x = m_to_idx(2)  # Start after the safe spawn zone
    cur_y = mid_y

    goals[0] = [cur_x - m_to_idx(0.5), mid_y]  # First goal at the spawning area border

    for i in range(7):
        # Increment platform height for added difficulty
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        
        # Add elevated platform
        add_platform(cur_x, cur_y, platform_height)
        goals[i + 1] = [cur_x + platform_length // 2, cur_y]
        cur_x += platform_length + gap_length

        if i < 6:  # Add beams before the last goal/platform
            beam_height = np.random.uniform(beam_height, beam_height)
            add_beam(cur_x, cur_y, beam_height)
            cur_x += beam_length + gap_length

    # Add a final goal at the end after the last platform
    goals[7] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_4(length, width, field_resolution, difficulty):
    """Stepping stone platforms for the robot to precisely navigate across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define stepping stone dimensions and properties
    stone_length = 0.6 - 0.2 * difficulty  # Make stones smaller with increased difficulty
    stone_width = 0.6 - 0.2 * difficulty  # Ensure the robot has to be precise
    stone_length = m_to_idx(stone_length)
    stone_width = m_to_idx(stone_width)
    stone_height_min, stone_height_max = 0.1 + 0.2 * difficulty, 0.2 + 0.3 * difficulty
    gap_distance = 0.4 + 0.5 * difficulty  # Increase gaps with difficulty
    gap_distance = m_to_idx(gap_distance)

    mid_y = m_to_idx(width) // 2

    def add_stepping_stone(x, y):
        x1, x2 = x, x + stone_length
        y1, y2 = y - stone_width // 2, y + stone_width // 2
        stone_height = np.random.uniform(stone_height_min, stone_height_max)
        height_field[x1:x2, y1:y2] = stone_height

    # Initialize the spawning area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    
    # First goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(7):  # Create 7 stepping stones
        add_stepping_stone(cur_x, mid_y)
        
        # Set intermediate goals on each stepping stone
        goals[i+1] = [cur_x + stone_length // 2, mid_y]
        
        # Move to the next stone position, factoring in the gap
        cur_x += stone_length + gap_distance
    
    # Final goal position
    goals[7] = [cur_x - gap_distance + m_to_idx(0.3), mid_y]

    return height_field, goals

def set_terrain_5(length, width, field_resolution, difficulty):
    """Narrow elevated walkways with gaps and hurdles testing balance and precision stepping."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Walkway settings based on difficulty
    walkway_width_min = 0.4
    walkway_width_max = 1.0 - (0.5 * difficulty)
    walkway_height_min = 0.2 + (0.2 * difficulty)
    walkway_height_max = 0.4 + (0.4 * difficulty)
    gap_length_min = 0.2
    gap_length_max = 1.0
    hurdle_height_min = 0.05
    hurdle_height_max = 0.15 + (0.35 * difficulty)

    mid_y = m_to_idx(width) // 2

    def add_walkway(start_x, end_x, height, width):
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_hurdle(start_x, width, height):
        half_width = width // 2
        x1, x2 = start_x, start_x + m_to_idx(0.1)  # small hurdle thickness
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0  # flat spawn area with height 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # first goal at the end of spawn area

    cur_x = spawn_length
    
    for i in range(6):
        # Walkway dimensions
        walkway_length = np.random.uniform(1.0, 1.5)
        walkway_width = np.random.uniform(walkway_width_min, walkway_width_max)
        walkway_height = np.random.uniform(walkway_height_min, walkway_height_max)

        # Convert to indices
        walkway_length_idx = m_to_idx(walkway_length)
        walkway_width_idx = m_to_idx(walkway_width)

        # Add the walkway
        add_walkway(cur_x, cur_x + walkway_length_idx, walkway_height, walkway_width_idx)

        # Place goal in center of walkway
        goals[i + 1] = [cur_x + walkway_length_idx // 2, mid_y]

        # Add hurdles on the walkway
        num_hurdles = np.random.randint(1, 3)
        for _ in range(num_hurdles):
            hurdle_position = np.random.uniform(cur_x + m_to_idx(0.2), cur_x + walkway_length_idx - m_to_idx(0.2))
            hurdle_position_idx = m_to_idx(hurdle_position)
            hurdle_height = np.random.uniform(hurdle_height_min, hurdle_height_max)
            add_hurdle(hurdle_position_idx, walkway_width_idx, hurdle_height)

        # Move to the next section (gap)
        cur_x += walkway_length_idx
        gap_length = np.random.uniform(gap_length_min, gap_length_max)
        cur_x += m_to_idx(gap_length)

    # Final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    
    return height_field, goals

def set_terrain_6(length, width, field_resolution, difficulty):
    """Combination of inclined platforms, wider gaps and narrow paths to increase challenge and test agility and control."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length = 1.0 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.2)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.15 + 0.3 * difficulty
    gap_length = 0.2 + 0.6 * difficulty  # Increased gap length
    gap_length = m_to_idx(gap_length)
    incline_height = 0.05 + 0.15 * difficulty

    mid_y = m_to_idx(width // 2)

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_incline(start_x, end_x, mid_y, height_delta):
        slope = np.linspace(0, height_delta, num=end_x-start_x)
        for i, x in enumerate(range(start_x, end_x)):
            height_field[x, mid_y-m_to_idx(0.4):mid_y+m_to_idx(0.4)] = slope[i]

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(6):
        # Alternate between flat platforms and inclines
        if i % 2 == 0:
            platform_height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)
            cur_x += platform_length + gap_length
        else:
            height_delta = incline_height + incline_height * difficulty
            add_incline(cur_x, cur_x + platform_length, mid_y, height_delta)
            cur_x += platform_length + gap_length

        # Set intermediate goals
        goals[i + 1] = [cur_x - gap_length // 2, mid_y]

    goals[7] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0  # Set final area to flat ground

    return height_field, goals

def set_terrain_7(length, width, field_resolution, difficulty):
    """Course with small ramps, narrow platforms, and moderate gaps to balance maneuverability and foot placement skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and ramp dimensions
    platform_length = 1.0 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.2)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.05 + 0.1 * difficulty, 0.15 + 0.2 * difficulty
    ramp_height_min, ramp_height_max = 0.05 + 0.1 * difficulty, 0.15 + 0.2 * difficulty
    gap_length = 0.2 + 0.4 * difficulty
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

    dx_min, dx_max = -0.1, 0.1
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

    # Add first platform
    cur_x = spawn_length
    dx = np.random.randint(dx_min, dx_max)
    dy = np.random.randint(dy_min, dy_max)
    add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
    goals[1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
    cur_x += platform_length + dx + gap_length

    for i in range(1, 6):  # Set up 6 obstacles
        if i % 2 == 1:
            # Add ramp
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)
            direction = (-1) ** i  # Alternate left and right ramps
            dy = dy * direction  # Alternate positive and negative y offsets

            add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, direction)
        else:
            # Add platform
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)

        # Put goal in the center of the obstacle
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += platform_length + dx + gap_length
    
    # Add final goal behind the last obstacle, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_8(length, width, field_resolution, difficulty):
    """Narrow beams with elevation changes."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define beam parameters
    beam_width = 0.4
    beam_length = 1.5 - 0.5 * difficulty  # Beam length decreases with difficulty
    beam_height_min = 0.0
    beam_height_max = 0.2 + 0.3 * difficulty  # Beam height increases with difficulty

    beam_width = m_to_idx(beam_width)
    beam_length = m_to_idx(beam_length)

    # Pit with narrow beams setup
    gap_length = 0.1 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, mid_y, height):
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - beam_width // 2, mid_y + beam_width // 2
        height_field[x1:x2, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # First goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Create narrow beams leading across gaps
    cur_x = spawn_length
    for i in range(6):
        beam_height = np.random.uniform(beam_height_min, beam_height_max)
        add_beam(cur_x, cur_x + beam_length, mid_y, beam_height)

        # Set goal in the center of each beam
        goals[i+1] = [cur_x + beam_length // 2, mid_y]

        # Move to the start of the next beam after the gap
        cur_x += beam_length + gap_length

    # Add a final goal
    final_beam_length = m_to_idx(1.0)
    add_beam(cur_x, cur_x + final_beam_length, mid_y, np.random.uniform(beam_height_min, beam_height_max))
    goals[7] = [cur_x + final_beam_length // 2, mid_y]

    return height_field, goals

def set_terrain_9(length, width, field_resolution, difficulty):
    """Combination of varied height and width platforms, inclined ramps and jumping gaps for the quadruped's navigation and agility test."""

    def m_to_idx(m):
        """Convert meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Dimensions and parameters for obstacles
    platform_length = 1.2 - 0.3 * difficulty  # Slightly longer platforms
    platform_length_idx = m_to_idx(platform_length)
    platform_width = 0.9 + 0.3 * difficulty  # Slightly narrower platforms
    platform_width_idx = m_to_idx(platform_width)

    platform_height_min, platform_height_max = 0.0 + 0.3 * difficulty, 0.1 + 0.3 * difficulty  # Increased height range
    gap_length = 0.2 + 0.6 * difficulty  # Adjusted gap length
    gap_length_idx = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width_idx // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_ramp(start_x, end_x, mid_y, direction):
        half_width = platform_width_idx // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(platform_height_min, platform_height_max)
        slope = np.linspace(0, direction * ramp_height, x2 - x1)[:, np.newaxis]
        height_field[x1:x2, y1:y2] = slope

    dx_min, dx_max = m_to_idx(-0.2), m_to_idx(0.2)
    dy_min, dy_max = m_to_idx(-0.2), m_to_idx(0.2)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(7):  # Define 7 obstacles, keeping 1 final goal
        if i % 3 == 0:
            # Add a challenging inclined ramp
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)
            direction = (-1) ** (i // 3)  # Alternate directions for ramps
            add_ramp(cur_x, cur_x + platform_length_idx + dx, mid_y + dy, direction)
            goals[i + 1] = [cur_x + (platform_length_idx + dx) // 2, mid_y + dy]
        else:
            # Add a wide platform
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)
            add_platform(cur_x, cur_x + platform_length_idx + dx, mid_y + dy)
            goals[i + 1] = [cur_x + (platform_length_idx + dx) // 2, mid_y + dy]

        cur_x += platform_length_idx + dx + gap_length_idx

    # Set final goal and ensure flat ground finish
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

# INSERT TERRAIN FUNCTION DEFINITIONS HERE
