
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
    """Series of ramps and turns to test the quadruped's ability to navigate inclined planes and make sharp turns."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    ramp_length = 1.0  # 1 meter ramps
    ramp_height_min, ramp_height_max = 0.05, 0.4  # start from 5 cm to 40 cm

    # Adding some variability to ramp size
    height_variation_factor = difficulty * 0.3
    ramp_length_idxs = m_to_idx(ramp_length)
    ramp_height_min, ramp_height_max = ramp_height_min + height_variation_factor, ramp_height_max + height_variation_factor

    y_center = m_to_idx(width / 2)
    
    def add_ramp(start_x, end_x, start_y, end_y, height_delta):
        x1, x2 = start_x, end_x
        y1, y2 = start_y, end_y
        for x in range(x1, x2):
            height = height_delta * ((x - x1) / max(1, x2 - x1))  # Linear ramp
            height_field[x, y1:y2] = height
    
    # Initialize flat start area
    quad_start_idx = m_to_idx(1)
    height_field[:quad_start_idx, :] = 0

    # Initial goal at the start
    goals[0] = [quad_start_idx - m_to_idx(0.5), y_center]

    cur_x = quad_start_idx

    # Create obstacles ensuring there's enough length for each
    for i in range(7):
        if i % 2 == 0:
            # Ramp upwards
            ramp_height = random.uniform(ramp_height_min, ramp_height_max)
            add_ramp(cur_x, cur_x + ramp_length_idxs, y_center - m_to_idx(0.5), y_center + m_to_idx(0.5), ramp_height)
            goal_x = cur_x + ramp_length_idxs // 2
            goal_y = y_center
        else:
            # Sharp Turn
            turn_offset = m_to_idx(1 if i // 2 % 2 == 0 else -1)
            end_y_center = y_center + turn_offset
            mid_x = cur_x + ramp_length_idxs // 2
            height_field[cur_x:cur_x + ramp_length_idxs // 2, min(y_center, end_y_center):max(y_center, end_y_center)+1] = ramp_height
            goal_x = mid_x
            goal_y = end_y_center

        goals[i+1] = [goal_x, goal_y]
        cur_x += ramp_length_idxs

    # Place the 8th goal
    goals[7] = [cur_x + ramp_length_idxs // 2, y_center]

    return height_field, goals

def set_terrain_1(length, width, field_resolution, difficulty):
    """Stepping stones along a pit requiring lateral movements."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Stepping stone dimensions and gap
    stone_length = 0.5  # meters
    stone_width = 0.5  # meters
    stone_height_min, stone_height_max = 0.1, 0.2 + 0.4 * difficulty  # varies with difficulty
    gap_length = 1.2 + 0.8 * difficulty  # longer gaps with higher difficulty

    stone_length = m_to_idx(stone_length)
    stone_width = m_to_idx(stone_width)
    stone_height_min = stone_height_min
    stone_height_max = stone_height_max
    gap_length = m_to_idx(gap_length)

    def add_stone(center_x, center_y):
        half_length = stone_length // 2
        half_width = stone_width // 2
        x1, x2 = center_x - half_length, center_x + half_length
        y1, y2 = center_y - half_width, center_y + half_width
        stone_height = np.random.uniform(stone_height_min, stone_height_max)
        height_field[x1:x2, y1:y2] = stone_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Place first goal at spawn area
    mid_y = m_to_idx(width) // 2
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    goal_index = 1

    while cur_x < m_to_idx(length) - m_to_idx(1):
        cur_x += gap_length
        
        for _ in range(2):
            cur_y = mid_y + random.choice([-1, 1]) * np.random.randint(m_to_idx(0.5), m_to_idx(1.5))
            add_stone(cur_x, cur_y)
            goals[goal_index] = [cur_x, cur_y]
            goal_index += 1
            if goal_index >= 8:
                break
        
        cur_x += stone_length
        if goal_index >= 8:
            break

    # Ensure all goals are placed
    while goal_index < 8:
        goals[goal_index] = [cur_x, mid_y]
        goal_index += 1

    return height_field, goals

