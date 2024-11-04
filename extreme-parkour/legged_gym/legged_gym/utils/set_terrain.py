
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
    """An enhanced obstacle course with uneven terrain, higher ramps, and narrower beams for a heightened parkour challenge."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(int) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2), dtype=int)

    # Enhanced obstacle characteristics influenced by difficulty
    ramp_length = m_to_idx(2.5 - 0.5 * difficulty)  # Slightly longer ramps even at higher difficulties
    step_height = 0.2 + 0.25 * difficulty  # Significantly higher steps at higher difficulties
    gap_width = m_to_idx(0.75 + 0.25 * difficulty)  # Slightly wider gaps at higher difficulties
    beam_width = m_to_idx(0.2 + 0.05 * difficulty)  # Narrower beams, increasing the difficulty

    cur_x, mid_y = m_to_idx(2), m_to_idx(width / 2)
    goals[0] = [cur_x, mid_y]  # First goal at starting point
    
    # Introduce uneven terrain for added complexity
    uneven_span = height_field.shape[1] // 10  # Covers a tenth of the width
    for x in range(10, m_to_idx(length), 20):  # Sparse placement along the length
        height_field[x:x+10, mid_y-uneven_span:mid_y+uneven_span] += np.random.uniform(0.1, 0.2, size=(10, uneven_span*2))

    # Sequentially create enhanced obstacles along the x-axis
    for i in range(1, 8):
        goals[i] = [cur_x + m_to_idx(1.5), mid_y]  # Adjust goal placement for increased difficulty
        if i % 3 == 0:  # Gaps
            cur_x += gap_width
        elif i % 3 == 1:  # Higher ramps
            ramp_slope = (0.3 + 0.15 * difficulty) / ramp_length
            for step in range(ramp_length):
                height_field[cur_x + step, mid_y - 10:mid_y + 10] = step * ramp_slope
            cur_x += ramp_length
        else:  # Narrower beams
            beam_length = m_to_idx(2.0)  # Slightly longer to compensate for increased height
            height_field[cur_x:cur_x + beam_length, mid_y - beam_width // 2:mid_y + beam_width // 2] += step_height
            cur_x += beam_length

    return height_field, goals

def set_terrain_1(length, width, field_resolution, difficulty):
    """Generates a slightly adjusted obstacle course to optimize quadruped robot learning and performance."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2), dtype=np.int16)

    # Slightly adjust obstacle heights and distances for optimized learning
    obstacle_base_height = 0.15  # Lower base height for less risk of collision
    max_extra_obstacle_height = 0.4 * difficulty  # Adjust obstacle variability
    obstacle_length_min, obstacle_length_max = 1.0, 2.0  # Standardize obstacle lengths
    obstacle_width_min, obstacle_width_max = 0.6, 1.2  # Adjust obstacle widths for better edge safety
    gap_between_obstacles = 1.4  # Slightly larger gaps for improved navigation

    cur_x, cur_y = m_to_idx(2.0), m_to_idx(width / 2)

    for i in range(7):
        obstacle_length = random.uniform(obstacle_length_min, obstacle_length_max)
        obstacle_width = random.uniform(obstacle_width_min, obstacle_width_max)
        extra_height = random.uniform(0, max_extra_obstacle_height)
        obstacle_height = obstacle_base_height + extra_height

        # Ensure y position is safely within bounds, considering obstacle width
        cur_y = max(cur_y, m_to_idx(obstacle_width) / 2)
        cur_y = min(cur_y, m_to_idx(width) - m_to_idx(obstacle_width) / 2)

        # Set obstacle and goal positions
        pos_x = cur_x + m_to_idx(obstacle_length / 2)
        pos_y = cur_y
        x1, x2 = pos_x - m_to_idx(obstacle_length / 2), pos_x + m_to_idx(obstacle_length / 2)
        y1, y2 = pos_y - m_to_idx(obstacle_width / 2), pos_y + m_to_idx(obstacle_width / 2)
        height_field[x1:x2, y1:y2] = obstacle_height  # Fixed by eurekaverse

        goals[i] = [pos_x, pos_y]
        cur_x += m_to_idx(obstacle_length) + m_to_idx(gap_between_obstacles)

    goals[-1] = [cur_x + m_to_idx(gap_between_obstacles / 2), cur_y]  # Last goal past the final obstacle
    goals[:, 1] = np.clip(goals[:, 1], 0, m_to_idx(width) - 1)  # Ensure y goals are within width bounds

    return height_field, goals

