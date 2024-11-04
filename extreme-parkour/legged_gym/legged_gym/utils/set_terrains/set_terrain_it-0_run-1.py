
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

def set_terrain_1(length, width, field_resolution, difficulty):
    """Series of hills and mounds for the robot to climb up and down, testing balance and stability."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set the overall length and width of the hill segments
    hill_length = 1.5 + 1.0 * difficulty  # Length of a hill, increases with difficulty
    hill_length = m_to_idx(hill_length)

    space_between_hills = 0.1 * difficulty
    space_between_hills = m_to_idx(space_between_hills)

    hill_height_min = 0.1 + 0.1 * difficulty  # Minimum height of the hills
    hill_height_max = 0.25 + 0.5 * difficulty  # Maximum height of the hills

    mid_y = m_to_idx(width) // 2

    def add_hill(start_x, end_x, mid_y, height, slope):
        half_width = m_to_idx(1.5)  # ensuring around 1.5 meters width for hills
        y1, y2 = mid_y - half_width // 2, mid_y + half_width // 2

        # Create slope: linear increase from ground to peak height
        for x in range(start_x, end_x):
            current_height = height * ((x - start_x) / (end_x - start_x)) ** slope
            height_field[x, y1:y2] = current_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    
    # Place first goal near the spawn point
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(6):  # Plan a sequence consisting of 6 hills
        hill_height = np.random.uniform(hill_height_min, hill_height_max)
        slope = np.random.uniform(1, 2)  # Randomized slope between 1 (linear) and 2 (quadratic)
        add_hill(cur_x, cur_x + hill_length, mid_y, hill_height, slope)
        
        # Place goal near the peak of each hill
        goals[i+1] = [cur_x + hill_length // 2, mid_y]

        cur_x += hill_length + space_between_hills  # Move to the position for the next hill

    # Add final goal behind the last hill, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_2(length, width, field_resolution, difficulty):
    """Series of hurdles and narrow planks for the robot to jump over and balance on, testing its precision and agility."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Parameter settings based on difficulty
    hurdle_height_min = 0.1 + 0.2 * difficulty
    hurdle_height_max = 0.2 + 0.4 * difficulty
    hurdle_width = 1.0  # Width of the hurdles, fixed
    hurdle_length = 0.4  # Length of the hurdles, fixed
    hurdle_gap_min = 0.5 + 0.5 * difficulty
    hurdle_gap_max = 1.0 + 1.0 * difficulty

    plank_height = 0 + 0.05 * difficulty
    plank_width = 0.4  # Narrow planks to test balancing
    plank_length = 1.5
    plank_gap_min = 0.4
    plank_gap_max = 0.8

    # Spawn area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0  # Flat ground for spawning

    # Number of hurdles and planks
    num_hurdles = 3
    num_planks = 2

    cur_x = spawn_length
    mid_y = m_to_idx(width) // 2

    def add_hurdle(start_x, end_x, mid_y):
        height = np.random.uniform(hurdle_height_min, hurdle_height_max)
        y1 = mid_y - m_to_idx(hurdle_width) // 2
        y2 = mid_y + m_to_idx(hurdle_width) // 2
        height_field[start_x:end_x, y1:y2] = height

    def add_plank(start_x, end_x, mid_y):
        y1 = mid_y - m_to_idx(plank_width) // 2
        y2 = mid_y + m_to_idx(plank_width) // 2
        height_field[start_x:end_x, y1:y2] = plank_height

    # Hurdles
    for i in range(num_hurdles):
        hurdle_start = cur_x
        hurdle_end = cur_x + m_to_idx(hurdle_length)
        gap_length = m_to_idx(np.random.uniform(hurdle_gap_min, hurdle_gap_max))
        add_hurdle(hurdle_start, hurdle_end, mid_y)

        # Set goal after each hurdle
        goals[i] = [hurdle_end - m_to_idx(0.2), mid_y]

        cur_x = hurdle_end + gap_length

    # Planks
    for j in range(num_planks):
        plank_start = cur_x
        plank_end = cur_x + m_to_idx(plank_length)
        gap_length = m_to_idx(np.random.uniform(plank_gap_min, plank_gap_max))
        add_plank(plank_start, plank_end, mid_y)

        # Set goal at the end of each plank
        goals[num_hurdles + j] = [plank_end - m_to_idx(0.2), mid_y]

        cur_x = plank_end + gap_length

    # Final goal at the end of the terrain
    goals[-1] = [m_to_idx(length) - m_to_idx(0.5), mid_y]

    # Ensure final stretch to goal is flat
    final_stretch_length = m_to_idx(length) - cur_x
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_3(length, width, field_resolution, difficulty):
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

