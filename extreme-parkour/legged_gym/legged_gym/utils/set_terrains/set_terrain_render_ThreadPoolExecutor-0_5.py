
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
    """Combination of narrow beams, stepping stones, and small ramps for balanced testing of agility and balancing skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Dimensions of obstacles
    beam_width = 0.2 - 0.1 * difficulty
    beam_width = m_to_idx(beam_width)
    beam_height = 0.2 + 0.2 * difficulty
    step_height_min, step_height_max = 0.05 + 0.1 * difficulty, 0.15 + 0.25 * difficulty
    platform_length = 0.8 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    gap_length_min, gap_length_max = 0.1, 0.4
    gap_length_min, gap_length_max = m_to_idx(gap_length_min), m_to_idx(gap_length_max)

    mid_y = m_to_idx(width / 2)

    def add_narrow_beam(start_x, end_x, mid_y):
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - beam_width // 2, mid_y + beam_width // 2
        height_field[x1:x2, y1:y2] = beam_height

    def add_step(start_x, step_height, mid_y, mid_y_offset):
        step_length = platform_length // 3
        x1, x2 = start_x, start_x + step_length
        y1, y2 = mid_y - mid_y_offset, mid_y + mid_y_offset
        height_field[x1:x2, y1:y2] = step_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Add first obstacle: a narrow beam
    cur_x = spawn_length
    beam_length = m_to_idx(1.0 + 0.3 * difficulty)
    add_narrow_beam(cur_x, cur_x + beam_length, mid_y)
    cur_x += beam_length + gap_length_min
    goals[1] = [cur_x - 0.5 * gap_length_min, mid_y]

    # Add second obstacle: stepping stones
    for i in range(2, 5):
        step_height = np.random.uniform(step_height_min, step_height_max)
        mid_y_offset = np.random.randint(-m_to_idx(0.1), m_to_idx(0.1))
        add_step(cur_x, step_height, mid_y, mid_y_offset)
        cur_x += platform_length // 3
        gap = np.random.randint(gap_length_min, gap_length_max)
        goals[i] = [cur_x - gap // 2, mid_y]
        cur_x += gap

    # Add third obstacle: a small ramp
    ramp_width = m_to_idx(0.4)
    ramp_height_min, ramp_height_max = 0.1 + 0.2 * difficulty, 0.3 + 0.4 * difficulty
    ramp_length = m_to_idx(1.2)
    x1, x2 = cur_x, cur_x + ramp_length
    y1, y2 = mid_y - ramp_width // 2, mid_y + ramp_width // 2
    height_field[x1:x2, y1:y2] = np.linspace(0, np.random.uniform(ramp_height_min, ramp_height_max), num=ramp_length)[:, None]
    cur_x += ramp_length + gap_length_min
    goals[5] = [cur_x - 0.5 * gap_length_min, mid_y]

    # Final obstacles: platforms and narrow beams for precision movement
    for i in range(5, 7):
        add_narrow_beam(cur_x, cur_x + beam_length, mid_y)
        cur_x += beam_length + gap_length_max
        goals[i] = [cur_x - 0.5 * gap_length_max, mid_y]

    # Add final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_1(length, width, field_resolution, difficulty):
    """Narrow elevated walkways with gaps and hurdles testing balance and precision stepping."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Walkway settings based on difficulty
    walkway_width_min = 0.4
    walkway_width_max = 1.0 - (0.5 * difficulty)
    walkway_height_min = 0.2 + (0.2 * difficulty)
    walkway_height_max = 0.4 + (0.4 * difficulty)
    gap_length_min = 0.2
    gap_length_max = 1.0
    hurdle_height_min = 0.05
    hurdle_height_max = 0.15 + (0.35 * difficulty)

    mid_y = m_to_idx(width) // 2

    def add_walkway(start_x, end_x, height, width):
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_hurdle(start_x, width, height):
        half_width = width // 2
        x1, x2 = start_x, start_x + m_to_idx(0.1)  # small hurdle thickness
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0  # flat spawn area with height 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # first goal at the end of spawn area

    cur_x = spawn_length
    
    for i in range(6):
        # Walkway dimensions
        walkway_length = np.random.uniform(1.0, 1.5)
        walkway_width = np.random.uniform(walkway_width_min, walkway_width_max)
        walkway_height = np.random.uniform(walkway_height_min, walkway_height_max)

        # Convert to indices
        walkway_length_idx = m_to_idx(walkway_length)
        walkway_width_idx = m_to_idx(walkway_width)

        # Add the walkway
        add_walkway(cur_x, cur_x + walkway_length_idx, walkway_height, walkway_width_idx)

        # Place goal in center of walkway
        goals[i + 1] = [cur_x + walkway_length_idx // 2, mid_y]

        # Add hurdles on the walkway
        num_hurdles = np.random.randint(1, 3)
        for _ in range(num_hurdles):
            hurdle_position = np.random.uniform(cur_x + m_to_idx(0.2), cur_x + walkway_length_idx - m_to_idx(0.2))
            hurdle_position_idx = m_to_idx(hurdle_position)
            hurdle_height = np.random.uniform(hurdle_height_min, hurdle_height_max)
            add_hurdle(hurdle_position_idx, walkway_width_idx, hurdle_height)

        # Move to the next section (gap)
        cur_x += walkway_length_idx
        gap_length = np.random.uniform(gap_length_min, gap_length_max)
        cur_x += m_to_idx(gap_length)

    # Final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    
    return height_field, goals

def set_terrain_2(length, width, field_resolution, difficulty):
    """Simplified platforms and gaps for easier navigation and jumping."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions
    platform_length = 1.0 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 1.0 + 0.2 * difficulty
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.1 * difficulty, 0.1 + 0.2 * difficulty
    gap_length = 0.1 + 0.3 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, start_y):
        half_width = platform_width // 2
        x1, x2 = start_x, start_x + platform_length
        y1, y2 = start_y - half_width, start_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    dx_min, dx_max = m_to_idx(-0.1), m_to_idx(0.1)
    dy_min, dy_max = m_to_idx(-0.2), m_to_idx(0.2)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Set the initial platform
    cur_x = spawn_length
    add_platform(cur_x, mid_y)
    # Place the first platform goal
    goals[1] = [cur_x + platform_length // 2, mid_y]
    cur_x += platform_length + gap_length

    for i in range(2, 7):  # Set up 5 more platforms
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x + dx, mid_y + dy)
        # Place the goal on the new platform
        goals[i] = [cur_x + dx + platform_length // 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

    # Add the final goal after the last platform, fill in remaining gap
    height_field[cur_x:, :] = 0
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    return height_field, goals

def set_terrain_3(length, width, field_resolution, difficulty):
    """Challenging course with inclined platforms and narrow stepping stones to enhance climbing and balancing skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length = 1.2 - 0.4 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.4)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 * difficulty, 0.4
    step_stone_width = 0.5
    step_stone_width = m_to_idx(step_stone_width)
    step_stone_height_min, step_stone_height_max = 0.05, 0.2 * difficulty
    gap_length = 0.2 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)
    mid_y = m_to_idx(width) // 2

    def add_inclined_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        slant = np.linspace(0, platform_height, num=x2-x1).reshape(-1, 1)
        height_field[x1:x2, y1:y2] = slant

    def add_stepping_stone(center_x, center_y):
        half_width = step_stone_width // 2
        x1, x2 = center_x - half_width, center_x + half_width
        y1, y2 = center_y - half_width, center_y + half_width
        stepping_stone_height = np.random.uniform(step_stone_height_min, step_stone_height_max)
        height_field[x1:x2, y1:y2] = stepping_stone_height
    
    dx_min, dx_max = -0.1, 0.3
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.0, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)
    
    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at spawn point

    cur_x = spawn_length

    # First Inclined Platform
    dx = np.random.randint(dx_min, dx_max)
    add_inclined_platform(cur_x, cur_x + platform_length + dx, mid_y)
    goals[1] = [cur_x + (platform_length + dx) / 2, mid_y]
    cur_x += platform_length + dx + gap_length

    # Add alternating obstacles
    for i in range(2, 7):
        if i % 2 == 0:
            # Inclined Platform
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)
            add_inclined_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
            cur_x += platform_length + dx + gap_length
        else:
            # Stepping Stone
            add_stepping_stone(cur_x + step_stone_width, mid_y)
            goals[i] = [cur_x + step_stone_width, mid_y]
            cur_x += step_stone_width + gap_length
    
    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_4(length, width, field_resolution, difficulty):
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

