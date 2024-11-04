
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

def set_terrain_1(length, width, field_resolution, difficulty):
    """Narrow bridges and sharp turns for the robot to navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Basic obstacle sizes and properties
    bridge_width = max(0.4, 0.8 * (1 - difficulty))  # Bridge width decreases with difficulty
    bridge_width = m_to_idx(bridge_width)
    bridge_length_min = 2.0
    bridge_length_max = 3.0
    bridge_length_min = m_to_idx(bridge_length_min)
    bridge_length_max = m_to_idx(bridge_length_max)
    bridge_height = 0.05 + 0.25 * difficulty  # Increase height with difficulty
    pit_depth = -1.0  # Depth of the pit around bridges
  
    spawn_x_idx = m_to_idx(2)
    height_field[0:spawn_x_idx, :] = 0  # Spawn area flat ground
    mid_y_idx = m_to_idx(width / 2)

    # Set the initial goal at spawn area
    goals[0] = [spawn_x_idx - m_to_idx(0.5), mid_y_idx]

    def add_bridge(start_x_idx, start_y_idx, length):
        half_width = bridge_width // 2
        x1, x2 = start_x_idx, start_x_idx + length
        y1, y2 = start_y_idx - half_width, start_y_idx + half_width
        height_field[x1:x2, y1:y2] = bridge_height

    cur_x = spawn_x_idx

    for i in range(7):  # Set up 7 bridges
        bridge_length = np.random.randint(bridge_length_min, bridge_length_max)
        offset_y = np.random.uniform(-1.0, 1.0)
        offset_y = m_to_idx(offset_y)
        
        add_bridge(cur_x, mid_y_idx + offset_y, bridge_length)
        goals[i+1] = [cur_x + bridge_length // 2, mid_y_idx + offset_y]  # Goal in the center of the bridge

        # Add space (pit) before the next bridge
        pit_length = np.random.uniform(0.4, 0.6)
        pit_length = m_to_idx(pit_length)
        cur_x += bridge_length + pit_length

    # Fill in the remaining area after the last bridge with flat ground
    height_field[cur_x:, :] = 0
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y_idx]  # Final goal just after last bridge

    return height_field, goals

def set_terrain_2(length, width, field_resolution, difficulty):
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

def set_terrain_3(length, width, field_resolution, difficulty):
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

def set_terrain_4(length, width, field_resolution, difficulty):
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

def set_terrain_5(length, width, field_resolution, difficulty):
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

def set_terrain_6(length, width, field_resolution, difficulty):
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

def set_terrain_7(length, width, field_resolution, difficulty):
    """Narrow passageways and raised walkways to test precision and careful navigation."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]
    
    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Configure parameters based on difficulty
    path_width = 0.4 + (0.6 * (1 - difficulty))  # Path width between 0.4m and 1m
    passage_height = 0.05 + (0.3 * difficulty)  # Passage height between 0.05m and 0.35m
    walkway_height = 0.1 + (0.3 * difficulty)  # Walkway height between 0.1m and 0.4m
    section_length = 1.0 + (1.0 * difficulty)  # Varying section lengths, longer with higher difficulty

    path_width = m_to_idx(path_width)
    passage_height = np.random.uniform(passage_height, passage_height + 0.1 * difficulty)
    walkway_height = np.random.uniform(walkway_height, walkway_height + 0.1 * difficulty)
    section_length = m_to_idx(section_length)

    # Initial flat ground area for spawn point
    spawn_area = m_to_idx(2)
    height_field[:spawn_area, :] = 0
    mid_y = m_to_idx(width) // 2
    goals[0] = [spawn_area - m_to_idx(0.5), mid_y]

    cur_x = spawn_area

    def add_narrow_passage(start_x, length, height, center_y):
        half_width = path_width // 2
        x_start, x_end = start_x, start_x + length
        y_start, y_end = center_y - half_width, center_y + half_width
        height_field[x_start:x_end, y_start:y_end] = height

    # Create a sequence of narrow passages and raised walkways
    for i in range(7):
        if i % 2 == 0:
            # Add narrow passage
            add_narrow_passage(cur_x, section_length, passage_height, mid_y)
            goals[i+1] = [cur_x + section_length / 2, mid_y]
        else:
            # Add raised walkway
            height_field[cur_x:cur_x + section_length, :] = walkway_height
            goals[i+1] = [cur_x + section_length / 2, mid_y]

        cur_x += section_length

    # Final goal at the end of the course
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    return height_field, goals

def set_terrain_8(length, width, field_resolution, difficulty):
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

