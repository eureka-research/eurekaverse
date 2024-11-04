
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

def set_terrain_1(length, width, field_resolution, difficulty):
    """Narrow hallways with varying heights for the robot to navigate and balance through."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Dimensions
    hallway_length = 1.5 + 0.3 * difficulty
    hallway_length = m_to_idx(hallway_length)
    hallways_gap = 0.4 + 0.4 * difficulty
    hallways_gap = m_to_idx(hallways_gap)
    hallway_width = 0.4 + 0.08 * difficulty
    hallway_width = m_to_idx(hallway_width)
    
    # Height settings
    min_height = 0.05 * difficulty
    max_height = 0.2 + 0.4 * difficulty
    
    mid_y = m_to_idx(width) // 2

    def add_hallway(start_x, end_x, mid_y):
        half_width = hallway_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height = np.random.uniform(min_height, max_height)
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = -0.1, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    for i in range(6):  # Create 6 hallways with gaps
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_hallway(cur_x, cur_x + hallway_length + dx, mid_y + dy)

        # Place goal in the center of the hallway
        goals[i+1] = [cur_x + (hallway_length + dx) / 2, mid_y + dy]

        # Add gap after hallway
        cur_x += hallway_length + dx + hallways_gap
    
    # Place the final goal at the end
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_2(length, width, field_resolution, difficulty):
    """Staggered narrow beams for the robot to balance and navigate across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up beam dimensions
    beam_length = 1.5 - 0.5 * difficulty  # Beam length decreases with difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = 0.45  # Maintain a minimum width to allow navigation
    beam_width = m_to_idx(beam_width)
    beam_height_min, beam_height_max = 0.1 + 0.05 * difficulty, 0.35 + 0.1 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, mid_y, height):
        half_width = beam_width // 2
        end_x = start_x + beam_length
        y1, y2 = mid_y - half_width, mid_y + half_width
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
        beam_height = np.random.uniform(beam_height_min, beam_height_max)
        add_beam(cur_x, mid_y + dy, beam_height)
        
        # Put goal in the center of the beam
        goals[i+1] = [cur_x + beam_length / 2 + dx, mid_y + dy]

        # Add gap of 0.4 meter between each beam to require maneuvering
        gap_length = m_to_idx(0.4)
        cur_x += beam_length + gap_length + dx
    
    # Add final goal in the center of the last beam, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    # Ensure the last section is on flat ground
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_3(length, width, field_resolution, difficulty):
    """Series of sloped ramps that require the robot to navigate inclines and declines."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Ramp parameters based on difficulty
    ramp_length = 1.0  # meters
    ramp_length_idx = m_to_idx(ramp_length)
    ramp_height_min = 0.05 * difficulty  # meters
    ramp_height_max = 0.5 * difficulty   # meters

    mid_y = m_to_idx(width) // 2

    def create_ramp(start_x, end_x, start_height, end_height, mid_y):
        """Creates a ramp between start_x and end_x with given start and end heights."""
        ramp_slope = (end_height - start_height) / (end_x - start_x)
        ramp_width = m_to_idx(1.0)  # 1 meter wide
        half_width = ramp_width // 2

        for x in range(start_x, end_x):
            for y in range(mid_y - half_width, mid_y + half_width):
                height_field[x, y] = start_height + ramp_slope * (x - start_x)

    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length

    for i in range(6):
        dx_min, dx_max = m_to_idx([0.1, 0.2])
        dy_min, dy_max = m_to_idx([-0.4, 0.4])
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        start_height = random.uniform(ramp_height_min, ramp_height_max)
        end_height = random.uniform(ramp_height_min, ramp_height_max)

        create_ramp(cur_x, cur_x + ramp_length_idx + dx, start_height, end_height, mid_y + dy)
        
        goals[i + 1] = [(cur_x + (ramp_length_idx + dx) / 2), mid_y + dy]
        
        cur_x += ramp_length_idx + dx + m_to_idx(0.1)

    goals[7] = [cur_x - m_to_idx(0.5), mid_y]

    return height_field, goals

def set_terrain_4(length, width, field_resolution, difficulty):
    """Stepping stones over a water-filled pit for the robot to navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Parameters for stepping stones
    stone_size_min = 0.4  # minimum side length of stone in meters
    stone_size_max = 1.0  # maximum side length of stone in meters
    stone_gap_min = 0.4  # minimum gap between stones in meters
    stone_gap_max = 1.2  # maximum gap between stones in meters
    stone_height_min, stone_height_max = 0.1, 0.4  # height variation for stones

    num_stones = 6

    def add_stepping_stone(center_x, center_y, size, height):
        half_size = size // 2
        x1, x2 = center_x - half_size, center_x + half_size
        y1, y2 = center_y - half_size, center_y + half_size
        height_field[x1:x2, y1:y2] = height

    mid_y = m_to_idx(width / 2)
    
    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # Place first goal near the spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    for i in range(num_stones):
        # Randomly determine stone size and gap
        stone_size = random.uniform(stone_size_min, stone_size_max) * (1 + 0.5 * difficulty)
        stone_size = m_to_idx(stone_size)
        stone_gap = random.uniform(stone_gap_min, stone_gap_max) * (1 - difficulty)
        stone_gap = m_to_idx(stone_gap)
        
        # Randomly place the stepping stone
        dx = random.randint(-m_to_idx(0.3), m_to_idx(0.3))
        dy = random.randint(-m_to_idx(1.0), m_to_idx(1.0))
        
        stone_height = random.uniform(stone_height_min, stone_height_max) * difficulty

        add_stepping_stone(cur_x + stone_gap, mid_y + dy, stone_size, stone_height)

        # Place a goal on each stone
        goals[i+1] = [cur_x + stone_gap, mid_y + dy]

        # Update next stone position
        cur_x += stone_gap + stone_size

    # Add final goal at the end of the course
    final_gap = m_to_idx(1.0)
    goals[-1] = [cur_x + final_gap, mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_5(length, width, field_resolution, difficulty):
    """Series of narrow beams and wide platforms testing the robot's balance and jumping abilities."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up beam and platform dimensions
    beam_width = 0.4  # Fixed narrow beam width
    beam_length = np.random.uniform(1.0, 2.0) - (1.0 * difficulty)  # Longer beam length for higher difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = m_to_idx(beam_width)
    
    platform_size_options = [m_to_idx(1.0), m_to_idx(1.2), m_to_idx(1.4)]
    platform_size = random.choice(platform_size_options)

    gap_length = 0.2 + 0.5 * difficulty  # Larger gap for higher difficulty
    gap_length = m_to_idx(gap_length)

    platform_height = np.random.uniform(0.1, 0.4) * difficulty  # Higher platform height for higher difficulty
    
    cur_x = m_to_idx(2)  # Starting position after spawn
    mid_y = m_to_idx(width / 2)

    def add_beam(start_x, mid_y):
        """Adds a narrow beam."""
        half_width = beam_width // 2
        x1, x2 = start_x, start_x + beam_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        beam_height = platform_height
        height_field[x1:x2, y1:y2] = beam_height
        return (x1 + x2) // 2, mid_y
    
    def add_platform(start_x, mid_y):
        """Adds a wide platform."""
        half_width = platform_size // 2
        x1, x2 = start_x, start_x + platform_size
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = platform_height
        return (x1 + x2) // 2, mid_y
    
    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    for i in range(6):  # Set up 6 obstacles: alternating beams and platforms
        if i % 2 == 0:
            cx, cy = add_beam(cur_x, mid_y)
        else:
            cx, cy = add_platform(cur_x, mid_y)

        goals[i + 1] = [cx, cy]  
        cur_x += beam_length if i % 2 == 0 else platform_size
        cur_x += gap_length  # Add gap after each obstacle

    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_6(length, width, field_resolution, difficulty):
    """Series of narrow beams for the quadruped to balance and navigate across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define the characteristics of the beams
    beam_width = 0.4  # meters
    beam_width_idx = m_to_idx(beam_width)
    beam_height_min = 0.1 + 0.1 * difficulty
    beam_height_max = 0.2 + 0.2 * difficulty
    gap_length = 0.3 + 0.5 * difficulty
    gap_length_idx = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, mid_y):
        half_width = beam_width_idx // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        beam_height = np.random.uniform(beam_height_min, beam_height_max)
        height_field[x1:x2, y1:y2] = beam_height

    dx_min, dx_max = m_to_idx(0.2), m_to_idx(0.3)
    dy_min, dy_max = m_to_idx(-0.6), m_to_idx(0.6)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at the end of the spawn area

    cur_x = spawn_length
    for i in range(6):  # Set up 6 beams
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        beam_length = 0.8 + 0.2 * difficulty  # meters
        beam_length_idx = m_to_idx(beam_length)
        
        add_beam(cur_x, cur_x + beam_length_idx + dx, mid_y + dy)

        # Put goal in the center of the beam
        goals[i + 1] = [cur_x + (beam_length_idx + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += beam_length_idx + dx + gap_length_idx

    # Add final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_7(length, width, field_resolution, difficulty):
    """Alternating steps and narrow bridges for the robot to navigate carefully and climb."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Step and bridge configurations
    step_height_base = 0.1
    step_height_incr = 0.1 * difficulty
    bridge_width_base = 0.5
    bridge_width_decr = 0.3 * difficulty
    step_length = m_to_idx(0.5)
    
    mid_y = m_to_idx(width) // 2
    spawn_length = m_to_idx(2)
    
    def add_step(start_x, end_x, height):
        width = m_to_idx(0.8)
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_bridge(start_x, end_x, width):
        half_width = m_to_idx(width) // 2
        height = step_height_base + step_height_incr * difficulty
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height
    
    # Set spawn area to flat ground
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    current_x = spawn_length
    steps = 3
    bridges = 2

    # Place steps and goals
    for i in range(steps):
        step_height = step_height_base + i * step_height_incr
        add_step(current_x, current_x + step_length, step_height)
        goals[i+1] = [current_x + step_length // 2, mid_y]
        current_x += step_length
    
    # Place narrow bridges and goals
    for i in range(bridges):
        bridge_width = bridge_width_base - i * bridge_width_decr
        add_bridge(current_x, current_x + m_to_idx(1.0), bridge_width)
        goals[steps+i+1] = [current_x + m_to_idx(0.5), mid_y]
        current_x += m_to_idx(1.0)

    # Add final goal at the end
    goals[-1] = [m_to_idx(11.5), mid_y]
    height_field[m_to_idx(11):, :] = 0

    return height_field, goals

def set_terrain_8(length, width, field_resolution, difficulty):
    """Series of raised beams for the robot to balance on and navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Beam specifications based on difficulty
    beam_width_min = 0.4 / (1 + difficulty)  # gets narrower as difficulty increases
    beam_width_max = 1.0 / (1 + difficulty)  # upper limit for beam width
    beam_height_min, beam_height_max = 0.1 + 0.1 * difficulty, 0.4 + 0.3 * difficulty
    beam_length = 1.0  # fixed length of the beams
    beam_length = m_to_idx(beam_length)
    space_between_beams = 0.5 + difficulty  # space increases with difficulty
    space_between_beams = m_to_idx(space_between_beams)

    def add_beam(start_x, start_y, length, width, height):
        x1, x2 = start_x, start_x + length
        y1, y2 = start_y - width // 2, start_y + width // 2
        height_field[x1:x2, y1:y2] = height

    mid_y = m_to_idx(width) // 2  # center line of the field

    # Set initial flat area for spawning
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0.0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    start_x = spawn_length

    for i in range(7):  # Create 7 beams
        beam_width = np.random.uniform(beam_width_min, beam_width_max)
        beam_width = m_to_idx(beam_width)
        beam_height = np.random.uniform(beam_height_min, beam_height_max)

        add_beam(start_x, mid_y, beam_length, beam_width, beam_height)
        
        # Place goal at the center of the beam
        goals[i + 1] = [start_x + beam_length // 2, mid_y]

        start_x += beam_length + space_between_beams

    # Fill the rest of the field with flat terrain
    height_field[start_x:, :] = 0.0
    goals[-1] = [start_x + m_to_idx(0.5), mid_y]

    return height_field, goals

def set_terrain_9(length, width, field_resolution, difficulty):
    """Narrow passageways with varying heights to test the robot's ability to navigate confined spaces."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Setup the passageway parameters
    passage_width = 0.4 + 0.6 * (1 - difficulty)
    passage_width = m_to_idx(passage_width)
    passage_height_min = 0.1 * difficulty
    passage_height_max = 0.4 * difficulty

    y_center = m_to_idx(width / 2)
    zigzag_amplitude = m_to_idx(0.5 + 1.5 * difficulty)
    zigzag_frequency = 3 + 5 * difficulty

    def add_passageway_pattern(start_x, end_x, y_center, zigzag_amplitude, zigzag_frequency):
        half_width = passage_width // 2

        for x in range(start_x, end_x):
            offset = int(zigzag_amplitude * np.sin(zigzag_frequency * 2 * np.pi * (x - start_x) / (end_x - start_x)))
            y1, y2 = y_center + offset - half_width, y_center + offset + half_width
            passage_height = np.random.uniform(passage_height_min, passage_height_max)
            height_field[x, y1:y2] = passage_height

    dx_min, dx_max = m_to_idx(-0.1), m_to_idx(0.1)
    dy_min, dy_max = m_to_idx(-0.2), m_to_idx(0.2)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), y_center]

    cur_x = spawn_length
    for i in range(7):  # Set up 7 passageway segments
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        end_x = cur_x + m_to_idx(1.5) + dx
        add_passageway_pattern(cur_x, end_x, y_center + dy, zigzag_amplitude, zigzag_frequency)
        goals[i+1] = [cur_x + (end_x - cur_x) // 2, y_center + dy]
        cur_x = end_x + m_to_idx(0.1)

    # Add final goal at the end of the last passageway
    goals[-1] = [cur_x - m_to_idx(0.5), y_center]
    height_field[cur_x:, :] = 0

    return height_field, goals

# INSERT TERRAIN FUNCTION DEFINITIONS HERE
