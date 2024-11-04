
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

def set_terrain_3(length, width, field_resolution, difficulty):
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

def set_terrain_4(length, width, field_resolution, difficulty):
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

def set_terrain_5(length, width, field_resolution, difficulty):
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


def set_terrain_6(length, width, field_resolution, difficulty):
    """Narrow beams and wide gaps for the robot to balance and jump across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up beam and gap dimensions
    beam_width = 0.4 + 0.4 * difficulty  # 0.4 to 0.8 meters wide beams
    beam_width = m_to_idx(beam_width)
    beam_height = 0.1 + 0.3 * difficulty  # 0.1 to 0.4 meters tall beams
    gap_length_min = 0.5
    gap_length_max = 2 + 2 * difficulty  # 0.5 to 4 meters wide gaps
    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, mid_y):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = beam_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    for i in range(6):  # Set up 6 beams and gaps
        gap_length = np.random.uniform(gap_length_min, gap_length_max)
        gap_length = m_to_idx(gap_length)
        
        add_beam(cur_x, cur_x + m_to_idx(1), mid_y)  # Beam with 1 meter length

        # Put goal at the center of the beam
        goals[i+1] = [cur_x + m_to_idx(0.5), mid_y]

        # Add gap
        cur_x += m_to_idx(1) + gap_length
    
    # Add final goal behind the last beam, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_7(length, width, field_resolution, difficulty):
    """Irregularly spaced stepping stones of varying heights and widths for balance and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Parameters for stepping stones
    stone_min_width = 0.4
    stone_max_width = 1.2 - 0.6 * difficulty
    stone_min_height = 0.1
    stone_max_height = 0.3 + 0.3 * difficulty
    gap_min_length = 0.2
    gap_max_length = 0.6 + 0.4 * difficulty

    def add_stepping_stone(start_x, start_y, stone_width, stone_height):
        x1, x2 = int(start_x), int(start_x + stone_width)
        y1, y2 = int(start_y - stone_width / 2), int(start_y + stone_width / 2)
        height_field[x1:x2, y1:y2] = stone_height

    # Set spawn area to be flat ground
    spawn_area_length = m_to_idx(2)
    height_field[:spawn_area_length, :] = 0
    mid_y = m_to_idx(width) // 2

    # Initial goal at the spawn area
    goals[0] = [spawn_area_length - m_to_idx(0.5), mid_y]
    
    # Generate stepping stones
    current_x = spawn_area_length
    for i in range(7):
        stone_width = m_to_idx(random.uniform(stone_min_width, stone_max_width))
        stone_height = random.uniform(stone_min_height, stone_max_height)
        gap_length = m_to_idx(random.uniform(gap_min_length, gap_max_length))

        ypos_variation = m_to_idx(np.random.uniform(-0.8, 0.8) * difficulty)
        
        add_stepping_stone(current_x, mid_y + ypos_variation, stone_width, stone_height)
        
        # Center of each stone is the goal position
        goals[i + 1] = [current_x + stone_width / 2, mid_y + ypos_variation]

        # Move to the next position
        current_x += stone_width + gap_length

    return height_field, goals

def set_terrain_8(length, width, field_resolution, difficulty):
    """Series of steps and narrow beams for the robot to navigate, testing balance and precise movements."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set dimensions for steps and beams
    step_height_min = 0.05
    step_height_max = 0.4 * difficulty + 0.1
    step_length = m_to_idx(0.5)
    step_width = m_to_idx(1.0)

    beam_height = 0.3 * difficulty + 0.05
    beam_length = m_to_idx(1.5)
    beam_width = m_to_idx(0.4)  # Narrow beam

    mid_y = m_to_idx(width) // 2

    def add_step(start_x, end_x, mid_y, height):
        y1, y2 = mid_y - step_width // 2, mid_y + step_width // 2
        height_field[start_x:end_x, y1:y2] = height

    def add_beam(start_x, end_x, mid_y, height):
        y1, y2 = mid_y - beam_width // 2, mid_y + beam_width // 2
        height_field[start_x:end_x, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at spawn area

    # Variables to keep track of x position and current goal index
    cur_x = spawn_length
    goal_index = 1

    for i in range(4):  # Create 4 steps
        step_height = np.random.uniform(step_height_min, step_height_max)
        add_step(cur_x, cur_x + step_length, mid_y, step_height)
        goals[goal_index] = [cur_x + step_length // 2, mid_y]
        cur_x += step_length
        goal_index += 1

    cur_x += m_to_idx(1.0)  # Small gap between steps and beams

    for i in range(3):  # Create 3 narrow beams
        add_beam(cur_x, cur_x + beam_length, mid_y, beam_height)
        goals[goal_index] = [cur_x + beam_length // 2, mid_y]
        cur_x += beam_length
        goal_index += 1
    
    # Add final goal behind the last beam
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    return height_field, goals

def set_terrain_9(length, width, field_resolution, difficulty):
    """A series of narrow and wide ramps to test the robot's balance and climbing skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set dimensions for ramps and gaps
    ramp_length_min, ramp_length_max = 0.8, 1.2
    ramp_width_min, ramp_width_max = 0.4, 1.6
    ramp_height_min, ramp_height_max = 0.05, 0.25

    gap_length = 0.1 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_ramp(start_x, ramp_length, ramp_width, height):
        half_width = ramp_width // 2
        x1, x2 = start_x, start_x + ramp_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(6):  # Set up 6 ramps
        ramp_length = np.random.uniform(ramp_length_min, ramp_length_max) - (0.2 * difficulty)
        ramp_length = m_to_idx(ramp_length)
        ramp_width = np.random.uniform(ramp_width_min, ramp_width_max) - (0.3 * difficulty)
        ramp_width = m_to_idx(ramp_width)
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max) * difficulty
        
        add_ramp(cur_x, ramp_length, ramp_width, ramp_height)

        # Set goal in the center of the ramp
        goals[i+1] = [cur_x + ramp_length // 2, mid_y]

        # Add gap
        cur_x += ramp_length + gap_length

    # Add final goal behind the last ramp, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

# INSERT TERRAIN FUNCTION DEFINITIONS HERE