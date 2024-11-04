
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

def set_terrain_1(length, width, field_resolution, difficulty):
    """Narrow beams, varying width platforms, and slopes to test balance, precision, and incline traversal."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define the size parameters based on difficulty
    min_beam_width = 0.4 + 0.1 * difficulty
    max_beam_width = 1.0 - 0.2 * difficulty
    min_platform_width = 1.0 + 0.2 * difficulty
    max_platform_width = 2.0 - 0.2 * difficulty
    min_height = 0.1 * difficulty
    max_height = 0.5 * difficulty
    gap_min = 0.2
    gap_max = 1.0

    mid_y = m_to_idx(width / 2)

    def add_beam_or_platform(start_x, end_x, mid_y, platform_width, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
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
        # Determine if this is a beam, wide platform, or inclined ramp
        if i % 2 == 0:  # Use beams for even indices
            platform_width = np.random.uniform(min_beam_width, max_beam_width)
        else:  # Use wide platforms for odd indices
            platform_width = np.random.uniform(min_platform_width, max_platform_width)

        platform_length = 1.0 + 0.4 * difficulty
        platform_length = m_to_idx(platform_length)
        platform_height = np.random.uniform(min_height, max_height)
        
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        add_beam_or_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, m_to_idx(platform_width), platform_height)

        # Place a goal at each obstacle
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Create a gap between platforms
        gap_length = np.random.uniform(gap_min, gap_max) * difficulty + 0.1
        gap_length = m_to_idx(gap_length)

        cur_x += platform_length + dx + gap_length

    # Add final goal behind the last platform, filling in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_2(length, width, field_resolution, difficulty):
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

def set_terrain_3(length, width, field_resolution, difficulty):
    """Alternating high steps and low platforms for the robot to jump across and climb."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set dimensions for high steps and low platforms
    high_step_height_min, high_step_height_max = 0.15 + 0.1 * difficulty, 0.25 + 0.2 * difficulty
    low_platform_height_min, low_platform_height_max = 0.0, 0.1 * difficulty
    step_length, platform_length = 0.8 + 0.2 * difficulty, 1.2 - 0.2 * difficulty
    step_length, platform_length = m_to_idx(step_length), m_to_idx(platform_length)
    gap_length = 0.2 + 0.2 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_step(start_x, height):
        x1, x2 = start_x, start_x + step_length
        y1, y2 = mid_y - m_to_idx(0.64), mid_y + m_to_idx(0.64)  # Width set to 1.28 meters
        height_field[x1:x2, y1:y2] = height

    def add_platform(start_x, height):
        x1, x2 = start_x, start_x + platform_length
        y1, y2 = mid_y - m_to_idx(1.0), mid_y + m_to_idx(1.0)  # Width set to 2 meters
        height_field[x1:x2, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0.0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    for i in range(3):  # Create 3 high steps
        high_step_height = np.random.uniform(high_step_height_min, high_step_height_max)
        low_platform_height = np.random.uniform(low_platform_height_min, low_platform_height_max)
        
        # Add alternating high step and low platform
        add_step(cur_x, high_step_height)
        goals[2 * i + 1] = [cur_x + step_length // 2, mid_y]
        cur_x += step_length + gap_length
        
        add_platform(cur_x, low_platform_height)
        goals[2 * i + 2] = [cur_x + platform_length // 2, mid_y]
        cur_x += platform_length + gap_length

    # Final low platform with goal
    add_platform(cur_x, low_platform_height_min)
    goals[7] = [cur_x + platform_length // 2, mid_y]

    return height_field, goals

def set_terrain_4(length, width, field_resolution, difficulty):
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

def set_terrain_5(length, width, field_resolution, difficulty):
    """Serpentine pathways with varying heights and narrow bridges to test the robot's turning and balance abilities."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Setup parameters for serpentine pathways and bridges
    pathway_width = 0.4 + 0.6 * (1 - difficulty)
    pathway_width = m_to_idx(pathway_width)
    pathway_height_min, pathway_height_max = 0.1 * difficulty, 0.4 * difficulty
    bridge_length = 1.0 - 0.7 * difficulty
    bridge_length = m_to_idx(bridge_length)
    bridge_height_min, bridge_height_max = 0.2 * difficulty, 0.5 * difficulty

    y_center = m_to_idx(width / 2)
    serpentine_amplitude = m_to_idx(0.5 + 1.5 * difficulty)
    serpentine_frequency = 3 + 5 * difficulty

    def add_pathway_pattern(start_x, end_x, y_center, serpentine_amplitude, serpentine_frequency):
        half_width = pathway_width // 2
        for x in range(start_x, end_x):
            offset = int(serpentine_amplitude * np.sin(serpentine_frequency * 2 * np.pi * (x - start_x) / (end_x - start_x)))
            y1, y2 = y_center + offset - half_width, y_center + offset + half_width
            pathway_height = np.random.uniform(pathway_height_min, pathway_height_max)
            height_field[x, y1:y2] = pathway_height

    def add_bridge(start_x, start_y, end_x, end_y):
        if start_x > end_x or start_y > end_y:
            return
        height_diff = np.random.uniform(bridge_height_min, bridge_height_max)
        bridge_slope = np.linspace(0, height_diff, num=end_x - start_x)
        mid_y = (start_y + end_y) // 2
        for x in range(start_x, end_x):
            height_field[x, mid_y-2:mid_y+2] = bridge_slope[x-start_x]

    dx_min, dx_max = m_to_idx(-0.05), m_to_idx(0.05)
    dy_min, dy_max = m_to_idx(-0.2), m_to_idx(0.2)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), y_center]

    # Add serpentine pathways
    cur_x = spawn_length
    section_length = m_to_idx(2)
    for i in range(4):  # Four primary sections
        next_x = cur_x + section_length
        dy = np.random.randint(dy_min, dy_max)
        add_pathway_pattern(cur_x, next_x, y_center + dy, serpentine_amplitude, serpentine_frequency)
        goals[i+1] = [cur_x + section_length // 2, y_center + dy]
        cur_x = next_x + m_to_idx(0.1)

    # Add narrow bridges connecting pathways
    for i in range(4, 7):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_bridge(cur_x, y_center + dy, cur_x + bridge_length, y_center + dy)
        goals[i+1] = [cur_x + bridge_length // 2, y_center + dy]
        cur_x += bridge_length + m_to_idx(0.1)

    # Add final goal behind the last section of serpentine pathway or bridge
    goals[-1] = [cur_x + m_to_idx(0.5), y_center]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_6(length, width, field_resolution, difficulty):
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

def set_terrain_7(length, width, field_resolution, difficulty):
    """Staggered platforms with large gaps and varying heights to test the robot's jumping and climbing abilities."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform and gap dimensions
    platform_length = 1.5 - 0.4 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.4)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.3 * difficulty, 0.2 + 0.5 * difficulty
    gap_length = 0.2 + 0.8 * difficulty
    gap_length = m_to_idx(gap_length)
    
    # Central y-coordinate for obstacles
    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y_offset):
        """Adds a platform at specified x and y coordinates."""
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y + mid_y_offset - half_width, mid_y + mid_y_offset + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    for i in range(6):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + platform_length + dx, dy)
        
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        
        # Add a gap
        cur_x += platform_length + dx + gap_length

    # Final platform and goal
    add_platform(cur_x, cur_x + m_to_idx(1.0), 0)
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_8(length, width, field_resolution, difficulty):
    """Alternate moving platforms and stepping stones across a pit for the robot to jump and balance"""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up moving platform and stepping stone dimensions
    platform_length = 0.8 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 0.8 + 0.3 * difficulty  # Decrease width for harder steps
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.3 + 0.25 * difficulty
    gap_length = 0.5 + 0.4 * difficulty  # Increase gap length with difficulty
    gap_length = m_to_idx(gap_length)

    stepping_stone_length = 0.4  # Small stepping stones
    stepping_stone_length = m_to_idx(stepping_stone_length)
    stepping_stone_width = stepping_stone_length
    stepping_stone_height = 0.05 + 0.2 * difficulty  # Increase height with difficulty

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_stepping_stone(x, y):
        half_length = stepping_stone_length // 2
        half_width = stepping_stone_width // 2
        x1, x2 = x - half_length, x + half_length
        y1, y2 = y - half_width, y + half_width
        height_field[x1:x2, y1:y2] = stepping_stone_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at the end of the spawn area

    cur_x = spawn_length
    for i in range(3):  # Set up 3 moving platforms
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
        goals[i * 2 + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        cur_x += platform_length + dx + gap_length

        # Adding stepping stones in between
        for j in range(2):
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)
            stone_x = cur_x + j * stepping_stone_length * 2
            stone_y = mid_y + dy
            add_stepping_stone(stone_x, stone_y)
            goals[i * 2 + 2] = [stone_x, stone_y]

        cur_x += stepping_stone_length * 2

    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_9(length, width, field_resolution, difficulty):
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

# INSERT TERRAIN FUNCTION DEFINITIONS HERE
