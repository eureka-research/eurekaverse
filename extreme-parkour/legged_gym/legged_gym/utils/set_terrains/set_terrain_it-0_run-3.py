
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
    """Ramps, narrow passages, and elevated platforms to simulate urban challenges."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    mid_y = m_to_idx(width) // 2

    # Set first goal at the spawn point
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Define ramp and passage parameters
    ramp_length = max(1.0, 1.5 - 0.5 * difficulty)  # Decrease ramp length with difficulty
    ramp_length = m_to_idx(ramp_length)
    ramp_height = np.linspace(0, 0.25 + 0.35 * difficulty, ramp_length)  # Incline increases with difficulty
    
    narrow_passage_width = np.random.uniform(0.4, 0.5) + difficulty * 0.3  # Make narrower with higher difficulty
    narrow_passage_width = m_to_idx(narrow_passage_width)

    # Platform parameters
    platform_height = 0.2 + 0.2 * difficulty
    platform_length = m_to_idx(1.0)
    platform_width = m_to_idx(1.0)

    def add_ramp(start_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, start_x + ramp_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = ramp_height[:, np.newaxis]

    def add_passage(start_x, mid_y):
        half_width = narrow_passage_width // 2
        x1, x2 = start_x, start_x + platform_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height_field[x1 - 1, y1]  # Continue from the previous height

    def add_platform(start_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, start_x + platform_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = platform_height

    # Initialize current x position just after spawn area
    cur_x = spawn_length

    # Add ramp
    add_ramp(cur_x, mid_y)
    goals[1] = [cur_x + ramp_length // 2, mid_y]  # Middle of the first ramp
    cur_x += ramp_length
    
    # Add passage
    add_passage(cur_x, mid_y)
    goals[2] = [cur_x + platform_length // 2, mid_y]  # Middle of the narrow passage
    cur_x += platform_length

    # Add platform
    add_platform(cur_x, mid_y)
    goals[3] = [cur_x + platform_length // 2, mid_y]  # Middle of the platform
    cur_x += platform_length

    for i in range(4, 8):
        if i % 2 == 0:
            # Alternate between ramp and platform
            add_ramp(cur_x, mid_y)
            goals[i] = [cur_x + ramp_length // 2, mid_y]
            cur_x += ramp_length
        else:
            add_platform(cur_x, mid_y)
            goals[i] = [cur_x + platform_length // 2, mid_y]
            cur_x += platform_length

    return height_field, goals

def set_terrain_1(length, width, field_resolution, difficulty):
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

def set_terrain_2(length, width, field_resolution, difficulty):
    """A series of balance beams of varying heights and widths."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up beam dimensions and gaps
    # Beam height and width vary with difficulty
    beam_height_min, beam_height_max = 0.05 * difficulty, 0.3 * difficulty
    beam_width_min, beam_width_max = 0.4, 1.0  # Ensure beams are traversable
    gap_length = 0.1 + 0.7 * difficulty

    beam_length = length / 8  # Divide the length of the course into 8 segments
    beam_length = m_to_idx(beam_length)
    gap_length = m_to_idx(gap_length)

    def add_beam(start_x, end_x, y_center, beam_width, beam_height):
        half_width = beam_width // 2
        y1, y2 = y_center - half_width, y_center + half_width
        height_field[start_x:end_x, y1:y2] = beam_height

    mid_y = m_to_idx(width) // 2

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -m_to_idx(0.4), m_to_idx(0.4)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    for i in range(6):  # Set up 6 balance beams
        beam_height = np.random.uniform(beam_height_min, beam_height_max)
        beam_width = np.random.uniform(beam_width_min, beam_width_max)
        beam_width = m_to_idx(beam_width)
        
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        add_beam(cur_x, cur_x + beam_length + dx, mid_y + dy, beam_width, beam_height)

        # Put goal in the center of the beam
        goals[i+1] = [cur_x + (beam_length + dx) // 2, mid_y + dy]

        # Add gap
        cur_x += beam_length + dx + gap_length

    # Add final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_3(length, width, field_resolution, difficulty):
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

def set_terrain_4(length, width, field_resolution, difficulty):
    """Multiple hurdles for the robot to jump over, testing its jumping capabilities."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set the dimensions of the hurdles
    hurdle_width = 1.0  # 1 meter wide hurdles
    hurdle_width_idx = m_to_idx(hurdle_width)
    hurdle_height_min = 0.1 + 0.3 * difficulty  # Minimum height of hurdle
    hurdle_height_max = 0.2 + 0.5 * difficulty  # Maximum height of hurdle
    hurdle_distance = 1.0 - 0.5 * difficulty  # Distance between hurdles
    hurdle_distance_idx = m_to_idx(hurdle_distance)

    # Set initial positions and mid-point
    cur_x = m_to_idx(2)  # Start hurdles after 2 meters from the start
    mid_y = m_to_idx(width / 2)
    
    # Set the flat spawn area
    height_field[:cur_x, :] = 0
    goals[0] = [cur_x - m_to_idx(1), mid_y]  # Set the first goal near the spawn
    
    for i in range(1, 8):
        if i < 7:
            # Generate hurdle height within the defined range
            hurdle_height = np.random.uniform(hurdle_height_min, hurdle_height_max)
            
            # Add hurdles to the terrain
            y1, y2 = mid_y - hurdle_width_idx // 2, mid_y + hurdle_width_idx // 2
            height_field[cur_x:cur_x + m_to_idx(0.2), y1:y2] = hurdle_height  # Hurdle depth is 0.2 meters

            # Set goals just behind each hurdle
            goals[i] = [cur_x + m_to_idx(0.3), mid_y]  # Goals are placed slightly behind the hurdles
        
            # Increment the current x position by the distance between hurdles
            cur_x += hurdle_distance_idx

    # Final segment of the terrain after last goal
    height_field[cur_x:, :] = 0
    
    return height_field, goals

def set_terrain_5(length, width, field_resolution, difficulty):
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

def set_terrain_6(length, width, field_resolution, difficulty):
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

def set_terrain_7(length, width, field_resolution, difficulty):
    """Narrow paths and gaps for precise balancing and navigation."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define narrow path dimensions and gap lengths
    path_width = 0.4
    path_width = m_to_idx(path_width)
    path_length = 2.0  # Fixed length for simplicity
    path_length = m_to_idx(path_length)
    path_height_min, path_height_max = 0.1 + 0.3 * difficulty, 0.2 + 0.4 * difficulty
    gap_length = 0.2 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_path(start_x, end_x, mid_y):
        half_width = path_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        path_height = np.random.uniform(path_height_min, path_height_max)
        height_field[x1:x2, y1:y2] = path_height

    dx_min, dx_max = -0.05, 0.05
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.15, 0.15
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Starting base line for paths and gaps
    cur_x = spawn_length
    for i in range(6):  # Set up 6 paths with gaps
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_path(cur_x, cur_x + path_length + dx, mid_y + dy)

        # Put goal in the center of the path
        goals[i+1] = [cur_x + (path_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += path_length + dx + gap_length
    
    # Final goal behind the last path, bridging the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_8(length, width, field_resolution, difficulty):
    """Obstacle course focuses on a zigzag path with narrow steps to test lateral agility and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform dimensions - steps are much narrower but long, height increases with difficulty
    step_length = 0.8 - 0.3 * difficulty
    step_length = m_to_idx(step_length)
    step_width = np.random.uniform(0.4, 0.7)
    step_width = m_to_idx(step_width)
    step_height_min, step_height_max = 0.1 + 0.2 * difficulty, 0.1 + 0.3 * difficulty

    mid_y = m_to_idx(width) // 2

    # Helper function to add a step
    def add_step(start_x, end_x, start_y, end_y, height):
        height_field[start_x:end_x, start_y:end_y] = height
        
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
    step_direction = 1  # 1 means moving towards positive y, -1 means negative y

    for i in range(6):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        start_y = mid_y + step_direction * (step_width // 2 + dy)
        end_y = start_y + step_direction * step_width
        
        step_height = np.random.uniform(step_height_min, step_height_max)
        add_step(cur_x, cur_x + step_length, start_y, end_y, step_height)
        
        # Place the goal at the center of the step
        goal_x = cur_x + step_length // 2
        goal_y = (start_y + end_y) // 2
        goals[i + 1] = [goal_x, goal_y]
        
        cur_x += step_length + m_to_idx(0.2)  # Space between consecutive steps
        step_direction *= -1  # Switch direction for zigzag pattern
        
    # Add final goal behind the last step, filling in remaining space
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_9(length, width, field_resolution, difficulty):
    """Series of narrow beams aligned with gaps in between for the robot to balance and traverse."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up beam and gap sizes based on difficulty
    beam_width_min, beam_width_max = 0.4 - 0.2 * difficulty, 0.8 - 0.3 * difficulty
    beam_width = np.random.uniform(beam_width_min, beam_width_max)
    beam_width = m_to_idx(beam_width)
    beam_height = 0.3 + 0.5 * difficulty
    gap_width = 0.2 + 0.6 * difficulty
    gap_width = m_to_idx(gap_width)

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, beam_width, mid_y):
        half_width = beam_width // 2
        x1 = start_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x1 + beam_width, y1:y2] = beam_height

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
        add_beam(cur_x, beam_width + dx, mid_y + dy)

        # Put goal at the endpoint of each beam
        goals[i+1] = [cur_x + (beam_width + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += beam_width + dx + gap_width
    
    # Add final goal behind the last beam, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

# INSERT TERRAIN FUNCTION DEFINITIONS HERE
