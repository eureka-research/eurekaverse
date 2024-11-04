
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

def set_terrain_1(length, width, field_resolution, difficulty):
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

def set_terrain_2(length, width, field_resolution, difficulty):
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

def set_terrain_3(length, width, field_resolution, difficulty):
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

def set_terrain_6(length, width, field_resolution, difficulty):
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

def set_terrain_7(length, width, field_resolution, difficulty):
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

def set_terrain_8(length, width, field_resolution, difficulty):
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

def set_terrain_9(length, width, field_resolution, difficulty):
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

def set_terrain_10(length, width, field_resolution, difficulty):
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

def set_terrain_11(length, width, field_resolution, difficulty):
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

def set_terrain_12(length, width, field_resolution, difficulty):
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

def set_terrain_13(length, width, field_resolution, difficulty):
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

def set_terrain_14(length, width, field_resolution, difficulty):
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

def set_terrain_15(length, width, field_resolution, difficulty):
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


def set_terrain_16(length, width, field_resolution, difficulty):
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

def set_terrain_17(length, width, field_resolution, difficulty):
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

def set_terrain_18(length, width, field_resolution, difficulty):
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

def set_terrain_19(length, width, field_resolution, difficulty):
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

def set_terrain_20(length, width, field_resolution, difficulty):
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

def set_terrain_21(length, width, field_resolution, difficulty):
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

