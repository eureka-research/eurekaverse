
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
    """Sequential hurdles for the quadruped to jump over and move towards each successive goal."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    hurdle_width = 1.0 - 0.2 * difficulty
    hurdle_width = m_to_idx(hurdle_width)

    hurdle_height_min, hurdle_height_max = 0.1 + 0.2 * difficulty, 0.15 + 0.35 * difficulty
    hurdle_spacing = 1.5 - 0.5 * difficulty
    hurdle_spacing = m_to_idx(hurdle_spacing)

    mid_y = m_to_idx(width) // 2

    def add_hurdle(start_x, mid_y):
        half_width = hurdle_width // 2
        x = start_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        hurdle_height = np.random.uniform(hurdle_height_min, hurdle_height_max)
        height_field[x, y1:y2] = hurdle_height

    dx_min, dx_max = -0.2, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    for i in range(6):  # Set up 6 hurdles
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        add_hurdle(cur_x, mid_y + dy)

        # Put goal just after each hurdle
        goals[i+1] = [cur_x + m_to_idx(0.8), mid_y + dy]

        # Add hurdle spacing
        cur_x += hurdle_spacing + dx
    
    # Add final goal after the last hurdle, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_1(length, width, field_resolution, difficulty):
    """Narrow beams and steps for testing balance and precise movement."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define the beam and step parameters based on difficulty
    beam_length = 0.8 + 0.4 * difficulty  # length of the beams in meters
    beam_length = m_to_idx(beam_length)
    beam_width = 0.4 - 0.2 * difficulty  # the width of the beams in meters
    beam_width = m_to_idx(beam_width)
    beam_height_min = 0.1 * difficulty  # min beam height in meters
    beam_height_max = 0.1 + 0.3 * difficulty  # max beam height in meters
    step_height_min, step_height_max = 0.05, 0.2 + 0.2 * difficulty  # step heights in meters
    
    mid_y = m_to_idx(width // 2)

    def add_beam(start_x, end_x, center_y):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = center_y - half_width, center_y + half_width
        beam_height = np.random.uniform(beam_height_min, beam_height_max)
        height_field[x1:x2, y1:y2] = beam_height

    def add_step(x_pos, y_pos, width, height):
        """Add a small step-shaped obstacle."""
        x1, x2 = x_pos, x_pos + m_to_idx(width)
        y1, y2 = y_pos - m_to_idx(width // 2), y_pos + m_to_idx(width // 2)
        height_field[x1:x2, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Place first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Placement of Beams and Steps
    cur_x = spawn_length
    for i in range(6):  # Create 6 sections
        # Add bottom beam
        cur_x += m_to_idx(0.4)
        add_beam(cur_x, cur_x + beam_length, mid_y)
        goals[i + 1] = [cur_x + (beam_length // 2), mid_y]
        cur_x += beam_length

        # Add step ahead of beam
        step_height = np.random.uniform(step_height_min, step_height_max)
        add_step(cur_x, mid_y, 0.4 + 0.2 * difficulty, step_height)
        cur_x += m_to_idx(0.6 + 0.2 * difficulty)

    # Add final goal to terminate the course
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_2(length, width, field_resolution, difficulty):
    """An obstacle course with stepping stones and narrow balancing beams for the quadruped to navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set the dimensions for stepping stones and balancing beams
    stepping_stone_size = 0.4
    stepping_stone_size = m_to_idx(stepping_stone_size)
    balance_beam_width = 0.4
    balance_beam_width = m_to_idx(balance_beam_width)
    balance_beam_length = 2.0
    balance_beam_length = m_to_idx(balance_beam_length)
    
    stepping_stone_height = 0.1 + 0.3 * difficulty
    balance_beam_height = 0.1 + 0.2 * difficulty

    pit_depth = -0.2 - 0.8 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_stepping_stone(x, y):
        half_size = stepping_stone_size // 2
        y1, y2 = y - half_size, y + half_size
        height_field[x:x+stepping_stone_size, y1:y2] = stepping_stone_height

    def add_balance_beam(start_x, y):
        half_width = balance_beam_width // 2
        y1, y2 = y - half_width, y + half_width
        height_field[start_x:start_x+balance_beam_length, y1:y2] = balance_beam_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    current_x = spawn_length
    goal_index = 1

    # Add stepping stones along the course
    for _ in range(3):
        current_x += stepping_stone_size + m_to_idx(random.uniform(0.2, 0.5))
        y_offset = random.randint(-m_to_idx(0.5), m_to_idx(0.5))
        add_stepping_stone(current_x, mid_y + y_offset)
        
        # Put goal in the center of each stepping stone
        goals[goal_index] = [current_x + stepping_stone_size // 2, mid_y + y_offset]
        goal_index += 1

    # Add balancing beams along the course
    for _ in range(2):
        current_x += balance_beam_length + m_to_idx(random.uniform(0.2, 0.5))
        y_offset = random.randint(-m_to_idx(0.5), m_to_idx(0.5))
        add_balance_beam(current_x - balance_beam_length, mid_y + y_offset)
        
        # Put goal at the end of each balance beam
        goals[goal_index] = [current_x - balance_beam_length // 2, mid_y + y_offset]
        goal_index += 1

    # Add final stepping stone to finish line
    current_x += stepping_stone_size + m_to_idx(random.uniform(0.2, 0.5))
    add_stepping_stone(current_x, mid_y)
    goals[7] = [current_x + stepping_stone_size // 2, mid_y]

    return height_field, goals

def set_terrain_3(length, width, field_resolution, difficulty):
    """Stepping Stones: a series of small, spaced stepping stones to test the robot's precision and agility."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    
    # Function to create stepping stones
    def add_stepping_stone(center_x, center_y, stone_size, stone_height):
        """Create one stepping stone."""
        half_size = stone_size // 2
        x1, x2 = center_x - half_size, center_x + half_size
        y1, y2 = center_y - half_size, center_y + half_size
        height_field[x1:x2, y1:y2] = stone_height
    
    # Stepping stone parameters
    stone_size = m_to_idx(0.4) + m_to_idx(0.2 * difficulty)
    stone_height = 0.1 + 0.2 * difficulty
    gap_length = m_to_idx(0.5) + m_to_idx(0.5 * difficulty)
    
    mid_y = m_to_idx(width) // 2
    
    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]
    
    cur_x = spawn_length

    for i in range(1, 8):  # 7 more stepping stones
        # Randomly adjust y position within bounds for variation
        dy = random.randint(-m_to_idx(1.6), m_to_idx(1.6))
        stone_y = mid_y + dy
        
        # Ensure stepping stone is within terrain bounds
        stone_y = max(stone_size // 2, min(stone_y, m_to_idx(width) - stone_size // 2))
        
        add_stepping_stone(cur_x, stone_y, stone_size, stone_height)
        
        # Set goal in the center of the stone
        goals[i] = [cur_x, stone_y]
        
        # Prepare for the next stepping stone
        cur_x += gap_length
        
    return height_field, goals

def set_terrain_4(length, width, field_resolution, difficulty):
    """Staggered steps and narrow pathways course."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set the dimensions of staggered steps
    step_length = 0.5
    step_length = m_to_idx(step_length)
    step_width = 0.4
    step_width = m_to_idx(step_width)
    step_height_min = 0.1
    step_height_max = 0.4 * difficulty

    # Set the dimensions of the narrow pathways
    path_length = 2.0
    path_length = m_to_idx(path_length)
    path_width = 0.4
    path_width = m_to_idx(path_width)
    path_height = 0.3 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_step(start_x, width_idx, height):
        y1 = mid_y - width_idx // 2
        y2 = mid_y + width_idx // 2
        height_field[start_x:start_x + step_length, y1:y2] = height

    def add_pathway(start_x, width_idx, height):
        y1 = mid_y - width_idx // 2
        y2 = mid_y + width_idx // 2
        height_field[start_x:start_x + path_length, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at spawn

    cur_x = spawn_length
    for i in range(3):  # Set up 3 staggered steps
        step_height = np.random.uniform(step_height_min, step_height_max)
        add_step(cur_x, step_width, step_height)

        # Put goal in the center of the step
        goals[i+1] = [cur_x + step_length // 2, mid_y]

        # Move to the next step
        cur_x += step_length

    for i in range(4):  # Set up 4 narrow pathways
        add_pathway(cur_x, path_width, path_height)

        # Put goal in the center of the narrow pathway
        goals[i+4] = [cur_x + path_length // 2, mid_y]

        # Move to the next pathway
        cur_x += path_length

    # Add final goal at the end of the last pathway
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    return height_field, goals

def set_terrain_5(length, width, field_resolution, difficulty):
    """A series of staggered steps and narrow walkways to challenge the quadruped's precise stepping and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set dimensions and properties for steps and walkways
    step_length = 0.4  # fixed size
    step_length_idx = m_to_idx(step_length)
    step_width = 1.0  # at least 1 meter wide
    step_width_idx = m_to_idx(step_width)
    step_height_min, step_height_max = 0.1 * difficulty, 0.3 * difficulty

    walkway_length = 1.0  # length of the walkways
    walkway_length_idx = m_to_idx(walkway_length)
    walkway_width = 0.4  # narrow width
    walkway_width_idx = m_to_idx(walkway_width)
    walkway_height = 0.15

    mid_y = m_to_idx(width) // 2

    def add_step(start_x, end_x, mid_y):
        half_width = step_width_idx // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        step_height = np.random.uniform(step_height_min, step_height_max)
        height_field[x1:x2, y1:y2] = step_height

    def add_walkway(start_x, end_x, mid_y):
        half_width = walkway_width_idx // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = walkway_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Arrange the steps and walkways
    cur_x = spawn_length
    dy_min, dy_max = -1, 1
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    for i in range(3):  # Set up 3 steps
        add_step(cur_x, cur_x + step_length_idx, mid_y)
        goals[i + 1] = [cur_x + step_length_idx / 2, mid_y]

        cur_x += step_length_idx

        dy = np.random.randint(dy_min, dy_max)
        add_walkway(cur_x, cur_x + walkway_length_idx, mid_y + dy)
        goals[i + 4] = [cur_x + walkway_length_idx / 2, mid_y + dy]

        cur_x += walkway_length_idx
    
    # Add final goal at the end of terrain
    goals[-3] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_6(length, width, field_resolution, difficulty):
    """A serpentine path with narrow walkways and small gaps to challenge precise navigation"""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Setup the walkway dimensions
    walkway_length = 1.2 - 0.4 * difficulty  # Vary the lengths of the walkways with difficulty
    walkway_length = m_to_idx(walkway_length)
    walkway_width = np.random.uniform(0.4, 0.8)  # Narrow walkways
    walkway_width = m_to_idx(walkway_width)
    walkway_height_min, walkway_height_max = 0.0, 0.15 + 0.35 * difficulty
    gap_length = 0.2 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 3

    def add_walkway(start_x, end_x, center_y):
        half_width = walkway_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = center_y - half_width, center_y + half_width
        walkway_height = np.random.uniform(walkway_height_min, walkway_height_max)
        height_field[x1:x2, y1:y2] = walkway_height

    dx_min, dx_max = -0.2, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -1.0, 1.0
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Starting X coordinate after the spawn area
    cur_x = spawn_length

    for i in range(6):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_walkway(cur_x, cur_x + walkway_length + dx, mid_y + dy)

        # Put goal in the center of the walkway
        goals[i + 1] = [cur_x + (walkway_length + dx) / 2, mid_y + dy]

        # Add a gap
        cur_x += walkway_length + dx + gap_length
    
    # Add final goal behind the last walkway, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0
  
    return height_field, goals

def set_terrain_7(length, width, field_resolution, difficulty):
    """Low barriers the robot needs to navigate around or step over."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up barrier dimensions
    barrier_height_min, barrier_height_max = 0.1, 0.3 + 0.2 * difficulty
    barrier_gap = 1.0 + 0.5 * difficulty  # Space between barriers
    barrier_gap = m_to_idx(barrier_gap)

    mid_y = m_to_idx(width) // 2

    def add_barrier(start_x, end_x, y):
        x1, x2 = start_x, end_x
        y1, y2 = y - m_to_idx(0.3), y + m_to_idx(0.3)  # Barriers are 0.6 meters wide
        height_field[x1:x2, y1:y2] = np.random.uniform(barrier_height_min, barrier_height_max)

    dy_min, dy_max = -0.75, 0.75  # Offset range for barrier placement
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at the spawn location
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    for i in range(7):  # Set up 7 barriers with corresponding goals
        dy = np.random.randint(dy_min, dy_max)
        barrier_start_x = cur_x
        barrier_end_x = cur_x + m_to_idx(0.4)  # Each barrier is 0.4 meters long
        add_barrier(barrier_start_x, barrier_end_x, mid_y + dy)

        # Put goal just after and a little offset from the barrier
        goal_offset = m_to_idx(0.2)  # Offset the goal slightly after the barrier
        goals[i+1] = [barrier_end_x + goal_offset, mid_y + dy + np.random.choice([-m_to_idx(0.3), m_to_idx(0.3)])]
        
        # Move to the next barrier position taking the gap into consideration
        cur_x += m_to_idx(0.4) + barrier_gap
    
    return height_field, goals

def set_terrain_8(length, width, field_resolution, difficulty):
    """Stepping stones across a variable-height terrain with narrow paths and randomized gaps."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up stepping stone dimensions
    stone_length = 0.5 + 0.3 * difficulty
    stone_length = m_to_idx(stone_length)
    stone_width = 0.4 + 0.2 * difficulty
    stone_width = m_to_idx(stone_width)
    stone_height_range = (0.1 * difficulty, 0.4 + 0.4 * difficulty)
    gap_length_range = (0.4, 0.8 + 0.2 * difficulty)
    gap_length_range = m_to_idx(gap_length_range)

    def add_stepping_stone(start_x, mid_y):
        """Adds a stepping stone at the specified location."""
        half_length = stone_length // 2
        half_width = stone_width // 2
        x1, x2 = start_x - half_length, start_x + half_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        stone_height = np.random.uniform(*stone_height_range)
        height_field[x1:x2, y1:y2] = stone_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    mid_y = m_to_idx(width) // 2
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Randomly place stepping stones and set goals
    cur_x = spawn_length
    path_y = mid_y
    for i in range(7):
        gap_length = np.random.randint(*gap_length_range)
        cur_x += gap_length
        dy = np.random.randint(m_to_idx(-0.9), m_to_idx(0.9)) if i % 2 == 1 else 0
        path_y = np.clip(path_y + dy, 0, m_to_idx(width) - 1)
        add_stepping_stone(cur_x, path_y)
        goals[i + 1] = [cur_x, path_y]

    # Ensure final goal is within bounds
    goals[-1] = [min(cur_x + m_to_idx(1), m_to_idx(length) - 1), path_y]

    return height_field, goals

def set_terrain_9(length, width, field_resolution, difficulty):
    """Slopes, ramps, and stepping stones to test the quadruped's ability to navigate uneven terrains."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up dimensions for ramps, slopes, and stepping stones
    ramp_length = 1.0 * (1 - difficulty)
    ramp_length_idx = m_to_idx(ramp_length)
    ramp_height = 0.1 + 0.5 * difficulty  # Ramps/slopes get steeper with increased difficulty
    stepping_stone_size = 0.4 + 0.1 * difficulty  # Stepping stones get smaller with increased difficulty
    stepping_stone_size_idx = m_to_idx([stepping_stone_size, stepping_stone_size])
    
    mid_y = m_to_idx(width) // 2

    def add_ramp(start_x, end_x, mid_y, height_increase):
        """Creates a ramp from start_x to end_x, increasing height by height_increase"""
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - m_to_idx(0.5), mid_y + m_to_idx(0.5)
        ramp_profile = np.linspace(0, height_increase, x2 - x1).reshape(-1, 1)
        height_field[x1:x2, y1:y2] = ramp_profile

    def add_stepping_stone(center_x, center_y, height):
        """Creates a stepping stone centered at center_x, center_y with a specific height"""
        x1, x2 = center_x - stepping_stone_size_idx[0] // 2, center_x + stepping_stone_size_idx[0] // 2
        y1, y2 = center_y - stepping_stone_size_idx[1] // 2, center_y + stepping_stone_size_idx[1] // 2
        height_field[x1:x2, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # First goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(2):  # Adding 2 ramps or slopes
        add_ramp(cur_x, cur_x + ramp_length_idx, mid_y, ramp_height)
        # Place goal at the top of each ramp
        goals[i + 1] = [(cur_x + ramp_length_idx) // 2, mid_y]
        # Move for the next ramp
        cur_x += ramp_length_idx
    
    for j in range(3, 7):  # Adding stepping stones
        step_x_offset = random.randint(-1, 1) * m_to_idx(0.2)
        step_y_offset = random.randint(-2, 2) * m_to_idx(0.1)
        add_stepping_stone(cur_x + step_x_offset, mid_y + step_y_offset, random.uniform(0.05, 0.3) * difficulty)
        goals[j] = [cur_x + step_x_offset, mid_y + step_y_offset]
        cur_x += m_to_idx(0.5)
    
    # Final goal at the end of the field
    goals[-1] = [cur_x + m_to_idx(2), mid_y]

    return height_field, goals

# INSERT TERRAIN FUNCTION DEFINITIONS HERE
