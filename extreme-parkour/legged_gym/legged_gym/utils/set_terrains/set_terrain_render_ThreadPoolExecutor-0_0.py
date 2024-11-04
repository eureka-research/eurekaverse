
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
    """Narrow balance beams requiring careful navigation."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up balance beam dimensions
    # Beam height slightly increases with difficulty
    beam_length = 1.8 - 0.5 * difficulty
    beam_length = m_to_idx(beam_length)
    beam_width_min, beam_width_max = 0.1, 0.3  # Width of 10cm to 30cm
    beam_height_min, beam_height_max = 0.1 + 0.1 * difficulty, 0.3 + 0.2 * difficulty
    
    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, mid_y):
        beam_width = np.random.uniform(beam_width_min, beam_width_max)
        half_width = m_to_idx(beam_width / 2)
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        beam_height = np.random.uniform(beam_height_min, beam_height_max)
        height_field[x1:x2, y1:y2] = beam_height

    dx_min, dx_max = 0.1, 0.3
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at spawn

    cur_x = spawn_length
    for i in range(6):  # Set up 6 balance beams
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        add_beam(cur_x, cur_x + beam_length + dx, mid_y + dy)

        # Put goal at the end of each beam
        goals[i+1] = [cur_x + (beam_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += beam_length + dx

    # Add final goal after the last beam
    goals[-1] = [cur_x + dx_min, mid_y]
    height_field[cur_x:, :] = 0  # Fill final section with flat ground

    return height_field, goals

def set_terrain_1(length, width, field_resolution, difficulty):
    """Narrow balance beams and tight paths for the robot to traverse."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Dimensions for beams and gaps
    beam_width_min, beam_width_max = 0.28, 0.4  # Width between 0.28m and 0.4m
    beam_length = 1.0 - 0.2 * difficulty
    beam_length = m_to_idx(beam_length)
    beam_height = 0.2 + 0.5 * difficulty  # Height varies with difficulty
    gap_length = 0.3 + 0.3 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width / 2)

    def add_beam(start_x, end_x, mid_y, beam_width, height):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

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
    for i in range(6):  # Set up 6 beams
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        beam_width = np.random.uniform(beam_width_min, beam_width_max)
        beam_width_idx = m_to_idx(beam_width)
        add_beam(cur_x, cur_x + beam_length + dx, mid_y + dy, beam_width_idx, beam_height)
        
        # Put goal in the center of the beam
        goals[i+1] = [cur_x + (beam_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += beam_length + dx + gap_length
    
    # Add final goal behind the last beam, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_2(length, width, field_resolution, difficulty):
    """Narrow pathways and beams testing balance and precision in navigation."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Pathway and beam dimensions
    beam_length_min, beam_length_max = 1.5, 2.5
    beam_length_min = m_to_idx(beam_length_min - 0.5 * difficulty)
    beam_length_max = m_to_idx(beam_length_max - 0.5 * difficulty)
    beam_width = 0.4 + 0.2 * difficulty
    beam_width = m_to_idx(beam_width)
    beam_height_min, beam_height_max = 0.1, 0.3
    beam_height_min += 0.1 * difficulty
    beam_height_max += 0.1 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, mid_y, height):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [m_to_idx(1), mid_y]  

    # Initial coordinates and gap parameters
    cur_x = spawn_length
    gap_min, gap_max = 0.2, 0.6
    gap_min = m_to_idx(gap_min)
    gap_max = m_to_idx(gap_max)

    dx_min = -0.1
    dx_max = 0.1
    dx_min = m_to_idx(dx_min)
    dx_max = m_to_idx(dx_max)

    dy_min = -0.2
    dy_max = 0.2
    dy_min = m_to_idx(dy_min)
    dy_max = m_to_idx(dy_max)

    # Place beams and goals
    for i in range(7):  # Setting up 7 beams
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        beam_length = np.random.randint(beam_length_min, beam_length_max)
        beam_height = np.random.uniform(beam_height_min, beam_height_max)
        beam_start = cur_x + gap_min + np.random.randint(gap_min, gap_max)

        add_beam(beam_start, beam_start + beam_length, mid_y + dy, beam_height)

        # Positioning the goal at the end of each beam
        goals[i + 1] = [beam_start + beam_length - m_to_idx(0.5), mid_y + dy]

        # Move the starting x coordinate to the end of the current beam
        cur_x = beam_start + beam_length
    
    # Add last goal behind the last beam
    goals[-1] = [cur_x + gap_min, mid_y]

    return height_field, goals

def set_terrain_3(length, width, field_resolution, difficulty):
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

def set_terrain_4(length, width, field_resolution, difficulty):
    """Stepping stones across the water feature for balance and coordination."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define stepping stone parameters based on difficulty
    stone_length = 0.4 + 0.3 * difficulty
    stone_width = 0.4 + 0.3 * difficulty
    stone_length_idx = m_to_idx(stone_length)
    stone_width_idx = m_to_idx(stone_width)
    stone_height_min, stone_height_max = 0.05 * difficulty, 0.15 * difficulty
    gap_distance = 0.3 + (0.6 * difficulty)
    gap_distance_idx = m_to_idx(gap_distance)

    mid_y = m_to_idx(width) // 2

    def add_stepping_stone(center_x, center_y):
        x1, x2 = center_x - stone_length_idx // 2, center_x + stone_length_idx // 2
        y1, y2 = center_y - stone_width_idx // 2, center_y + stone_width_idx // 2
        stone_height = np.random.uniform(stone_height_min, stone_height_max)
        height_field[x1:x2, y1:y2] = stone_height

    dx_min, dx_max = -0.2, 0.2
    dx_min_idx, dx_max_idx = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min_idx, dy_max_idx = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length_idx = m_to_idx(2)
    height_field[0:spawn_length_idx, :] = 0
    # Set initial goal at the end of the spawn area
    goals[0] = [spawn_length_idx - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length_idx
    for i in range(7):  # Create 7 stepping stones
        dx = np.random.randint(dx_min_idx, dx_max_idx)
        dy = np.random.randint(dy_min_idx, dy_max_idx)
        stone_center_x = cur_x + gap_distance_idx + dx
        stone_center_y = mid_y + dy
        add_stepping_stone(stone_center_x, stone_center_y)

        # Set goal at the center of the stone
        goals[i + 1] = [stone_center_x, stone_center_y]

        # Update current x position
        cur_x = stone_center_x + m_to_idx(stone_length / 2)
    
    # Make sure last section is flat ground
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_5(length, width, field_resolution, difficulty):
    """Stepping stones course that tests the quadruped's ability to navigate uneven and spaced terrain."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_width = 0.5
    platform_height_min, platform_height_max = 0.2, 0.5  # Ranges from 0.2 to 0.5 meters in height
    gap_min_length, gap_max_length = 0.3, 1.0  # Ranges from 0.3 to 1.0 meters in gap
    gap_length = lambda: m_to_idx(gap_min_length + (gap_max_length - gap_min_length) * difficulty)

    mid_y = m_to_idx(width) // 2

    def add_stepping_stone(start_x, platform_width, y_center):
        x1, x2 = start_x, start_x + platform_width
        y1, y2 = y_center - platform_width // 2, y_center + platform_width // 2
        platform_height = random.uniform(platform_height_min, platform_height_max) * difficulty
        height_field[x1:x2, y1:y2] = platform_height

    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    x = spawn_length
    for i in range(7):  # Place 7 stepping stones
        x += gap_length()
        add_stepping_stone(x, m_to_idx(platform_width), mid_y)
        goals[i + 1] = [x + m_to_idx(platform_width) / 2, mid_y]

    return height_field, goals

def set_terrain_6(length, width, field_resolution, difficulty):
    """Stepping stones course with uneven gaps and platform heights to test precision jumping."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define the stepping stones' size and spacing parameters
    stone_size = 0.4  # Size of each stone (smaller than a large platform)
    stone_size_idx = m_to_idx(stone_size)
    min_gap = 0.2 + 0.3 * difficulty  # Minimum gap size between stones
    max_gap = 0.5 + 0.5 * difficulty  # Maximum gap size between stones
    min_gap_idx = m_to_idx(min_gap)
    max_gap_idx = m_to_idx(max_gap)
    stone_height_min, stone_height_max = 0.05, 0.2 + 0.4 * difficulty  # Height range of stones

    # Define the spawn area initially flat with a first goal
    spawn_length = m_to_idx(2)
    mid_y = m_to_idx(width / 2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Define a function to add a stepping stone
    def add_stepping_stone(start_x, center_y):
        half_size = stone_size_idx // 2
        x1, x2 = start_x, start_x + stone_size_idx
        y1, y2 = center_y - half_size, center_y + half_size
        stone_height = np.random.uniform(stone_height_min, stone_height_max)
        height_field[x1:x2, y1:y2] = stone_height

    # Begin adding stepping stones starting from beyond the spawn area
    cur_x = spawn_length
    for i in range(6):  # Create 6 stepping stones
        gap = np.random.randint(min_gap_idx, max_gap_idx)
        dy = np.random.randint(-2 * stone_size_idx, 2 * stone_size_idx)  # Random horizontal displacement
        
        add_stepping_stone(cur_x, mid_y + dy)
        # Set goal at the center of each stone
        goals[i + 1] = [cur_x + stone_size_idx // 2, mid_y + dy]
        cur_x += stone_size_idx + gap
    
    # Place the final goal just beyond the last stone
    final_gap = m_to_idx(1)
    cur_x += final_gap
    goals[-1] = [cur_x, mid_y]

    return height_field, goals

def set_terrain_7(length, width, field_resolution, difficulty):
    """Narrow ridges and bridges that challenge the robot's balance and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    ridge_width = 0.5  # wide enough for robot to balance but narrow
    ridge_height = 0.3 + 0.5 * difficulty  # height dependent on difficulty
    bridge_length = 1.0  # length of the bridge
    ridge_gap = 1.0  # gap between ridges

    ridge_width = m_to_idx(ridge_width)
    ridge_height = ridge_height
    bridge_length = m_to_idx(bridge_length)
    ridge_gap = m_to_idx(ridge_gap)

    mid_y = m_to_idx(width / 2)

    def add_ridge(start_x, length, mid_y):
        half_width = ridge_width // 2
        x1, x2 = start_x, start_x + length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = ridge_height

    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [m_to_idx(0.5), mid_y]  # First goal at the spawn area

    # Set up narrow ridges
    cur_x = spawn_length
    total_elements = 6
    for i in range(total_elements):
        if i % 2 == 0:  # Even indices have ridges
            add_ridge(cur_x, bridge_length, mid_y)
            goals[i // 2 + 1] = [cur_x + bridge_length / 2, mid_y]
        cur_x += bridge_length + ridge_gap

    # Remaining part is flat for the final goal
    height_field[cur_x:, :] = 0
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    return height_field, goals

def set_terrain_8(length, width, field_resolution, difficulty):
    """Stepped terrain for the robot to navigate different levels."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Step dimensions
    step_length = 1.5 - 0.5 * difficulty
    step_length = m_to_idx(step_length)
    step_width_min, step_width_max = 0.4, 1.6
    step_width_range = [m_to_idx(step_width_min), m_to_idx(step_width_max)]
    step_height_min, step_height_max = 0.1, 0.4
    step_gap_length = 0.2 * difficulty
    step_gap_length = m_to_idx(step_gap_length)

    mid_y = m_to_idx(width) // 2

    def add_step(start_x, end_x, start_y, end_y, height):
        height_field[start_x:end_x, start_y:end_y] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(1), mid_y]

    # Create steps
    cur_x = spawn_length
    step_height_range = [step_height_min, step_height_max]

    for i in range(6):  # Create 6 steps
        step_width = np.random.randint(*step_width_range)
        step_height = np.random.uniform(*step_height_range)
        
        end_x = cur_x + step_length
        start_y, end_y = mid_y - step_width // 2, mid_y + step_width // 2
        
        add_step(cur_x, end_x, start_y, end_y, step_height)
        
        # Create goal in the center of the current step
        goals[i + 1] = [cur_x + step_length // 2, mid_y]

        # Add gap
        cur_x += step_length + step_gap_length
    
    # Final goal at the end
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_9(length, width, field_resolution, difficulty):
    """Stepping stones course where the robot must balance, walk, and jump across various heights and distances."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    stepping_stone_length = 0.6  # Length of each stepping stone in meters
    stepping_stone_width = 0.6   # Width of each stepping stone in meters
    stepping_stone_length = m_to_idx(stepping_stone_length)
    stepping_stone_width = m_to_idx(stepping_stone_width)

    min_height = 0.05 * difficulty  # Minimum height of stepping stones
    max_height = 0.3 * difficulty   # Maximum height of stepping stones

    min_gap = 0.3  # Minimum gap distance between stepping stones in meters
    max_gap = 0.8  # Maximum gap distance between stepping stones in meters
    min_gap = m_to_idx(min_gap)
    max_gap = m_to_idx(max_gap)

    mid_y = m_to_idx(width) // 2

    def add_stepping_stone(start_x, mid_y, height):
        half_width = stepping_stone_width // 2
        x1, x2 = start_x, start_x + stepping_stone_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    # Set the initial flat ground for spawning
    spawn_length = m_to_idx(1)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at spawn point

    cur_x = spawn_length
    for i in range(6):  # Add 6 stepping stones
        height = np.random.uniform(min_height, max_height)
        add_stepping_stone(cur_x, mid_y, height)

        # Set the goal on the top of the stepping stone
        goals[i+1] = [cur_x + stepping_stone_length / 2, mid_y]

        # Add a gap before the next stepping stone
        gap = np.random.randint(min_gap, max_gap)
        cur_x += stepping_stone_length + gap
    
    # Final goal beyond the last stepping stone
    goals[-1] = [cur_x + stepping_stone_length / 2, mid_y]
    add_stepping_stone(cur_x, mid_y, random.uniform(min_height, max_height))  # Adding the last stone

    return height_field, goals

# INSERT TERRAIN FUNCTION DEFINITIONS HERE