def set_terrain_22(length, width, field_resolution, difficulty):
    """Courses that combine narrow steps, long gaps, and complex slopes to test climbing, jumping, and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 1.0
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.2 + 0.25 * difficulty, 0.3 + 0.35 * difficulty
    gap_length = 0.4 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)
    slope_length = 1.0 + 0.5 * difficulty
    slope_length = m_to_idx(slope_length)

    mid_y = m_to_idx(width) // 2    

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_slope(start_x, mid_y, length, height, direction=1):
        half_width = platform_width // 2
        x1, x2 = start_x, start_x + length
        y1, y2 = mid_y - half_width, mid_y + half_width
        slope = np.linspace(0, height, x2 - x1)[::direction]
        slope = slope[:, None]
        height_field[x1:x2, y1:y2] += slope

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    # Sequence of Platforms
    for i in range(3):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        height = np.random.uniform(platform_height_min, platform_height_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, height)
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length
    
    # Slopes
    for i in range(3, 7):
        height = np.random.uniform(platform_height_min, platform_height_max)
        direction = np.random.choice([-1, 1])
        add_slope(cur_x, mid_y, slope_length, height, direction)
        goals[i+1] = [cur_x + slope_length // 2, mid_y]
        cur_x += slope_length + gap_length

    # Ending platform
    add_platform(cur_x, cur_x + platform_length, mid_y, 0)
    goals[-1] = [cur_x + platform_length / 2, mid_y]

    return height_field, goals

def set_terrain_23(length, width, field_resolution, difficulty):
    """Series of staggered narrow beams with height variations for the quadruped to balance and navigate through."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    # Initialize height field and goals
    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Beam dimensions and setup
    beam_width = 0.2 + 0.1 * difficulty
    beam_width = m_to_idx(beam_width)
    beam_length = 1.0 + 0.2 * difficulty
    beam_length = m_to_idx(beam_length)
    beam_height_min, beam_height_max = 0.1 + 0.1 * difficulty, 0.2 + 0.4 * difficulty
    gap_length = 0.4 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, center_y, height):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = center_y - half_width, center_y + half_width
        height_field[x1:x2, y1:y2] = height

    # Flatten the spawn area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(6):  # Create a sequence of beams with gaps
        dx = np.random.randint(-m_to_idx(0.1), m_to_idx(0.1))
        dy = np.random.randint(-m_to_idx(0.3), m_to_idx(0.3))
        beam_height = np.random.uniform(beam_height_min, beam_height_max)
        add_beam(cur_x, cur_x + beam_length + dx, mid_y + dy, beam_height)

        # Place goal in the middle of each beam
        goals[i + 1] = [cur_x + (beam_length + dx) / 2, mid_y + dy]

        # Increment current x by the length of the beam and the gap
        cur_x += beam_length + dx + gap_length

    # Place the final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_24(length, width, field_resolution, difficulty):
    """Combination of side ramps, platforms, and narrow beams to test precision, balance, and agility."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    mid_y = m_to_idx(width) // 2
    
    # General obstacle dimensions
    platform_length = m_to_idx(1.2 - 0.3 * difficulty)
    platform_width = m_to_idx(np.random.uniform(1.0, 1.5))
    platform_height_min = 0.1 + 0.2 * difficulty
    platform_height_max = 0.2 + 0.3 * difficulty

    ramp_slope = np.linspace(0, m_to_idx(0.4 + 0.4 * difficulty), platform_width)
    beam_width = m_to_idx(0.4)
    beam_length = m_to_idx(1.5)
    gap_length = m_to_idx(0.1 + 0.5 * difficulty)

    def add_platform(start_x, end_x, y, height):
        """Add a rectangular platform."""
        half_width = platform_width // 2
        height_field[start_x:end_x, y - half_width:y + half_width] = height

    def add_ramp(start_x, mid_y, direction=1):
        """Add a ramp oriented as specified by direction (1 indicates upwards, -1 indicates downwards)."""
        half_width = platform_width // 2
        ramp_height = np.random.uniform(platform_height_min, platform_height_max)
        ramp = np.outer(np.linspace(0, direction * ramp_height, platform_length), np.ones(2 * half_width))
        height_field[start_x:start_x + platform_length, mid_y - half_width:mid_y + half_width] = ramp

    def add_beam(start_x, end_x, y, height):
        """Add a narrow beam."""
        half_width = beam_width // 2
        height_field[start_x:end_x, y - half_width:y + half_width] = height

    # Initialize flat spawn area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]
    
    cur_x = spawn_length

    for i in range(3):
        # Alternating between platforms and ramps
        if i % 2 == 0:
            platform_height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)
            goals[i + 1] = [cur_x + platform_length // 2, mid_y]
        else:
            direction = (-1)**i  # Alternate ramp direction (upwards/downwards)
            add_ramp(cur_x, mid_y, direction)
            goals[i + 1] = [cur_x + platform_length // 2, mid_y]
        
        cur_x += platform_length + gap_length
    
    # Add beams in between ramps
    for j in range(3, 5):
        add_beam(cur_x, cur_x + beam_length, mid_y, 0)
        goals[j + 1] = [cur_x + beam_length // 2, mid_y]
        cur_x += beam_length + gap_length

    # Add final platform leading to the last goal
    final_platform_height = np.random.uniform(platform_height_min, platform_height_max)
    add_platform(cur_x, cur_x + platform_length, mid_y, final_platform_height)
    goals[-1] = [cur_x + platform_length // 2, mid_y]

    return height_field, goals

def set_terrain_25(length, width, field_resolution, difficulty):
    """Obstacle course with slalom ladders and varying height barriers for the robot to navigate through."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    slalom_gap = 0.8 - 0.3 * difficulty  # Slalom gap decreases with difficulty
    slalom_gap = m_to_idx(slalom_gap)
    barrier_height = 0.05 + 0.25 * difficulty  # Barrier height increases with difficulty
    barrier_width = 1.0 + 0.5 * difficulty  # Barrier width increases slightly with difficulty
    barrier_width = m_to_idx(barrier_width)
    slalom_y_positions = [m_to_idx(1.0) + m_to_idx(2.0) * i for i in range(4)]  # Positioning slalom barriers

    def add_slalom_barrier(start_x, width, height, y_positions):
        for y in y_positions:
            height_field[start_x:start_x+width, y:y + m_to_idx(0.4)] = height

    dx_min, dx_max = 2.0, 3.0
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)

    # Initial flat ground for spawning
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    mid_y = m_to_idx(width) // 2
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(4):  # Set up 4 slalom sections
        add_slalom_barrier(cur_x, barrier_width, barrier_height, slalom_y_positions)

        # Place goals to navigate the slaloms
        goals[i+1] = [cur_x + m_to_idx(0.5), mid_y - m_to_idx(1.5) * ((i+1) % 2)]
        
        # Add a clear pathway between the slalom sections
        cur_x += barrier_width + slalom_gap

    # Add final goal at the end of the course
    goals[-1] = [cur_x + m_to_idx(1.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_26(length, width, field_resolution, difficulty):
    """Obstacle course featuring staggered stepping stones and varying elevation platforms to test agility and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    stepping_stone_length = 0.6 - 0.2 * difficulty
    stepping_stone_length = m_to_idx(stepping_stone_length)
    stepping_stone_width = np.random.uniform(0.4, 0.6)
    stepping_stone_width = m_to_idx(stepping_stone_width)
    stepping_stone_height_min, stepping_stone_height_max = 0.15 * difficulty, 0.35 * difficulty
    small_gap_length = 0.05 + 0.25 * difficulty
    small_gap_length = m_to_idx(small_gap_length)

    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.1)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.4 * difficulty, 0.1 + 0.5 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_stepping_stone(start_x, end_x, y_start, y_end, height):
        """Add a stepping stone to the height_field."""
        height_field[start_x:end_x, y_start:y_end] = height
        
    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.1, 0.1
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length

    for i in range(3):  # Set up 3 stepping stones
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        stone_height = np.random.uniform(stepping_stone_height_min, stepping_stone_height_max)
        
        # Ensure that stones remain within bounds
        y_center = mid_y + dy
        y_start = max(1, y_center - stepping_stone_width // 2, m_to_idx(1))
        y_end = min(m_to_idx(width) - 1, y_center + stepping_stone_width // 2, m_to_idx(width - 1))
        
        add_stepping_stone(cur_x, cur_x + stepping_stone_length + dx, y_start, y_end, stone_height)

        # Put goal in the center of the current stone
        goals[i+1] = [cur_x + (stepping_stone_length + dx) / 2, y_center]

        # Creating gaps
        cur_x += stepping_stone_length + dx + small_gap_length

    for i in range(4, 8):  # Adding 4 platforms
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)

        # Put goal in the center of the platform
        goals[i] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += platform_length + dx + small_gap_length
    
    # Add final goal near the end of the course
    goals[-1] = [cur_x + m_to_idx(1), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_27(length, width, field_resolution, difficulty):
    """Stepping stones in a shallow water course, requiring the robot to navigate by stepping on a series of small platforms."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up stepping stone dimensions
    stone_diameter = 0.4 + 0.1 * difficulty  # Diameter of each stepping stone
    stone_diameter = m_to_idx(stone_diameter)
    stone_height = np.random.uniform(0.05, 0.2) + 0.15 * difficulty  # Height of the stones
    gap_distance = 0.4 + 0.6 * difficulty  # Distance between stepping stones
    gap_distance = m_to_idx(gap_distance)
    
    middle_y = m_to_idx(width) // 2

    def place_stone(x, y):
        radius = stone_diameter // 2
        height_field[x - radius:x + radius + 1, y - radius:y + radius + 1] = stone_height

    # Set the spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), middle_y]

    current_x = spawn_length
    for i in range(1, 7):
        dx = np.random.randint(-1, 2)  # Small variation in x position
        dy = np.random.randint(-3, 4)  # Small variation in y position
        x_pos = current_x + gap_distance + dx
        y_pos = middle_y + dy
        place_stone(x_pos, y_pos)

        # Place goal at each stepping stone
        goals[i] = [x_pos, y_pos]

        current_x += gap_distance + stone_diameter

    # Add final goal past the last stepping stone, ensuring it is on flat ground
    final_gap = m_to_idx(1)
    final_x = current_x + final_gap
    height_field[final_x:, :] = 0
    goals[-1] = [final_x - m_to_idx(0.5), middle_y]

    return height_field, goals

def set_terrain_28(length, width, field_resolution, difficulty):
    """Multiple narrow paths with subtle ramps for balance and precision traversal."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define narrow path and ramp dimensions
    path_length = 1.0 - 0.3 * difficulty
    path_length = m_to_idx(path_length)
    path_width = np.random.uniform(0.4, 0.7)  # Ensure narrow but traversable paths
    path_width = m_to_idx(path_width)
    ramp_height_min, ramp_height_max = 0.05 + 0.25 * difficulty, 0.2 + 0.4 * difficulty
    ramp_length = 0.4 + 0.3 * difficulty
    ramp_length = m_to_idx(ramp_length)

    mid_y = m_to_idx(width) // 2

    def add_narrow_path(start_x, end_x, mid_y):
        half_width = path_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = 0

    def add_narrow_ramp(start_x, end_x, mid_y):
        half_width = path_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        linear_height = np.linspace(0, ramp_height, x2 - x1)[:, None]
        height_field[x1:x2, y1:y2] = linear_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Set first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    toggle = -1
    for i in range(6):  # Create alternating narrow paths and ramps
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        if i % 2 == 0:  # Add narrow path
            add_narrow_path(cur_x, cur_x + path_length + dx, mid_y + dy * toggle)
        else:  # Add ramp
            add_narrow_ramp(cur_x, cur_x + ramp_length + dx, mid_y + dy * toggle)

        # Place goal in the middle of each section
        goals[i + 1] = [cur_x + (path_length + dx) / 2, mid_y + dy * toggle]

        # Alternate path direction
        toggle *= -1
        cur_x += max(path_length, ramp_length) + dx

    # Add final goal behind the last section
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_29(length, width, field_resolution, difficulty):
    """Multiple narrow bridges, stepping stones and asymmetric ramps traversal to test balance, precision, and climbing."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define obstacle dimensions
    bridge_length = 1.2 - 0.4 * difficulty  # Length of each bridge
    bridge_length = m_to_idx(bridge_length)
    bridge_width = np.random.uniform(0.4, 0.6)  # Narrow bridges
    bridge_width = m_to_idx(bridge_width)
    bridge_height_min, bridge_height_max = 0.1, 0.35 * difficulty

    stepping_stone_length = np.random.uniform(0.4, 0.6)  # Stepping stones
    stepping_stone_length = m_to_idx(stepping_stone_length)
    stepping_stone_width = np.random.uniform(0.4, 0.5)
    stepping_stone_width = m_to_idx(stepping_stone_width)
    stepping_stone_height_min, stepping_stone_height_max = 0.1, 0.35 * difficulty

    ramp_length = 1.0  # Ramp length is fixed
    ramp_length = m_to_idx(ramp_length)
    ramp_height_min, ramp_height_max = 0.0 + 0.4 * difficulty, 0.05 + 0.45 * difficulty

    gap_length = 0.2 + 0.5 * difficulty  # Gap lengths
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width / 2)

    def add_bridge(x_start, x_end, y_mid):
        half_width = bridge_width // 2
        y1, y2 = y_mid - half_width, y_mid + half_width
        bridge_height = np.random.uniform(bridge_height_min, bridge_height_max)
        height_field[x_start:x_end, y1:y2] = bridge_height

    def add_stepping_stone(x_start, x_end, y_mid):
        half_width = stepping_stone_width // 2
        y1, y2 = y_mid - half_width, y_mid + half_width
        stepping_stone_height = np.random.uniform(stepping_stone_height_min, stepping_stone_height_max)
        height_field[x_start:x_end, y1:y2] = stepping_stone_height

    def add_ramp(x_start, x_end, y_mid, slant_direction):
        half_width = bridge_width // 2
        y1, y2 = y_mid - half_width, y_mid + half_width
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        slant = np.linspace(0, ramp_height, num=y2-y1)[::slant_direction]
        height_field[x_start:x_end, y1:y2] = slant[np.newaxis, :]  # Add a dimension for broadcasting
    
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at spawn

    obstacle_count = 0
    cur_x = spawn_length

    while obstacle_count < 6:
        obstacle_type = np.random.choice(["bridge", "stepping_stone", "ramp"])

        if obstacle_type == "bridge":
            add_bridge(cur_x, cur_x + bridge_length, mid_y)
            goals[obstacle_count + 1] = [cur_x + bridge_length / 2, mid_y]
            cur_x += bridge_length + gap_length

        elif obstacle_type == "stepping_stone":
            add_stepping_stone(cur_x, cur_x + stepping_stone_length, mid_y)
            goals[obstacle_count + 1] = [cur_x + stepping_stone_length / 2, mid_y]
            cur_x += stepping_stone_length + gap_length

        elif obstacle_type == "ramp":
            slant_direction = np.random.choice([1, -1])
            add_ramp(cur_x, cur_x + ramp_length, mid_y, slant_direction)
            goals[obstacle_count + 1] = [cur_x + ramp_length / 2, mid_y]
            cur_x += ramp_length + gap_length

        obstacle_count += 1

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_30(length, width, field_resolution, difficulty):
    """Slanted balance beams and narrow pathways testing robot's balance and coordination."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not isinstance(m, (list, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Convert critical points
    length_idx = m_to_idx(length)
    width_idx = m_to_idx(width)
    spawn_length = m_to_idx(2)
    mid_y = width_idx // 2

    # Set the spawn area
    height_field[:spawn_length, :] = 0
    goals[0] = [spawn_length // 2, mid_y]

    # Set up balance beam dimensions
    balance_beam_width = m_to_idx(0.4)
    balance_beam_length = m_to_idx(1.5) + m_to_idx(difficulty)
    beam_height_min, beam_height_max = 0.1, 0.4

    def add_balance_beam(start_x, mid_y, length, width, height):
        half_width = width // 2
        x1, x2 = start_x, start_x + length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    current_x = spawn_length
    for i in range(7):
        beam_height = random.uniform(beam_height_min * (1 + difficulty), beam_height_max * (0.5 + difficulty))
        add_balance_beam(current_x, mid_y, balance_beam_length, balance_beam_width, beam_height)

        # Place goals at the ends of each balance beam
        goals[i+1] = [current_x + balance_beam_length // 2, mid_y]

        # Update current_x to the end of current balance beam and account for small gaps
        current_x += balance_beam_length + m_to_idx(0.1 + 0.2 * difficulty)

    # Final goal at the end of the last beam
    goals[-1] = [current_x - balance_beam_length // 2, mid_y]
    
    return height_field, goals

def set_terrain_31(length, width, field_resolution, difficulty):
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

def set_terrain_32(length, width, field_resolution, difficulty):
    """Staggered platforms and ramps with increasing height for climbing and navigation"""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Parameters for platforms and ramps
    platform_length = m_to_idx(1.0 - 0.3 * difficulty)
    platform_width = m_to_idx(np.random.uniform(1.0, 1.6))
    ramp_width = m_to_idx(np.random.uniform(0.7, 1.0))
    platform_height_min, platform_height_max = 0.0 + 0.2 * difficulty, 0.1 + 0.3 * difficulty
    ramp_height_min, ramp_height_max = 0.05 + 0.1 * difficulty, 0.15 + 0.4 * difficulty
    gap_length = m_to_idx(0.1 + 0.5 * difficulty)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_ramp(start_x, end_x, mid_y, height):
        half_width = ramp_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slope = np.linspace(0, height, num=x2-x1)
        slope = slope[:, np.newaxis]
        height_field[x1:x2, y1:y2] = slope

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    for i in range(4):
        dx = np.random.randint(m_to_idx(-0.1), m_to_idx(0.1))
        dy = np.random.randint(m_to_idx(-0.4), m_to_idx(0.4))

        if i % 2 == 0:
            # Adding a ramp
            ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
            add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, ramp_height)
            goals[i+1] = [cur_x + (platform_length + dx) // 2, mid_y + dy]
        else:
            # Adding a platform
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i+1] = [cur_x + (platform_length + dx) // 2, mid_y + dy]

        cur_x += platform_length + dx + gap_length

    # Final addition of alternating pattern to finish off
    for i in range(4, 7):
        dx = np.random.randint(m_to_idx(-0.1), m_to_idx(0.1))
        dy = np.random.randint(m_to_idx(-0.4), m_to_idx(0.4))
        
        if i % 2 == 0:
            platform_height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        else:
            ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
            add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, ramp_height)
            goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        cur_x += platform_length + dx + gap_length

    # Add final goal behind the last obstacle and fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_33(length, width, field_resolution, difficulty):
    """Series of staggered, raised platforms with varying heights and gaps for the robot to jump across and navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions
    platform_length = 1.0 + 0.4 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 0.8 + 0.2 * difficulty  # Slightly increase platform width
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.2 * difficulty, 0.1 + 0.3 * difficulty
    gap_length = 0.3 + 0.2 * difficulty
    gap_length = m_to_idx(gap_length)
    
    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_gap(start_x, end_x):
        height_field[start_x:end_x, :] = -1.0  # Set a pit for the gap

    dx_min, dx_max = -m_to_idx(0.2), m_to_idx(0.2)
    dy_min, dy_max = -m_to_idx(0.2), m_to_idx(0.2)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Set remaining area to be a pit
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    for i in range(6):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height)
        
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        cur_x += platform_length + dx
        add_gap(cur_x, cur_x + gap_length)
        cur_x += gap_length
    
    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_34(length, width, field_resolution, difficulty):
    """Challenging mix of narrow beams, staggered platforms, and angled ramps for testing balance and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up obstacle dimensions
    beam_length = 1.0 - 0.2 * difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = np.random.uniform(0.4, 0.5)  # Narrow beams
    beam_width = m_to_idx(beam_width)
    platform_length = 1.2 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.6, 0.7)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 * difficulty, 0.4 * difficulty
    ramp_height_min, ramp_height_max = 0.2 * difficulty, 0.5 * difficulty
    gap_length = 0.2 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, y_mid):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = y_mid - half_width, y_mid + half_width
        beam_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = beam_height

    def add_platform(start_x, end_x, y_mid):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = y_mid - half_width, y_mid + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_ramp(start_x, end_x, y_mid, height_start, height_end):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = y_mid - half_width, y_mid + half_width
        for x in range(x1, x2):
            height_field[x, y1:y2] = np.linspace(height_start, height_end, num=x2 - x1)[x - x1]

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Start the pattern of beam -> platform -> ramp
    cur_x = spawn_length
    for i in range(2):
        # Add a beam
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_beam(cur_x, cur_x + beam_length + dx, mid_y + dy)
        goals[i * 3 + 1] = [cur_x + (beam_length + dx) / 2, mid_y + dy]
        cur_x += beam_length + dx + gap_length
        
        # Add a platform
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
        goals[i * 3 + 2] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

        # Add a ramp
        height_start = np.random.uniform(ramp_height_min, ramp_height_max)
        height_end = np.random.uniform(ramp_height_min, ramp_height_max)
        add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, height_start, height_end)
        goals[i * 3 + 3] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

    # Add final goal behind the last obstacle
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_35(length, width, field_resolution, difficulty):
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

def set_terrain_36(length, width, field_resolution, difficulty):
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

def set_terrain_37(length, width, field_resolution, difficulty):
    """Urban-like terrain with steps, slopes, and narrow passages."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Conversion helpers
    len_idx = m_to_idx(length)
    wid_idx = m_to_idx(width)
    quad_length, quad_width = 0.645, 0.28

    mid_y = wid_idx // 2

    # Obstacle settings
    step_height = 0.1 + difficulty * 0.2
    max_slope_height = 0.05 + difficulty * 0.3
    narrow_width = quad_width + (0.4 + 0.2 * difficulty)

    def add_step(start_x, end_x, mid_y, step_h):
        half_width = m_to_idx(1.0) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = step_h

    def add_slope(start_x, end_x, start_h, end_h, mid_y):
        half_width = m_to_idx(1.0) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slope = np.linspace(start_h, end_h, x2 - x1)
        height_field[x1:x2, y1:y2] = slope[:, np.newaxis]

    def add_narrow_passage(start_x, end_x, mid_y, step_h):
        half_width = m_to_idx(narrow_width) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = step_h

    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    # Place the first step
    add_step(cur_x, cur_x + m_to_idx(2), mid_y, step_height)
    goals[1] = [cur_x + m_to_idx(1), mid_y]
    cur_x += m_to_idx(2)

    # Place a slope
    add_slope(cur_x, cur_x + m_to_idx(3), step_height, max_slope_height, mid_y)
    goals[2] = [cur_x + m_to_idx(1.5), mid_y]
    cur_x += m_to_idx(3)

    # Place a narrow passage
    add_narrow_passage(cur_x, cur_x + m_to_idx(2), mid_y, max_slope_height)
    goals[3] = [cur_x + m_to_idx(1), mid_y]
    cur_x += m_to_idx(2)

    # Place a downward slope
    add_slope(cur_x, cur_x + m_to_idx(3), max_slope_height, step_height, mid_y)
    goals[4] = [cur_x + m_to_idx(1.5), mid_y]
    cur_x += m_to_idx(3)

    # Place another step
    add_step(cur_x, cur_x + m_to_idx(2), mid_y, step_height)
    goals[5] = [cur_x + m_to_idx(1), mid_y]
    cur_x += m_to_idx(2)

    # Final slope to ground level
    add_slope(cur_x, cur_x + m_to_idx(3), step_height, 0.0, mid_y)
    goals[6] = [cur_x + m_to_idx(1.5), mid_y]
    cur_x += m_to_idx(3)

    goals[7] = [cur_x + m_to_idx(0.5), mid_y]

    return height_field, goals

def set_terrain_38(length, width, field_resolution, difficulty):
    """Complex terrain with varied ramps and platforms to test advanced agility and precise movements."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and ramp dimensions
    platform_length = 0.8 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.5, 0.8)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.15 + 0.3 * difficulty
    ramp_height_min, ramp_height_max = 0.2 + 0.3 * difficulty, 0.25 + 0.4 * difficulty
    gap_length = 0.2 + 0.5 * difficulty
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
        slant = np.linspace(0, ramp_height, num=x2-x1)[::direction]
        slant = slant[:, None]  # Add a dimension for broadcasting to y
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.5, 0.5
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Add varied platforms and ramps, introduce complexity
    cur_x = spawn_length
    for i in range(6):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        obstacle_type = np.random.choice(['platform', 'ramp'])
        direction = np.random.choice([-1, 1])

        if obstacle_type == 'platform':
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        else:
            add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, direction)
            goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        
        # Add gap
        cur_x += platform_length + dx + gap_length
    
    # Add final goal behind the last obstacle, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_39(length, width, field_resolution, difficulty):
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

# INSERT TERRAIN FUNCTION DEFINITIONS HERE
