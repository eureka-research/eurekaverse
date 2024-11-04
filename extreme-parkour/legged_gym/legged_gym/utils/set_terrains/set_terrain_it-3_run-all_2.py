
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

def set_terrain_1(length, width, field_resolution, difficulty):
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

def set_terrain_2(length, width, field_resolution, difficulty):
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

def set_terrain_3(length, width, field_resolution, difficulty):
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

def set_terrain_4(length, width, field_resolution, difficulty):
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

def set_terrain_5(length, width, field_resolution, difficulty):
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

def set_terrain_6(length, width, field_resolution, difficulty):
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

def set_terrain_7(length, width, field_resolution, difficulty):
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

def set_terrain_8(length, width, field_resolution, difficulty):
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

def set_terrain_9(length, width, field_resolution, difficulty):
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

def set_terrain_10(length, width, field_resolution, difficulty):
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

def set_terrain_11(length, width, field_resolution, difficulty):
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

def set_terrain_12(length, width, field_resolution, difficulty):
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

def set_terrain_13(length, width, field_resolution, difficulty):
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

def set_terrain_14(length, width, field_resolution, difficulty):
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

def set_terrain_15(length, width, field_resolution, difficulty):
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

def set_terrain_16(length, width, field_resolution, difficulty):
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

def set_terrain_17(length, width, field_resolution, difficulty):
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

def set_terrain_18(length, width, field_resolution, difficulty):
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

def set_terrain_19(length, width, field_resolution, difficulty):
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

def set_terrain_20(length, width, field_resolution, difficulty):
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

def set_terrain_21(length, width, field_resolution, difficulty):
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

def set_terrain_22(length, width, field_resolution, difficulty):
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

def set_terrain_23(length, width, field_resolution, difficulty):
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

def set_terrain_24(length, width, field_resolution, difficulty):
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

def set_terrain_25(length, width, field_resolution, difficulty):
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

def set_terrain_26(length, width, field_resolution, difficulty):
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


def set_terrain_27(length, width, field_resolution, difficulty):
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

def set_terrain_28(length, width, field_resolution, difficulty):
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

def set_terrain_29(length, width, field_resolution, difficulty):
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

def set_terrain_30(length, width, field_resolution, difficulty):
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


def set_terrain_31(length, width, field_resolution, difficulty):
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

def set_terrain_32(length, width, field_resolution, difficulty):
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

def set_terrain_33(length, width, field_resolution, difficulty):
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

def set_terrain_34(length, width, field_resolution, difficulty):
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

def set_terrain_35(length, width, field_resolution, difficulty):
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

def set_terrain_36(length, width, field_resolution, difficulty):
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

def set_terrain_37(length, width, field_resolution, difficulty):
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

def set_terrain_38(length, width, field_resolution, difficulty):
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

def set_terrain_39(length, width, field_resolution, difficulty):
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

# INSERT TERRAIN FUNCTION DEFINITIONS HERE