def set_terrain_9(length, width, field_resolution, difficulty):
    """Multi-skill course featuring small ramps, jumps, and a final narrow bridge."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    mid_y = m_to_idx(width / 2)

    def add_ramp(start_x, end_x, mid_y, start_height, end_height):
        """Add a ramp to the height field."""
        for x in range(start_x, end_x):
            height_value = start_height + ((end_height - start_height) * (x - start_x) / (end_x - start_x))
            height_field[x, mid_y- m_to_idx(0.5): mid_y + m_to_idx(0.5)] = height_value

    def add_jump(start_x, mid_y, height, length, width):
        """Add a platform to jump onto."""
        x1, x2 = start_x, start_x + length
        y1, y2 = mid_y - width//2, mid_y + width//2
        height_field[x1:x2, y1:y2] = height

    def add_narrow_bridge(start_x, end_x, mid_y, width):
        """Add a narrow bridge towards the end of the course."""
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - width//2, mid_y + width//2
        height_field[x1:x2, y1:y2] = 0.5

    # Set up levels and parameters
    ramp_height = 0.2 + 0.3 * difficulty
    platform_height = 0.4 + 0.3 * difficulty
    gap_length = m_to_idx(0.4)
    narrow_bridge_width = m_to_idx(0.4)

    # Clear spawn area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    # Add series of ramps and platforms
    for i in range(3):
        ramp_length = m_to_idx(1.0 + 0.5 * difficulty)
        add_ramp(cur_x, cur_x + ramp_length, mid_y, 0, ramp_height)
        goals[i+1] = [cur_x + ramp_length//2, mid_y]
        
        cur_x += ramp_length + gap_length
        
        platform_length = m_to_idx(1.0)
        add_jump(cur_x, mid_y, platform_height, platform_length, m_to_idx(1.0))
        goals[i+2] = [cur_x + platform_length//2, mid_y]
        
        cur_x += platform_length + gap_length

    # Add a final narrow bridge
    bridge_length = m_to_idx(2.0)
    add_narrow_bridge(cur_x, cur_x + bridge_length, mid_y, narrow_bridge_width)
    goals[6] = [cur_x + bridge_length//2, mid_y]

    cur_x += bridge_length
    
    # Set final goal
    goals[7] = [cur_x + m_to_idx(0.5), mid_y]

    #Ensure remaining area is flat
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_10(length, width, field_resolution, difficulty):
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

def set_terrain_11(length, width, field_resolution, difficulty):
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

def set_terrain_12(length, width, field_resolution, difficulty):
    """Series of staggered stairs for the quadruped to climb up and down."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Convert terrain dimensions to grid indices
    terrain_length = m_to_idx(length)
    terrain_width = m_to_idx(width)

    # Quadruped's center starting point
    start_x = m_to_idx(2)
    start_y = terrain_width // 2
    
    # Initial goal at start position
    goals[0] = [start_x - m_to_idx(0.5), start_y]

    # Define stair dimensions based on difficulty
    stair_width = 1.0 - 0.3 * difficulty  # decrease with difficulty
    stair_width = m_to_idx(stair_width)

    stair_height_min = 0.1 * difficulty  # increase with difficulty
    stair_height_max = 0.3 * difficulty  # increase with difficulty
    stair_length = 1.2  # fixed length of 1.2 meters
    stair_length = m_to_idx(stair_length)
    
    cur_x = start_x

    def add_stair(x, y, width, length, height):
        """Add a stair with given dimensions to the height_field."""
        half_width = width // 2
        x1, x2 = x, x + length
        y1, y2 = y - half_width, y + half_width
        height_field[x1:x2, y1:y2] += height

    for i in range(7):  # 7 sets of stairs
        stair_height = np.random.uniform(stair_height_min, stair_height_max)
        add_stair(cur_x, start_y, stair_width, stair_length, stair_height)

        # Place the goal in the center of the stair
        goals[i + 1] = [cur_x + stair_length // 2, start_y]

        # Move to the next stair position
        cur_x += stair_length

        # Adding a small gap with random width between stairs for added difficulty
        gap = np.random.uniform(0.1, 0.4) * difficulty
        gap = m_to_idx(gap)
        cur_x += gap

    # Final goal at the end of the terrain
    goals[-1] = [cur_x + m_to_idx(0.5), start_y]

    return height_field, goals

def set_terrain_13(length, width, field_resolution, difficulty):
    """Stepping stones obstacle course testing the quadruped's precision and agility."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up step dimensions
    step_size = 0.3  # Each stone has a diameter of approximately 0.3 meters
    step_size_idx = m_to_idx(step_size)
    gap_min = 0.4  # Minimum gap between steps
    gap_max = 0.8  # Maximum gap between steps
    gap_min_idx = m_to_idx(gap_min)
    gap_max_idx = m_to_idx(gap_max)
    step_height_min, step_height_max = 0.1, 0.4  # Height range for steps
    step_height_min += 0.1 * difficulty
    step_height_max += 0.3 * difficulty

    mid_y = m_to_idx(width // 2)

    def add_step(x, y):
        """Adds a stepping stone at the specified (x, y) location."""
        radius = step_size_idx // 2
        step_height = np.random.uniform(step_height_min, step_height_max)
        height_field[x - radius:x + radius, y - radius:y + radius] = step_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # Place the first goal right at the spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    cur_y = mid_y

    for i in range(7):  # Set up 7 stepping stones
        add_step(cur_x, cur_y)

        # Update the goal to the center of the current step
        goals[i+1] = [cur_x, cur_y]

        # Move to the next position for the next step
        gap_x = np.random.randint(gap_min_idx, gap_max_idx)
        cur_x += gap_x

        # Slightly randomize the y position for the next step
        dy = np.random.uniform(-gap_max / 2, gap_max / 2)
        cur_y = np.clip(cur_y + m_to_idx(dy), step_size_idx, m_to_idx(width) - step_size_idx)
    
    # Ensure the last goal is reachable and set on flat ground
    goals[-1] = [cur_x + gap_min_idx, mid_y]
    height_field[cur_x + gap_min_idx:, :] = 0

    return height_field, goals

def set_terrain_14(length, width, field_resolution, difficulty):
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

def set_terrain_15(length, width, field_resolution, difficulty):
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

def set_terrain_16(length, width, field_resolution, difficulty):
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

def set_terrain_17(length, width, field_resolution, difficulty):
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

def set_terrain_18(length, width, field_resolution, difficulty):
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

def set_terrain_19(length, width, field_resolution, difficulty):
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

def set_terrain_20(length, width, field_resolution, difficulty):
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

def set_terrain_21(length, width, field_resolution, difficulty):
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

def set_terrain_22(length, width, field_resolution, difficulty):
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

def set_terrain_23(length, width, field_resolution, difficulty):
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

def set_terrain_24(length, width, field_resolution, difficulty):
    """Narrow passages with varying heights for the robot to maneuver on."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define beam characteristics
    beam_length = m_to_idx(0.4 + 0.2 * difficulty)  # Varies from 0.4m to 0.6m depending on difficulty
    beam_width = m_to_idx(0.4)  # Constant width

    # Heights will have more variation with increased difficulty
    min_height = 0.05 * difficulty
    max_height = 0.2 + 0.3 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_beam(x, y_center):
        y1 = y_center - beam_width // 2
        y2 = y_center + beam_width // 2
        beam_height = np.random.uniform(min_height, max_height)
        height_field[x:x + beam_length, y1:y2] = beam_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [m_to_idx(1), mid_y]  # First goal at the spawn area

    cur_x = spawn_length
    dx_range = m_to_idx([-0.1, 0.1])  # Small variation in x direction
    dy_range = m_to_idx([-0.5 + 0.3 * difficulty, 0.5 - 0.3 * difficulty])  # Larger variation in y direction for difficulty

    for i in range(7):  # Set up 7 beams
        dx = np.random.randint(dx_range[0], dx_range[1])
        dy = np.random.randint(dy_range[0], dy_range[1])
        add_beam(cur_x + dx, mid_y + dy)

        # Place goal within each beam
        goals[i+1] = [cur_x + dx + beam_length // 2, mid_y + dy]

        # Pass to the next beam
        cur_x += beam_length + dx

    return height_field, goals

def set_terrain_25(length, width, field_resolution, difficulty):
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
    """Narrow beams and larger platforms for balance and transition skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Terrain dimensions and parameters
    mid_y = m_to_idx(width) // 2
    beam_height_min, beam_height_max = 0.05, 0.4 * difficulty
    beam_width = m_to_idx(0.2)  # Narrow beam, 0.2 meters
    platform_width = m_to_idx(1.2)  # Broad platform, 1.2 meters
    platform_length = m_to_idx(1.0 - 0.3 * difficulty)
    gap_length = m_to_idx(0.5 + 0.5 * difficulty)

    def add_beam(start_x, end_x, mid_y):
        """Add a narrow beam to the terrain."""
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        beam_height = np.random.uniform(beam_height_min, beam_height_max)
        height_field[x1:x2, y1:y2] = beam_height

    def add_platform(start_x, end_x, mid_y):
        """Add a broad platform to the terrain."""
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(beam_height_min, beam_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    cur_x = m_to_idx(2)
    height_field[:cur_x, :] = 0
    goals[0] = [cur_x / 2, mid_y]

    def add_goal(i, cur_x, length, mid_y):
        """Add a goal at the center of the current surface."""
        goals[i] = [cur_x + length // 2, mid_y]

    # Place obstacles and goals
    for i in range(7):
        if i % 2 == 0:  # Add a narrow beam
            beam_length = platform_length if i == 0 else platform_length - m_to_idx(0.2)
            add_beam(cur_x, cur_x + beam_length, mid_y)
            add_goal(i + 1, cur_x, beam_length, mid_y)
            cur_x += beam_length + gap_length
        else:  # Add a broad platform
            add_platform(cur_x, cur_x + platform_length, mid_y)
            add_goal(i + 1, cur_x, platform_length, mid_y)
            cur_x += platform_length + gap_length

    goals[-1] = [cur_x - gap_length / 2, mid_y]
    
    # Final area should be flat
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_28(length, width, field_resolution, difficulty):
    """A series of varying steps to test the robot's climbing and descending capabilities."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Step characteristics
    step_heights = [0.05, 0.1, 0.15, 0.2]  # Heights in meters 
    step_width_range = (1.0, 1.6)  # Range of step widths in meters
    step_length = 0.4  # Length of each step in meters

    step_length = m_to_idx(step_length)
    step_width_min, step_width_max = m_to_idx(step_width_range[0]), m_to_idx(step_width_range[1])
    mid_y = m_to_idx(width) // 2

    def add_step(start_x, start_y, step_height, step_width):
        x2 = start_x + step_length
        y1 = start_y - step_width // 2
        y2 = start_y + step_width // 2
        height_field[start_x:x2, y1:y2] = step_height

    # Setting initial flat area for spawn
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(7):  # Create 7 steps
        step_height = random.choice(step_heights) * difficulty
        step_width = random.randint(step_width_min, step_width_max)
        
        add_step(cur_x, mid_y, step_height, step_width)
        
        # Place goal at the top of each step
        goals[i + 1] = [cur_x + step_length // 2, mid_y]

        cur_x += step_length

    # Set the height at the end to zero (flat ground)
    height_field[cur_x:, :] = 0
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

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
    """Stepping stones across a stream for the robot to jump and balance on."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up stepping stone dimensions
    stone_diameter_min = 0.4  # minimum diameter of stepping stones
    stone_diameter_max = 0.8  # maximum diameter of stepping stones
    stone_height_min, stone_height_max = 0.1 + 0.1 * difficulty, 0.15 + 0.25 * difficulty
    gap_length_min = 0.3  # minimum gap between stepping stones
    gap_length_max = 0.7 + 0.3 * difficulty  # maximum gap increases with difficulty

    def add_stepping_stone(center_x, center_y):
        radius = np.random.uniform(stone_diameter_min / 2, stone_diameter_max / 2)
        radius_idx = m_to_idx(radius)
        stone_height = np.random.uniform(stone_height_min, stone_height_max)

        x, y = m_to_idx(center_x), m_to_idx(center_y)
        for i in range(-radius_idx, radius_idx + 1):
            for j in range(-radius_idx, radius_idx + 1):
                if i**2 + j**2 <= radius_idx**2:
                    height_field[x + i, y + j] = stone_height

    spawn_length = m_to_idx(2)
    mid_y = m_to_idx(width / 2)

    # Set spawn area to flat ground
    height_field[0:spawn_length, :] = 0
    # Put the first goal at spawn area
    goals[0] = [m_to_idx(1), mid_y]

    cur_x = 2.0
    for i in range(1, 8):  # Set up 7 stepping stones
        stone_center_y = width / 2 + np.random.uniform(-width / 4, width / 4)
        stone_center_x = cur_x + np.random.uniform(gap_length_min, gap_length_max)
        add_stepping_stone(stone_center_x, stone_center_y)

        # Place goal on the current stepping stone
        goals[i] = [m_to_idx(stone_center_x), m_to_idx(stone_center_y)]
        
        # Update current x position for the next stone
        cur_x = stone_center_x

    return height_field, goals

def set_terrain_31(length, width, field_resolution, difficulty):
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

def set_terrain_32(length, width, field_resolution, difficulty):
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

def set_terrain_33(length, width, field_resolution, difficulty):
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

def set_terrain_34(length, width, field_resolution, difficulty):
    """Series of narrow beams for the robot to carefully navigate across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up beam dimensions
    beam_length = 2.0 - difficulty  # Beams get shorter with higher difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = 0.4 + 0.2 * difficulty  # The width of the beams, keeping it between 0.4m and 0.6m
    beam_width = m_to_idx(beam_width)
    beam_height = 0.2 + 0.3 * difficulty  # The height of the beams, increasing with difficulty
    gap_length = 0.4 + 0.6 * difficulty  # Gaps between beams

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, mid_y):
        y_half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - y_half_width, mid_y + y_half_width
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
        goals[i+1] = [cur_x + (beam_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += beam_length + dx + m_to_idx(gap_length)

    # Add final goal behind the last beam, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_35(length, width, field_resolution, difficulty):
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

def set_terrain_36(length, width, field_resolution, difficulty):
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

def set_terrain_37(length, width, field_resolution, difficulty):
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

def set_terrain_38(length, width, field_resolution, difficulty):
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