def set_terrain_2(length, width, field_resolution, difficulty):
    """Stepping stones with varying heights for the robot to step on and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Parameters for stepping stones
    stone_radius_range = (0.2, 0.4)   # Radius of the stepping stones in meters
    stone_height_min, stone_height_max = 0.05 * difficulty, 0.3 * difficulty  # Height based on difficulty 
    gap_min, gap_max = 0.7, 1.2  # Horizontal gap between stones
    gap_min_idx, gap_max_idx = m_to_idx(gap_min), m_to_idx(gap_max)
    
    mid_y = m_to_idx(width) // 2

    def add_stone(center_x, center_y):
        radius = np.random.uniform(stone_radius_range[0], stone_radius_range[1])
        radius_idx = m_to_idx(radius)
        height = np.random.uniform(stone_height_min, stone_height_max)
        x1, x2 = max(0, center_x - radius_idx), min(m_to_idx(length), center_x + radius_idx)
        y1, y2 = max(0, center_y - radius_idx), min(m_to_idx(width), center_y + radius_idx)
        
        for i in range(x1, x2):
            for j in range(y1, y2):
                if np.sqrt((i - center_x)**2 + (j - center_y)**2) <= radius_idx:
                    height_field[i, j] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    for i in range(7):  # Setting up stepping stones
        gap = np.random.randint(gap_min_idx, gap_max_idx)
        cur_x += gap
        
        random_y_offset = np.random.randint(-m_to_idx(1.0), m_to_idx(1.0))  # Make sure stones are not perfectly aligned
        center_y = mid_y + random_y_offset
        
        add_stone(cur_x, center_y)

        # Put goal near the center of the stepping stone
        goals[i + 1] = [cur_x, center_y]
    
    return height_field, goals

def set_terrain_3(length, width, field_resolution, difficulty):
    """A course featuring narrow passages and walls to test the robot's navigation skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    wall_height = 0.4 + 0.3 * difficulty  # Height of the walls increases with the difficulty
    wall_width = m_to_idx(0.2)
    passage_width = m_to_idx(1.0 - 0.6 * difficulty)  # Width of the passages narrows with difficulty
    wall_distance = m_to_idx(1.0 + 1.0 * difficulty)  # Distance between walls increases with difficulty
    
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), m_to_idx(width) // 2]

    cur_x = spawn_length
    direction_toggle = -1

    def add_wall(start_x, mid_y):
        y1 = mid_y - wall_width // 2
        y2 = mid_y + wall_width // 2
        height_field[start_x:start_x + wall_width, y1:y2] = wall_height

    for i in range(7):  # Create 7 walls
        mid_y = m_to_idx(width) // 2 + direction_toggle * (passage_width // 2)
        add_wall(cur_x, mid_y)

        # Place goal at the passage center
        goals[i + 1] = [cur_x + wall_width // 2, mid_y]

        # Move to next position
        cur_x += wall_distance
        direction_toggle *= -1  # Switch the side of the next passage to create a zigzag pattern

    height_field[cur_x:, :] = 0
    goals[-1] = [cur_x - m_to_idx(0.5), m_to_idx(width) // 2]

    return height_field, goals


def set_terrain_4(length, width, field_resolution, difficulty):
    """Stepping stones course for the robot to navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    
    # Stepping stones parameters
    stone_length = 0.4 + 0.2 * difficulty
    stone_length = m_to_idx(stone_length)
    stone_width = 0.4 + 0.2 * difficulty
    stone_width = m_to_idx(stone_width)
    stone_height_min, stone_height_max = 0.05, 0.15 * difficulty
    gap_length = 0.6 + 0.4 * difficulty
    gap_length = m_to_idx(gap_length)

    def add_stepping_stone(center_x, center_y):
        half_length = stone_length // 2
        half_width = stone_width // 2
        x1, x2 = center_x - half_length, center_x + half_length
        y1, y2 = center_y - half_width, center_y + half_width
        stone_height = np.random.uniform(stone_height_min, stone_height_max)
        height_field[x1:x2, y1:y2] = stone_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)
    
    mid_y = m_to_idx(width) // 2

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(7):  # Set up 7 stepping stones
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        center_x = cur_x + stone_length + gap_length + dx
        center_y = mid_y + dy
        
        add_stepping_stone(center_x, center_y)

        # Put goal on each stepping stone
        goals[i+1] = [center_x, center_y]

        # Move to the next position
        cur_x += stone_length + gap_length + dx
    
    return height_field, goals

def set_terrain_5(length, width, field_resolution, difficulty):
    """Narrow passages with steps and turns to test the quadruped's maneuverability and agility."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    def add_passage(start_x, end_x, mid_y, passage_width, step_height):
        half_width = passage_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = step_height

    passage_length = 1.0
    passage_length = m_to_idx(passage_length)
    step_height_min, step_height_max = 0.05 + 0.15 * difficulty, 0.05 + 0.25 * difficulty
    passage_width_min, passage_width_max = 0.4, 0.55
    passage_width_min, passage_width_max = m_to_idx(passage_width_min), m_to_idx(passage_width_max)
    
    mid_y = m_to_idx(width) // 2

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn 
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)
   
    cur_x = spawn_length
    for i in range(6):  # Setting up 6 narrow passages
        passage_width = np.random.randint(passage_width_min, passage_width_max)
        step_height = np.random.uniform(step_height_min, step_height_max)

        dy = np.random.randint(dy_min, dy_max)
        passage_mid_y = mid_y + dy

        add_passage(cur_x, cur_x + passage_length, passage_mid_y, passage_width, step_height)

        # Place goals at each segment of the passage
        goals[i+1] = [cur_x + passage_length / 2, passage_mid_y]

        cur_x += passage_length

    # Add the final goal beyond the last step obstacle
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0
    
    return height_field, goals

def set_terrain_6(length, width, field_resolution, difficulty):
    """Staggered hurdles for the robot to navigate over, testing leg-lifting capabilities and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up hurdle dimensions
    hurdle_width = np.random.uniform(0.4, 1.0)
    hurdle_width = m_to_idx(hurdle_width)
    hurdle_gap_length = np.random.uniform(1.0, 2.0)
    hurdle_gap_length = m_to_idx(hurdle_gap_length)
    num_hurdles = 6
    
    # Hurdles height
    hurdle_height_min, hurdle_height_max = 0.1 + 0.2 * difficulty, 0.2 + 0.3 * difficulty
    mid_y = m_to_idx(width) // 2

    def add_hurdle(start_x, mid_y, height):
        half_width = hurdle_width // 2
        x1, x2 = start_x, start_x + m_to_idx(0.1)  # a thin hurdle in x direction
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    for i in range(num_hurdles):
        hurdle_height = np.random.uniform(hurdle_height_min, hurdle_height_max)
        add_hurdle(cur_x, mid_y, hurdle_height)
        
        # Put goal just after the hurdle
        goals[i+1] = [cur_x + m_to_idx(0.15), mid_y]

        # Add gap
        cur_x += hurdle_gap_length + m_to_idx(0.1)
    
    # Add final goal behind the last hurdle and fill in the gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    
    return height_field, goals

def set_terrain_7(length, width, field_resolution, difficulty):
    """Series of hurdles of varying height that the quadruped must jump over and navigate through."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    hurdle_width = 0.4  # Width of each hurdle in meters
    hurdle_spacing = 1.2  # Space between each hurdle
    hurdle_height_min = 0.1  # Minimum height of hurdles
    hurdle_height_max = 0.4 * difficulty  # Maximum height of hurdles based on difficulty

    dy_min, dy_max = -0.7, 0.7  # Horizontal (y-axis) range of movement for goals
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    mid_y = m_to_idx(width) // 2

    # Setup goals and the initial goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(1, 8):  # Set up 7 hurdles (one goal before each hurdle, and one final goal)
        # Hurdle positions
        hurdle_start_x = cur_x
        hurdle_end_x = cur_x + m_to_idx(hurdle_width)
        
        # Random height for each hurdle based on difficulty
        hurdle_height = random.uniform(hurdle_height_min, hurdle_height_max)
        height_field[hurdle_start_x:hurdle_end_x, :] = hurdle_height

        # Place goal after each hurdle
        cur_x += m_to_idx(hurdle_width + hurdle_spacing)

        # Slight random y-offset for goal to add variety and challenge in navigating
        dy = random.randint(dy_min, dy_max)
        goals[i] = [cur_x - m_to_idx(hurdle_spacing / 2), mid_y + dy]

    # Place final goal after last hurdle
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    return height_field, goals

def set_terrain_8(length, width, field_resolution, difficulty):
    """Narrow beams and slight turns to test the quadruped's balance and navigation."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Beam parameters
    # Make beams narrower and slightly elevated as difficulty increases
    beam_length = 1.0 + 1.0 * difficulty
    beam_width = 0.4 + 0.1 * difficulty
    beam_height_min, beam_height_max = 0.05 * difficulty, 0.3 * difficulty
    turn_ratio = 0.5  # Percentage of beams that involve a turn
    gap_between_beams = 0.2 + 0.3 * difficulty

    beam_length = m_to_idx(beam_length)
    beam_width = m_to_idx(beam_width)
    gap_between_beams = m_to_idx(gap_between_beams)
    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, start_y, end_x, end_y, beam_height):
        x1, x2 = start_x, end_x
        y1, y2 = int(min(start_y, end_y) - beam_width // 2), int(max(start_y, end_y) + beam_width // 2)
        height_field[x1:x2, y1:y2] = beam_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # First goal at spawn area
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    current_y = mid_y

    for i in range(1, 8):
        beam_height = np.random.uniform(beam_height_min, beam_height_max)
        next_x = cur_x + beam_length
        if i % 2 == 1 and difficulty > 0.3:  # Introduce turns on some beams
            turn_direction = np.random.choice([-1, 1])
            next_y = current_y + turn_direction * beam_width * (0.2 + 0.8 * difficulty)
            next_y = int(np.clip(next_y, beam_width, m_to_idx(width) - beam_width))
        else:
            next_y = current_y
            
        add_beam(cur_x, current_y, next_x, next_y, beam_height)
        
        goals[i] = [(cur_x + next_x) // 2, (current_y + next_y) // 2]

        cur_x = next_x + gap_between_beams
        current_y = next_y

    # Ensuring the final goal is just before the course end
    final_goal_x = m_to_idx(length) - m_to_idx(0.5)
    height_field[cur_x:final_goal_x, :] = 0
    goals[7] = [final_goal_x, current_y]

    return height_field, goals

def set_terrain_9(length, width, field_resolution, difficulty):
    """Stepped obstacle course with varying heights."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define obstacle dimensions based on difficulty
    step_height_min = 0.1
    step_height_max = 0.4 * difficulty + 0.1  # at hardest, height differences are 0.5 meters
    step_width_min = 0.4
    step_width_max = 1.0  # meters
    step_length = m_to_idx(1.0)  # always 1 meter length

    def add_step(start_x, end_x, min_y, max_y, height):
        """Add a step to the terrain."""
        x1, x2 = start_x, end_x
        y1, y2 = m_to_idx(min_y), m_to_idx(max_y)
        height_field[x1:x2, y1:y2] = height

    # Set up the flat spawning area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # First goal near spawn area
    mid_y = m_to_idx(width // 2.0)
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    # Create series of steps
    for i in range(7):
        step_height = random.uniform(step_height_min, step_height_max)
        step_width = random.uniform(step_width_min, step_width_max)
        step_width = m_to_idx(step_width)
        
        min_y = (mid_y - step_width // 2)
        max_y = (mid_y + step_width // 2)
        add_step(cur_x, cur_x + step_length, min_y * field_resolution, max_y * field_resolution, step_height)
        
        # Set the goal on each step
        goals[i+1] = [cur_x + step_length // 2, mid_y]

        cur_x += step_length

    # Make sure final goal coordinates are valid
    if cur_x >= m_to_idx(length):
        cur_x = m_to_idx(length - 1)

    goals[-1] = [cur_x - m_to_idx(0.5), mid_y]

    return height_field, goals

# INSERT TERRAIN FUNCTION DEFINITIONS HERE