def set_terrain_4(length, width, field_resolution, difficulty):
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

def set_terrain_5(length, width, field_resolution, difficulty):
    """Stepping stones in a zigzag pattern to test the robot's balance and maneuvering skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set stepping stone dimensions
    stone_size = m_to_idx(random.uniform(0.4, 0.6))
    stone_height_min, stone_height_max = 0.05, 0.15 + 0.15 * difficulty
    
    mid_y = m_to_idx(width) // 2
    
    cur_x, cur_y = m_to_idx(2), mid_y  # Start after the spawn region
    spawn_region_length = m_to_idx(2)
    
    # Ensure the spawn area is flat
    height_field[:spawn_region_length, :] = 0

    def add_stepping_stone(x, y):
        """Add a stepping stone at a particular (x, y) position."""
        stone_height = np.random.uniform(stone_height_min, stone_height_max)
        half_size = stone_size // 2
        height_field[x - half_size:x + half_size, y - half_size:y + half_size] = stone_height

    # Place the stones in a zigzag pattern
    zigzag_length = m_to_idx(1.2)
    lateral_shift = m_to_idx(0.7)

    # Place first goal at the spawn location
    goals[0] = [cur_x - m_to_idx(0.5), cur_y]

    for i in range(1, 8):
        add_stepping_stone(cur_x, cur_y)
        goals[i] = [cur_x, cur_y]
        
        direction = -1 if i % 2 == 0 else 1
        cur_y += direction * lateral_shift
        cur_x += zigzag_length

    return height_field, goals

def set_terrain_6(length, width, field_resolution, difficulty):
    """Sloped terrain with alternating ascending and descending slopes for the robot to navigate."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up slope dimensions
    slope_length = 1.0  # 1 meter long slopes
    slope_length_idx = m_to_idx(slope_length)
    max_slope_height = 0.3 * difficulty  # maximum height difference is proportional to difficulty, up to 0.3 meters
    mid_y = m_to_idx(width) // 2

    def add_slope(start_x, slope_length_idx, height_start, height_end, mid_y):
        slope = np.linspace(height_start, height_end, slope_length_idx)
        for i in range(slope_length_idx):
            height_field[start_x + i, :] = slope[i]

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length, mid_y]  
    
    cur_x = spawn_length
    current_height = 0

    # Create alternating slopes
    for i in range(4):  # We will make 4 ascending and 4 descending slopes
        next_height = current_height + max_slope_height if i % 2 == 0 else current_height - max_slope_height
        add_slope(cur_x, slope_length_idx, current_height, next_height, mid_y)
        
        # Place goal at end of each slope
        goals[i*2 + 1] = [cur_x + slope_length_idx, mid_y]
        
        current_height = next_height
        cur_x += slope_length_idx
        
        # Add a short flat segment between consecutive slopes
        if i != 3:  # No flat segment after the last slope
            add_slope(cur_x, m_to_idx(0.2), current_height, current_height, mid_y)
            cur_x += m_to_idx(0.2)
    
    # Ensure the last segment is flat ground for the final goal
    if cur_x < height_field.shape[0]:
        height_field[cur_x:, :] = current_height
    goals[-1] = [height_field.shape[0] - m_to_idx(0.5), mid_y]

    return height_field, goals

def set_terrain_7(length, width, field_resolution, difficulty):
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

def set_terrain_8(length, width, field_resolution, difficulty):
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

def set_terrain_9(length, width, field_resolution, difficulty):
    """Staggered steps of varying heights for the robot to climb and traverse."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set the dimensions of the staggered steps
    step_length_base = 1.0  # Base length of each step in meters
    step_width_base = 1.2   # Base width of each step in meters
    
    step_length_variation = 0.3 * difficulty  # The more difficult, the more variation in length
    step_height_min, step_height_max = 0.15 * difficulty, 0.3 * difficulty

    step_length = m_to_idx(step_length_base - step_length_variation)
    step_width = m_to_idx(step_width_base)
    mid_y = m_to_idx(width) // 2

    def add_step(start_x, end_x, height, mid_y):
        half_width = step_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = -0.5, 0.5
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    for i in range(6):  # Set up 6 steps
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        step_height = np.random.uniform(step_height_min, step_height_max)
        add_step(cur_x, cur_x + step_length + dx, step_height, mid_y + dy)

        # Put goal in the center of the step
        goals[i+1] = [cur_x + (step_length + dx) / 2, mid_y + dy]

        # Prepare for the next step
        cur_x += step_length + dx
    
    # Add final goal behind the last step, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

# INSERT TERRAIN FUNCTION DEFINITIONS HERE
