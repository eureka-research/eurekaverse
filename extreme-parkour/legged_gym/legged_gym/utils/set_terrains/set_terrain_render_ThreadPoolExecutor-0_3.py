
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
    """Staircase obstacles for the quadruped robot to climb up and down."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    # Initialize the height field and goals arrays
    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Parameters for stairs
    stair_width = 1.0  # width of each stair in meters
    stair_width = m_to_idx(stair_width)
    stair_height_max = 0.2  # maximum height of each stair in meters
    stair_height_min = 0.05 # minimum height of each stair in meters
    stair_depth = 0.4  # depth of each stair in meters
    stair_depth = m_to_idx(stair_depth)
    
    # Varying heights based on difficulty
    min_height = stair_height_min
    max_height = stair_height_min + difficulty * (stair_height_max - stair_height_min)
    
    # Staircase positions and dimensions
    num_stairs_per_set = min(12, max(3, int(6 * difficulty)))  # number of stairs per set, based on difficulty
    stair_sets = 2  # number of sets of stairs
    
    # Spawn area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    mid_y = m_to_idx(width // 2)

    # Place the first goal at spawn
    goals[0] = [spawn_length, mid_y]

    cur_x = spawn_length
    goal_index = 1

    for set_idx in range(stair_sets):
        for stair_idx in range(num_stairs_per_set):
            stair_height = min_height + (max_height - min_height) * (stair_idx / num_stairs_per_set)
            height_field[cur_x:cur_x+stair_depth, mid_y-stair_width//2:mid_y+stair_width//2] = stair_height
            cur_x += stair_depth
            
            # Set a goal in the middle of each stair
            if goal_index < 7:
                goals[goal_index] = [cur_x - stair_depth // 2, mid_y]
                goal_index += 1
        
        # Small flat area between stair sets
        if set_idx < stair_sets - 1:
            flat_area_depth = m_to_idx(0.8)
            height_field[cur_x:cur_x+flat_area_depth, :] = 0
            cur_x += flat_area_depth
        
    # Final goal at the end of the last staircase
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    return height_field, goals

def set_terrain_1(length, width, field_resolution, difficulty):
    """Series of narrow beams at varying heights to test the quadruped's balance and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Beam settings
    beam_width = 0.4  # narrowest allowable width for the beams
    beam_length = 1.5  # An intermediate length
    beam_height_min, beam_height_max = 0.1 * difficulty, 0.3 * difficulty + 0.1
    beam_gap_length = 0.6 + 0.4 * difficulty  # Increased with difficulty
    beam_width_idx = m_to_idx(beam_width)
    beam_length_idx = m_to_idx(beam_length)
    beam_gap_idx = m_to_idx(beam_gap_length)

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, center_y):
        half_width = beam_width_idx // 2
        x1, x2 = start_x, end_x
        y1, y2 = center_y - half_width, center_y + half_width
        beam_height = np.random.uniform(beam_height_min, beam_height_max)
        height_field[x1:x2, y1:y2] = beam_height

    dx_min, dx_max = -0.1, 0.1    
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)  # Small horizontal variations
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)  # Small vertical variations

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Add beams and corresponding goals
    cur_x = spawn_length
    for i in range(6):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        add_beam(cur_x, cur_x + beam_length_idx, mid_y + dy)
        
        # Put goal in the center of the current beam
        goals[i+1] = [cur_x + beam_length_idx // 2, mid_y + dy]
        
        # Increase current x position by beam length and gap
        cur_x += beam_length_idx + beam_gap_idx

    # Add final goal beyond the last beam, ensuring it is reachable
    goals[-1] = [cur_x + m_to_idx(0.6), mid_y]

    # Set area for the last goal to be flat ground in case of overshooting or undershooting
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_2(length, width, field_resolution, difficulty):
    """Dynamic elevations with varying height walls and narrow pathways to test balance and maneuvering."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up wall dimensions relative to the robot's height
    wall_height_min, wall_height_max = 0.1 * difficulty, 0.4 * difficulty
    wall_width = 0.2 + 0.4 * difficulty
    wall_width = m_to_idx(wall_width)
    path_width = m_to_idx(0.4)  # The minimum navigable width for narrow pathways

    def add_wall(start_x, mid_y, height):
        half_width = wall_width // 2
        x1, x2 = start_x, start_x + m_to_idx(1.0)  # 1 meter walls
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    max_y = m_to_idx(width)
    spawn_length = m_to_idx(2)
    cur_x = spawn_length

    # Spawning area is flat
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), max_y // 2]

    # Set alternating walls and pathways
    for i in range(6):
        wall_height = np.random.uniform(wall_height_min, wall_height_max)
        mid_y = random.randint(m_to_idx(1.5), max_y - m_to_idx(1.5))
        add_wall(cur_x, mid_y, wall_height)

        # Set goals at path exits to encourage maneuvering around walls
        goals[i+1] = [cur_x + m_to_idx(0.5), mid_y]
        
        # Create a path through the center
        half_path_width = path_width // 2
        path_y1, path_y2 = mid_y - half_path_width, mid_y + half_path_width
        cur_x += m_to_idx(1.0)
        height_field[cur_x:cur_x + m_to_idx(1.5), path_y1:path_y2] = 0  # Path length is 1.5 meters
        cur_x += m_to_idx(1.5)

    # Final region, ensuring enough space for the last goal
    final_path_mid_y = random.randint(m_to_idx(1.5), max_y - m_to_idx(1.5))
    goals[-1] = [cur_x + m_to_idx(0.5), final_path_mid_y]
    height_field[cur_x:, :] = 0  # Clearing the final region

    return height_field, goals

def set_terrain_3(length, width, field_resolution, difficulty):
    """Zigzag stepping stones navigated by the robot."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Parameters for stepping stones
    stone_length = m_to_idx(0.4)
    stone_width = m_to_idx(0.5 - 0.2 * difficulty)  # width decreases with difficulty
    stone_height_min = 0.1 + 0.3 * difficulty
    stone_height_max = 0.15 + 0.35 * difficulty
    gap_length = m_to_idx(0.3 + 0.5 * difficulty)

    mid_y = m_to_idx(width) // 2

    def add_stepping_stone(start_x, mid_y, stone_width, stone_length):
        half_width = stone_width // 2
        x1, x2 = start_x, start_x + stone_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        stone_height = np.random.uniform(stone_height_min, stone_height_max)
        height_field[x1:x2, y1:y2] = stone_height
        
    # Set start area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # initial goal at spawning area
    goals[0] = [m_to_idx(1), mid_y]
    
    # Start placing stepping stones after the flat ground
    cur_x = spawn_length

    # Define the zigzag pattern for the goals
    directions = [-1, 1, -1, 1, -1, 1, -1, 1]
    for i in range(8):
        dy = directions[i] * (mid_y // 2)
        add_stepping_stone(cur_x, mid_y + dy, stone_width, stone_length)
        
        # Add goals in center of each stone
        goals[i] = [cur_x + stone_length // 2, mid_y + dy]
        
        cur_x += stone_length + gap_length

    return height_field, goals

def set_terrain_4(length, width, field_resolution, difficulty):
    """Multiple uneven steps for the robot to climb at varying difficulty levels."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Step specifications
    step_height_min, step_height_max = 0.05, 0.4  # Step heights vary from 5cm to 40cm
    step_width_min, step_width_max = 0.4, 1.6  # Step widths vary from 40cm to 1.6m
    step_length = 0.6
    step_length = m_to_idx(step_length)

    mid_y = m_to_idx(width) // 2

    def add_step(start_x, height, width):
        half_width = m_to_idx(width) // 2
        x1, x2 = start_x, start_x + step_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    goal_idx = 1

    max_steps = 7  # Maximum steps we can fit considering the length
    x_padding = m_to_idx(1.0)
    remaining_distance = m_to_idx(length) - (spawn_length + x_padding * max_steps)
    
    for i in range(max_steps):
        step_height = np.random.uniform(step_height_min, step_height_max * difficulty)
        step_width = np.random.uniform(step_width_min, step_width_max)
        corrected_width = min(step_width, width - field_resolution)  # Ensure width fits in bounds
        add_step(cur_x, step_height, corrected_width)
        
        mid_y_step = mid_y + random.randint(-m_to_idx(0.5), m_to_idx(0.5)) # Add randomness to goal
        
        # Place goal in the middle of the step
        goals[goal_idx] = [cur_x + step_length // 2, mid_y_step]
        goal_idx += 1
        
        # Advance x position
        cur_x += step_length + x_padding

    # Add final goal at the end
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    return height_field, goals

def set_terrain_5(length, width, field_resolution, difficulty):
    """Series of hurdles and narrow paths forcing precise movements and jumps."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up hurdle dimensions
    hurdle_height_min, hurdle_height_max = 0.1 + 0.2 * difficulty, 0.3 + 0.3 * difficulty
    hurdle_width = 0.4 + 0.4 * difficulty
    hurdle_width = m_to_idx(hurdle_width)
    hurdle_gap_length = 0.6 + 1.0 * difficulty
    hurdle_gap_length = m_to_idx(hurdle_gap_length)

    mid_y = m_to_idx(width) // 2
    
    def add_hurdle(start_x, y):
        half_width = hurdle_width // 2
        x1, x2 = start_x, start_x + m_to_idx(0.3)
        y1, y2 = y - half_width, y + half_width
        hurdle_height = np.random.uniform(hurdle_height_min, hurdle_height_max)
        height_field[x1:x2, y1:y2] = hurdle_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [m_to_idx(1), mid_y]

    cur_x = spawn_length
    for i in range(6):  # Set up 6 hurdles
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_hurdle(cur_x + dx, mid_y + dy)

        # Put goal in front of each hurdle
        goals[i+1] = [cur_x + dx + m_to_idx(0.15), mid_y + dy]

        # Add gap
        cur_x += m_to_idx(0.3) + hurdle_gap_length

    # Add final goal behind the last hurdle, fill in the remaining area
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_6(length, width, field_resolution, difficulty):
    """Series of narrow beams to test balancing abilities of the quadruped."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define general dimensions
    beam_length = 2.0 + 3.0 * difficulty  # beams get longer with difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = m_to_idx(0.3)  # narrow beam width, consistency in challenge
    beam_height_min = 0.1 * difficulty
    beam_height_max = 0.3 * difficulty
    gap_length = m_to_idx(0.3 + 0.5 * difficulty)

    mid_y = m_to_idx(width) // 2
    
    def add_beam(start_x, end_x, mid_y):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        beam_height = np.random.uniform(beam_height_min, beam_height_max)
        height_field[x1:x2, y1:y2] = beam_height

    dx_min, dx_max = -0.1, 0.1
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
        add_beam(cur_x, cur_x + beam_length + dx, mid_y + dy)

        # Put goal in the center of the beam
        goals[i+1] = [cur_x + (beam_length + dx) // 2, mid_y + dy]

        # Add gap
        cur_x += beam_length + dx + gap_length

    # Add final goal past the last beam, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_7(length, width, field_resolution, difficulty):
    """Balancing beams and small steps for the robot to navigate across, testing its balance and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Terrain dimensions
    course_len = m_to_idx(length)
    course_wid = m_to_idx(width)
    
    # Setting initial goal and spawn area
    spawn_x = m_to_idx(2)
    mid_y = course_wid // 2
    height_field[:spawn_x, :] = 0
    goals[0] = [spawn_x - m_to_idx(0.5), mid_y]
    
    # Balancing Beam Segment
    def place_balancing_beam(start_x, beam_length, mid_y):
        half_width = m_to_idx(0.2)  # Beam width of 0.4 meters
        x1, x2 = start_x, start_x + beam_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        beam_height = 0.1 + 0.3 * difficulty  # Beam height 0.1 to 0.4 meters based on difficulty
        height_field[x1:x2, y1:y2] = beam_height

    # Small Steps Segment
    def place_small_steps(start_x, steps_length, mid_y):
        step_height = 0.05 + 0.15 * difficulty  # Step height from 0.05 to 0.2 meters
        step_width = m_to_idx(0.3)
        
        current_x = start_x
        for _ in range(3):  # Add three consecutive steps
            half_width = step_width // 2
            x1, x2 = current_x, current_x + step_width
            y1, y2 = mid_y - half_width, mid_y + half_width
            height_field[x1:x2, y1:y2] = step_height
            current_x += step_width
            step_height += 0.05  # Increasing height for each step

    # Alternating between beams and steps
    segment_length = m_to_idx(2.0)  # 2 meters segment length
    gap_length = m_to_idx(0.5 + 0.5 * difficulty)  # Gaps between beams/steps
    cur_x = spawn_x
    
    for i in range(4):  # 4 segments, alternating between beams and steps
        if i % 2 == 0:
            place_balancing_beam(cur_x, segment_length, mid_y)
            goals[i*2 + 1] = [cur_x + segment_length / 2, mid_y]
        else:
            place_small_steps(cur_x, segment_length, mid_y)
            goals[i*2 + 1] = [cur_x + segment_length, mid_y]
        
        cur_x += segment_length + gap_length
    
    # Final goal to complete the course
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0
    
    return height_field, goals

def set_terrain_8(length, width, field_resolution, difficulty):
    """Narrow balance beams at different heights for the robot to traverse."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Balance beam metrics
    beam_length = 2.0 - 0.5 * difficulty  # Making beams shorter as difficulty rises
    beam_width = 0.5
    beam_height_min = 0.2 * difficulty  # Minimum height of beams as difficulty parameter
    beam_height_max = 0.4 * difficulty  # Maximum height of beams as difficulty parameter
    gap_length = 0.5 + 0.5 * difficulty  # Gaps become longer with difficulty

    beam_length = m_to_idx(beam_length)
    beam_width = m_to_idx(beam_width)
    gap_length = m_to_idx(gap_length)

    def add_beam(start_x, end_x, center_y, height):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = center_y - half_width, center_y + half_width
        height_field[x1:x2, y1:y2] = height

    mid_y = m_to_idx(width) // 2

    # Set spawning area to flat ground
    spawn_length = m_to_idx(2)
    height_field[:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(6):  # We will have 6 balance beams
        beam_height = np.random.uniform(beam_height_min, beam_height_max)
        add_beam(cur_x, cur_x + beam_length, mid_y, beam_height)
        
        # Define goal in the middle of the beam
        goals[i+1] = [cur_x + beam_length // 2, mid_y]
        
        # Advance the current x position for the next beam, accounting for the gap
        cur_x += beam_length + gap_length

    # Add final goal after beams
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_9(length, width, field_resolution, difficulty):
    """Obstacle course with varying height platforms and narrow beams for balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and beam dimensions
    platform_height_min, platform_height_max = 0.2 * difficulty, 0.5 * difficulty
    platform_length = 1.0
    platform_length = m_to_idx(platform_length)
    platform_width = 1.0
    platform_width = m_to_idx(platform_width)
    
    beam_length = 1.5
    beam_width = 0.4
    beam_length = m_to_idx(beam_length)
    beam_width = m_to_idx(beam_width)
    
    def add_platform(start_x, start_y, length, width, height):
        end_x = start_x + length
        end_y = start_y + width
        height_field[start_x:end_x, start_y:end_y] = height

    mid_y = m_to_idx(width) // 2

    # Set the spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal slightly ahead of spawn point
    goals[0] = [spawn_length + m_to_idx(0.5), mid_y]

    cur_x = spawn_length + m_to_idx(1)
    for i in range(1, 8):
        if i % 2 == 0:  # Add a platform
            height = np.random.uniform(platform_height_min, platform_height_max)
            start_y = mid_y - platform_width // 2 + m_to_idx(random.uniform(-0.5, 0.5))
            add_platform(cur_x, start_y, platform_length, platform_width, height)
            goals[i] = [cur_x + platform_length // 2, mid_y]
            cur_x += platform_length + m_to_idx(0.4)
        else:  # Add a narrow beam
            height = np.random.uniform(platform_height_min, platform_height_max)
            start_y = mid_y - beam_width // 2 + m_to_idx(random.uniform(-0.5, 0.5))
            add_platform(cur_x, start_y, beam_length, beam_width, height)
            goals[i] = [cur_x + beam_length // 2, mid_y]
            cur_x += beam_length + m_to_idx(0.4)

    return height_field, goals

# INSERT TERRAIN FUNCTION DEFINITIONS HERE