def set_terrain_5(length, width, field_resolution, difficulty):
    """Obstacle course featuring balance beams and narrow pathways for the robot to traverse."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Balance beam dimensions
    beam_length = 2.0
    beam_width = 0.4 - difficulty * 0.2
    beam_height = 0.05 + difficulty * 0.2
    
    beam_length_idx = m_to_idx(beam_length)
    beam_width_idx = m_to_idx(beam_width)
    beam_height_value = 0.2 + difficulty * 0.3

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, beam_width_idx):
        mid_y_offset = np.random.randint(-m_to_idx(0.5), m_to_idx(0.5))
        beam_mid_y = mid_y + mid_y_offset
        half_width = beam_width_idx // 2
        height_field[start_x:start_x + beam_length_idx, beam_mid_y - half_width:beam_mid_y + half_width] = beam_height_value
        return beam_mid_y

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [1, mid_y]  # First goal at the spawn

    cur_x = spawn_length

    # Place balance beams and goals
    for i in range(6):
        beam_y = add_beam(cur_x, beam_width_idx)
        goals[i+1] = [cur_x + beam_length_idx // 2, beam_y]
        # Update x position for the next beam, including gaps proportional to the difficulty
        cur_x += beam_length_idx + m_to_idx(0.5 + 0.5 * difficulty)

    # Final goal past the last beam
    goals[-1] = [cur_x + m_to_idx(1), mid_y]  # 1 meter past the last beam
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_6(length, width, field_resolution, difficulty):
    """Intermediate Platforms with Gaps and Narrow Pathways Testing Precision Navigation."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions
    platform_length = 1.0 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.2, 1.6)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.3 * difficulty, 0.3 + 0.5 * difficulty
    narrow_path_width = 0.3 + 0.2 * difficulty  # Making narrow paths wider based on difficulty
    narrow_path_width = m_to_idx(narrow_path_width)
    gap_length = 0.2 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_narrow_path(start_x, end_x, mid_y):
        half_width = narrow_path_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = 0  # flat narrow path

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Set remaining area to be a pit, force jumps or narrow path traversal
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    narrow_path_enabled = False

    for i in range(6):  # Set up platforms and possibly narrow paths
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        if narrow_path_enabled:
            add_narrow_path(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
            narrow_path_enabled = False
        else:
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
            narrow_path_enabled = True

        # Add gap
        cur_x += platform_length + dx + gap_length

    # Ensure a final platform at the end
    add_platform(cur_x, cur_x + platform_length, mid_y)
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    
    # Ensure last part of terrain is solid
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_7(length, width, field_resolution, difficulty):
    """Complex obstacle course with raised steps, narrow beams, zigzag paths, and jumps across gaps for balanced difficulty."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    mid_y = m_to_idx(width) // 2
    
    def add_raised_step(start_x, end_x, mid_y, height):
        """Adds a raised step to the terrain."""
        half_width = m_to_idx(1.0) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_narrow_beam(start_x, end_x, mid_y):
        """Adds a narrow beam to the terrain."""
        beam_width = m_to_idx(0.4)
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - beam_width // 2, mid_y + beam_width // 2
        beam_height = np.random.uniform(0.1, 0.3) * difficulty
        height_field[x1:x2, y1:y2] = beam_height

    def add_zigzag_path(start_x, length, mid_y):
        """Adds a zigzag path to the terrain."""
        path_width = m_to_idx(0.4)
        turns = np.random.randint(3, 5)  # Number of zigzag turns
        cur_x = start_x
        cur_y = mid_y
        direction = 1
        for _ in range(turns):
            end_x = cur_x + length // turns
            y1, y2 = cur_y - path_width // 2, cur_y + path_width // 2
            path_height = np.random.uniform(0.1, 0.3) * difficulty
            height_field[cur_x:end_x, y1:y2] = path_height
            cur_x = end_x
            cur_y += direction * path_width * 2
            direction *= -1  # Alternate direction

    def add_gap(start_x, end_x, start_y, end_y):
        """Creates a gap in the terrain."""
        height_field[start_x:end_x, start_y:end_y] = -1.0

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    # Increase the height and complexity of each obstacle
    for i in range(7):
        if i % 2 == 0:
            # Add a raised step/platform
            platform_length = m_to_idx(1.2)
            platform_height = np.random.uniform(0.2, 0.4) * difficulty + i * 0.05
            add_raised_step(cur_x, cur_x + platform_length, mid_y, platform_height)
            goals[i + 1] = [cur_x + platform_length // 2, mid_y]
            cur_x += platform_length + m_to_idx(0.2)
        else:
            # Add a narrow beam
            beam_length = m_to_idx(1.2)
            add_narrow_beam(cur_x, cur_x + beam_length, mid_y)
            goals[i + 1] = [cur_x + beam_length // 2, mid_y]
            cur_x += beam_length + m_to_idx(0.2)
            
            # Create a zigzag path
            zigzag_length = m_to_idx(1.5)
            add_zigzag_path(cur_x, zigzag_length, mid_y)
            goals[i + 1] = [cur_x + zigzag_length // 2, mid_y]
            cur_x += zigzag_length + m_to_idx(0.2)

        # Add gaps to increase difficulty
        gap_length = m_to_idx(0.4 + 0.4 * difficulty)
        add_gap(cur_x, cur_x + gap_length, 0, m_to_idx(width))
        cur_x += gap_length
    
    # Add final goal behind the last obstacle
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_8(length, width, field_resolution, difficulty):
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

def set_terrain_9(length, width, field_resolution, difficulty):
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

# INSERT TERRAIN FUNCTION DEFINITIONS HERE