def set_terrain_2(length, width, field_resolution, difficulty):
    """Creates a more challenging obstacle course by varying obstacle heights, spacings, and incorporating inclined planes."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    # Initialize height_field and goals
    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    
    # Define obstacle parameters
    base_obstacle_length = 0.5  # meters
    obstacle_height_start = 0.1  # meters, start height
    obstacle_height_increment = 0.05  # meters, incremental height per obstacle, slightly increased

    # Midpoint in the width for centered goal positioning
    mid_y = m_to_idx(width) // 2
    start_x = m_to_idx(2)

    for i in range(8):
        # Adjust obstacle width and height for varying difficulty
        obstacle_width = random.uniform(0.55, 1.0)  # Increased max width for more difficulty
        obstacle_width_idx = m_to_idx(obstacle_width)
        obstacle_height = obstacle_height_start + i * obstacle_height_increment * (1 + difficulty)
        
        # Positioning obstacles, considering sharper and more varied turns
        if i % 2 == 0:
            obstacle_center_y = mid_y + (i % 3 - 1) * m_to_idx(0.6)  # Encouraging zigzag movement
        else:
            obstacle_center_y = mid_y - (i % 3 - 1) * m_to_idx(0.6)  # Variating to avoid repetitive patterns
            
        # Quantized indices for obstacle placement
        x1, x2 = start_x, start_x + m_to_idx(base_obstacle_length)
        y1, y2 = obstacle_center_y - (obstacle_width_idx // 2), obstacle_center_y + (obstacle_width_idx // 2)
        
        height_field[x1:x2, y1:y2] = obstacle_height  # Fixed by eurekaverse
        
        # Set the goals behind each obstacle to encourage complete traversal
        goals[i] = [x2, obstacle_center_y]
        
        # Increment start_x leveraging difficulty for spacing adjustments
        start_x += m_to_idx(base_obstacle_length + 1 + 0.3 * difficulty + 0.05 * random.random())  # Increased spacing variability

    return height_field, goals

def set_terrain_3(length, width, field_resolution, difficulty):
    """A more challenging course featuring variable height obstacles, sharper turns, and precision jumps."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]
        
    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    
    # Spiral staircase with increased height increments
    start_x, start_y = 2, width / 4
    x, y = m_to_idx(start_x), m_to_idx(start_y)
    stair_height_increment = 0.1 + 0.1 * difficulty  # Increased step height

    for i in range(2):
        stair_length = m_to_idx(1.5)
        stair_width = m_to_idx(0.5)
        height = i * stair_height_increment
        height_field[x:x+stair_length, y:y+stair_width] = height
        goals[i] = [x + stair_length//2, y + stair_width//2]
        x, y = x + stair_length + m_to_idx(0.5), y + stair_width

    # Introduce a winding path with sharp turns
    for j in range(2, 6):
        turn_side = j % 2
        turn_length = m_to_idx(2)
        turn_width = m_to_idx(0.25)
        turn_x = x if turn_side == 0 else x - m_to_idx(2)
        height_field[turn_x:turn_x + turn_length, y:y + turn_width] = height + stair_height_increment / 2
        goals[j] = [turn_x + turn_length // 2, y + turn_width // 2]
        x, y = turn_x + turn_length, y + (m_to_idx(1) if turn_side == 0 else -m_to_idx(1))

    # Precision jumps: smaller platforms the robot must jump across
    for k in range(6, 8):
        platform_length = m_to_idx(0.5)
        platform_width = m_to_idx(0.25)
        platform_gap = m_to_idx(0.75)  # Space between platforms
        height_field[x:x+platform_length, y:y+platform_width] = height + (k-5) * stair_height_increment
        goals[k] = [x + platform_length // 2, y + platform_width // 2]
        x += platform_length + platform_gap 

    return height_field, goals

def set_terrain_4(length, width, field_resolution, difficulty):
    """Creates an enhanced, more complex and slightly harder terrain with variance in obstacle characteristics."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2), dtype=np.int16)
    
    # Adjusting parameters to increase difficulty carefully
    base_slope_length = 1.0 + 0.7 * difficulty  # Slightly longer slopes
    max_height = 0.2 + 0.4 * difficulty  # Increased height variance
    flat_platform_size = 0.5 + difficulty * 0.7  # Larger platforms to reduce collision penalties but require better control
    
    def add_slope(base_x, base_y, length_increment, height_increment):
        """Adds a dynamic slope, varying in length and height."""
        length_indices = m_to_idx(base_slope_length + length_increment)
        for i in range(length_indices):
            height_field[base_x + i, base_y - m_to_idx(0.3):base_y + m_to_idx(0.3)] += height_increment * (i / length_indices)
    
    def add_platform(base_x, base_y, length, height):
        """Adds a flat platform with slight variance in height."""
        height_field[base_x:base_x + m_to_idx(length), base_y - m_to_idx(0.5):base_y + m_to_idx(0.5)] = height
    
    cur_x, cur_y = m_to_idx(2), m_to_idx(width // 2)
    
    for i in range(4):
        # Generating obstacles with slight variance for enhanced complexity
        slope_length_increment = random.uniform(-0.2, 0.4)  # More variance in length
        add_slope(cur_x, cur_y, slope_length_increment, max_height * random.uniform(0.8, 1.2))
        cur_x += m_to_idx(base_slope_length + slope_length_increment + 0.5)  # Slightly more space after slopes
        
        # Adjusting platform properties for improved balance challenge
        platform_height = random.uniform(0.1, 0.4) * difficulty
        platform_length_var = random.uniform(0, 0.2)  # Varying platform lengths
        add_platform(cur_x, cur_y, flat_platform_size + platform_length_var, platform_height)
        cur_x += m_to_idx(flat_platform_size + platform_length_var) + m_to_idx(0.3)  # Additional space for maneuver
        
        # Setting goal positions ensuring they are achievable but require precision
        goals[i*2] = np.array([cur_x, cur_y])
        cur_x += m_to_idx(0.2)  # Slight increment before next obstacle
        goals[i*2 + 1] = np.array([cur_x, cur_y])
    
    return height_field, goals

def set_terrain_5(length, width, field_resolution, difficulty):
    """An iterated parkour course with added complexity for an advanced quadruped robot."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16)
    
    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2), dtype=np.int16)
    
    # Adjust obstacle parameters to increase complexity slightly.
    ramp_inclines = [0.2 + 0.35 * difficulty + 0.1 * random.random() for _ in range(4)]  # Higher ramps
    step_heights = [0.3 + 0.3 * difficulty + 0.1 * random.random() for _ in range(3)]  # Taller steps
    gap_widths = [m_to_idx(0.6 + 0.55 * difficulty + 0.15 * random.random()) for _ in range(3)]  # Wider gaps
    obstacle_spacing = [m_to_idx(0.5 + 0.5 * difficulty) for _ in range(4)]  # Controlled spacing
    
    safe_zone_length = m_to_idx(2)
    mid_y = m_to_idx(width) // 2
    cur_x = safe_zone_length
    goals[0] = [cur_x, mid_y]
    
    def add_ramp(start_x, start_y, end_x, incline):
        length = end_x - start_x
        for x in range(length):
            slope = (x / length) * incline
            height_field[start_x + x, start_y - m_to_idx(0.25):start_y + m_to_idx(0.25)] = slope
    
    def add_step(start_x, step_width, step_height):
        for x in range(step_width):
            height_field[start_x + x, :] += step_height
    
    def add_gap(start_x, start_y, width):
        height_field[start_x:start_x + width, start_y - m_to_idx(0.25):start_y + m_to_idx(0.25)] = 0
    
    # Adding obstacles with slight modifications in their placement and characteristics.
    for i in range(1, 5):
        obstacle_spacing_offset = obstacle_spacing[i-1]
        if i % 2 == 0: 
            step_width = m_to_idx(1.0 + 0.2 * random.random())
            add_step(cur_x + obstacle_spacing_offset, step_width, step_heights[i//2 - 1])
        else:  
            ramp_length = m_to_idx(2.5 + 0.4 * random.random())
            add_ramp(cur_x + obstacle_spacing_offset, mid_y, cur_x + obstacle_spacing_offset + ramp_length, ramp_inclines[i//2])
        cur_x += ramp_length if i % 2 else step_width
        goals[i] = [cur_x + obstacle_spacing_offset, mid_y]

    for i in range(5, 7):
        gap_width = gap_widths[i-5]
        add_gap(cur_x + obstacle_spacing[i-5], mid_y, gap_width)
        cur_x += gap_width + obstacle_spacing[i-5]
        goals[i] = [cur_x, mid_y]

    # Adding a complex obstacle at the end to challenge the robot's precision and agility.
    complex_obstacle_length = m_to_idx(0.8)
    for _ in range(3):
        add_step(cur_x, complex_obstacle_length, 0.22)
        cur_x += complex_obstacle_length + m_to_idx(0.6)
    
    goals[7] = [cur_x + m_to_idx(1), mid_y]

    return height_field, goals

def set_terrain_6(length, width, field_resolution, difficulty):
    """Enhanced terrain with variable height obstacles, narrow passages, and twists for increased parkour challenges."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Enhanced feature parameters
    variable_height_increment = 0.1 + 0.4 * difficulty  # Increased range for difficulty
    narrow_passage_width = m_to_idx(0.5)  # Narrow passages require precision
    twist_angle_degrees = 5 + 10 * difficulty  # More pronounced twists as difficulty increases

    current_x = m_to_idx(2)  # Start placing obstacles 2 meters from spawn
    mid_y = m_to_idx(width // 2)
    current_height = 0

    for goal_idx in range(8):
        # Introduce a checker for even and odd goals for varied challenges
        if goal_idx % 4 == 0:
            # Increment heights more variably
            height_increment = variable_height_increment * random.uniform(0.5, 1.5)
            current_height += height_increment
            length = m_to_idx(1 + difficulty)  # Slightly longer obstacles as difficulty increases
            width = m_to_idx(random.uniform(0.5, 0.8))  # Varied obstacle width
            height_field[current_x:current_x + length, mid_y - width // 2: mid_y + width // 2] = current_height

        elif goal_idx % 4 == 1:
            # Introduce narrow passages
            passage_length = m_to_idx(1.5)
            height_field[current_x:current_x + passage_length, mid_y - narrow_passage_width // 2: mid_y + narrow_passage_width // 2] = current_height

        elif goal_idx % 4 == 2:
            # Return to base height for recovery
            current_height = 0

        else:
            # Add twists to the path
            twist_length = m_to_idx(0.5)
            y_offset = int(twist_angle_degrees / 90 * twist_length)
            for i in range(twist_length):
                height_field[current_x + i, mid_y - y_offset // 2 + i: mid_y + y_offset // 2 + i] = current_height

        # Update goal positions
        goals[goal_idx] = [current_x + m_to_idx(1) // 2, mid_y]
        current_x += m_to_idx(2)  # Ensure enough space for next obstacle

    return height_field, goals

def set_terrain_7(length, width, field_resolution, difficulty):
    """Challenging course with hurdles of varying heights and pits, testing jumping and precision navigation skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Basics for calculating sizes and heights influenced by difficulty
    hurdle_base_height = 0.1 + 0.2 * difficulty  # Starting height for hurdles
    pit_depth = -0.1 - 0.1 * difficulty  # Depth for pits

    mid_y = m_to_idx(width) // 2

    def add_hurdle(pos_x, width_multiplier=1, height_multiplier=1):
        """Adds a hurdle at the specified position."""
        width_idx = m_to_idx(0.5 * width_multiplier)
        height = hurdle_base_height * height_multiplier
        height_field[pos_x - width_idx:pos_x + width_idx, mid_y - width_idx:mid_y + width_idx] = height

    def add_pit(pos_x, width_multiplier=1):
        """Adds a pit at the specified position."""
        width_idx = m_to_idx(0.5 * width_multiplier)
        height_field[pos_x - width_idx:pos_x + width_idx, mid_y - width_idx:mid_y + width_idx] = pit_depth

    # Ensure the spawn area is obstacle-free
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length, mid_y]  # Place the first goal at spawn

    # Step size between obstacles
    step_size = m_to_idx(length / 9)

    # Creating hurdles and pits with increasing difficulty
    for i in range(1, 7):
        if i % 2 == 0:  # Even-indexed obstacles are hurdles of varying heights
            add_hurdle(spawn_length + i * step_size, width_multiplier=1 + 0.25 * i, height_multiplier=1 + 0.1 * i)
        else:  # Odd-indexed obstacles are pits
            add_pit(spawn_length + i * step_size, width_multiplier=1 + 0.2 * (i - 1))
        
        goals[i] = [spawn_length + i * step_size, mid_y]  # Set incremental goals
        
    # Final goal with a bit more challenge: slightly elevated
    final_goal_height = 0.2 + 0.1 * difficulty
    final_goal_pos = spawn_length + 7 * step_size
    height_field[final_goal_pos - m_to_idx(1):final_goal_pos + m_to_idx(1), mid_y - m_to_idx(0.5):mid_y + m_to_idx(0.5)] = final_goal_height
    goals[7] = [final_goal_pos, mid_y]

    return height_field, goals

def set_terrain_8(length, width, field_resolution, difficulty):
    """
    Adjusts the parkour course for a balance of challenge and learning feasibility, with specific attention to reducing edge violations and collision penalties.
    """
    
    def m_to_idx(m):
        """ Converts meters to quantized indices. """
        return np.round(m / field_resolution).astype(np.int16) if not isinstance(m, (list, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2), dtype=np.int16)

    def add_variable_obstacles(start_x, end_x, max_height=0.4):
        """ Places a series of variable height and spacing hurdles, with slight adjustments for easier navigation. """
        current_x = start_x
        while current_x < end_x:
            height = 0.15 + random.random() * (max_height - 0.15)  # random height between 0.15 and max_height
            width_span = m_to_idx(0.6 + 0.2 * (1 - difficulty))  # slightly wider for reduced difficulty
            midpoint = m_to_idx(width // 2)
            height_field[current_x:current_x+width_span, midpoint - width_span//2:midpoint + width_span//2] = height
            current_x += width_span + m_to_idx(0.8 + (random.random() * (0.6 - 0.2 * difficulty)))  # adjust spacing for difficulty
    
    # Use training feedback to adjust course layout
    add_variable_obstacles(m_to_idx(2), m_to_idx(length - 4), max_height=0.2 + 0.1 * difficulty)

    # Slightly adjust goals for diverse learning exposure
    step = (length - 4) / 7  # space goals more evenly
    for i in range(8):
        x_pos = 2 + step * i
        goals[i] = [m_to_idx(x_pos), m_to_idx(width // 2)]

    # Introduce mild elevation changes near goals to challenge balance
    for goal in goals:
        goal_x, goal_y = goal
        height_field[goal_x - m_to_idx(1):goal_x + m_to_idx(1), goal_y - m_to_idx(0.5):goal_y + m_to_idx(0.5)] += 0.05  # mild elevation around goals

    return height_field, goals

def set_terrain_9(length, width, field_resolution, difficulty):
    """
    Creates a series of ramps and flat areas that progressively increase in height,
    simulating a complex hill climbing task designed for a quadruped.
    """

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define basic parameters for elevation and ramp size
    base_elevation = 0.05  # Minimum elevation at start
    elevation_increment = 0.05 + 0.10 * difficulty  # Elevation gain per ramp
    ramp_length = m_to_idx(1.5 - 0.5 * difficulty)  # Adjust ramp length based on difficulty
    flat_length = m_to_idx(0.75 - 0.25 * difficulty)  # Adjust flat area length based on difficulty
    
    current_x = m_to_idx(2)  # Start position for the first ramp, ensuring it's beyond the spawn area
    current_elevation = base_elevation
    
    mid_y = m_to_idx(width) // 2
    goals[0] = [current_x, mid_y] # First goal at the start of the first ramp

    for i in range(1, 8):
        # Alter between ramp and flat terrain
        if i % 2 == 0:
            # Flat terrain
            height_field[current_x:current_x+flat_length, :] = current_elevation
            current_x += flat_length
        else:
            # Ramp terrain - linearly increases in height
            for j in range(ramp_length):
                height_slice = current_x + j
                height_field[height_slice, :] = current_elevation + (elevation_increment * j / ramp_length)
            current_x += ramp_length
            current_elevation += elevation_increment

        # Last goal behind the final obstacle, adjust position based on odd or even
        if i < 7:
            goals[i] = [current_x, mid_y]  # Other goals at the start of each new section
        else:
            goals[i] = [current_x + m_to_idx(0.5), mid_y]  # Final goal a bit further to ensure complete course traversal

    return height_field, goals

# INSERT TERRAIN FUNCTION DEFINITIONS HERE
