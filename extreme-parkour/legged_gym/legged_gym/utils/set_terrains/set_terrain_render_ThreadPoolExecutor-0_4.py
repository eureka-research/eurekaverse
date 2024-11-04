
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
    """
    Stepped platforms with both vertical and horizontal displacements to test climbing, balancing, and 
    precise stepping abilities.
    """

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length = 1.0 - 0.2 * difficulty  # Length of each platform
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.6)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.15 * difficulty, 0.05 + 0.3 * difficulty
    gap_length = 0.1 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.0, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Initialize current x-position
    cur_x = spawn_length

    for i in range(7):  # Set up 7 elevated platforms
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        height = np.random.uniform(platform_height_min, platform_height_max)
        
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, height)

        # Put goal in the center of each platform
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += platform_length + dx + gap_length

    # Add final goal behind the last platform, fill in the remaining gap
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
    """Series of elevated beams and tunnels for the robot to navigate and balance on."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up beam dimensions
    beam_length = np.random.uniform(1.0, 2.0) - 0.5 * difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = np.random.uniform(0.4, 0.8)  # Narrow beam
    beam_width = m_to_idx(beam_width)
    beam_height_min, beam_height_max = 0.1 + 0.1 * difficulty, 0.3 + 0.2 * difficulty
    gap_length = 0.2 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)

    additional_gap = 0.2  # Extra gap based on difficulty level
    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, center_y):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = center_y - half_width, center_y + half_width
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
        goals[i+1] = [cur_x + (beam_length + dx) / 2, mid_y + dy]

        # Add optional gap to beams based on the difficulty.
        additional_gap_flag = np.random.rand() < difficulty  # Adds additional gaps as difficulty increases
        cur_x += beam_length + dx + gap_length + (additional_gap_flag * m_to_idx(additional_gap))
    
    # Add final goal behind the last beam, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_3(length, width, field_resolution, difficulty):
    """Urban-inspired obstacle course with cylindrical columns and rectangular barriers."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    obstacle_height_min = 0.05
    obstacle_height_max = 0.4
    mid_y = m_to_idx(width / 2)
    # Flatten spawn area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    
    # Set the first goal at the spawn point
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    def add_cylinder_obstacle(x_center, y_center, radius, height):
        for x in range(x_center - radius, x_center + radius + 1):
            for y in range(y_center - radius, y_center + radius + 1):
                if (x - x_center) ** 2 + (y - y_center) ** 2 <= radius ** 2:
                    height_field[x, y] = height

    def add_rect_obstacle(start_x, end_x, start_y, end_y, height):
        height_field[start_x:end_x, start_y:end_y] = height

    # Parameters for the obstacles
    cylinder_radius = m_to_idx(0.2) + int(difficulty * 5)
    cylinder_height = obstacle_height_min + difficulty * (obstacle_height_max - obstacle_height_min)
    rect_width = m_to_idx(1.0) + int(difficulty * 8)
    rect_height = cylinder_height

    current_x = spawn_length
    for i in range(6):
        dx = m_to_idx(random.uniform(0.4, 1.0))
        dy = m_to_idx(random.uniform(-1.0, 1.0))

        if i % 2 == 0:
            x_center = current_x + dx
            y_center = mid_y + dy
            add_cylinder_obstacle(x_center, y_center, cylinder_radius, cylinder_height)
            goals[i + 1] = [x_center, y_center]
        else:
            start_x = current_x + dx
            end_x = start_x + rect_width
            start_y = mid_y + dy - rect_width // 2
            end_y = start_y + rect_width
            add_rect_obstacle(start_x, end_x, start_y, end_y, rect_height)
            goals[i + 1] = [start_x + rect_width // 2, mid_y + dy]

        current_x += dx + rect_width

    # Set the final goal
    goals[-1] = [min(current_x + m_to_idx(1.0), height_field.shape[0] - m_to_idx(0.5)), mid_y]
    
    return height_field, goals

def set_terrain_4(length, width, field_resolution, difficulty):
    """Varied terrain with balance beams and alternating platforms for balanced navigation and agility."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up balance beam and platform dimensions
    platform_length = 1.2 - 0.4 * difficulty  # Adjusted to handle increasing difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.2)  # Balance beams and narrow platforms, decrease slightly for increased difficulty
    platform_width = m_to_idx(platform_width)
    balance_beam_width = m_to_idx(0.4) + int(difficulty * 4)  # Ensure minimum width for feasibility
    platform_height_min, platform_height_max = 0.05 * difficulty, 0.2 + 0.3 * difficulty  # Maintain heights for progressive difficulty
    gap_length = 0.05 + 0.3 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, width):
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_balance_beam(start_x, end_x, mid_y):
        beam_half_width = balance_beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - beam_half_width, mid_y + beam_half_width
        beam_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = beam_height

    dx_min, dx_max = 0.0, 0.2  # No backward steps
    m_dx_min, m_dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn point
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  
    
    cur_x = spawn_length
    for i in range(4):
        dx = np.random.randint(m_dx_min, m_dx_max)
        dy = np.random.randint(dy_min, dy_max)

        if i % 2 == 0:  # Alternate between platforms and balance beams
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_width)
            goals[i + 1] = [cur_x + (platform_length + dx) // 2, mid_y + dy]
        else:
            add_balance_beam(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i + 1] = [cur_x + (platform_length + dx) // 2, mid_y + dy]

        cur_x += platform_length + dx + gap_length

    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_5(length, width, field_resolution, difficulty):
    """Zigzag patterned platforms with varying heights for enhanced navigation and jumping precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions
    platform_length = 0.8 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.6, 1.2)  # Varied width
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.05 + 0.1 * difficulty, 0.2 + 0.3 * difficulty
    gap_length = 0.1 + 0.3 * difficulty
    gap_length = m_to_idx(gap_length)
    
    mid_y = m_to_idx(width) // 2
    
    def add_platform(start_x, end_x, y_center, level):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = y_center - half_width, y_center + half_width
        platform_height = platform_height_min + (platform_height_max - platform_height_min) * level
        height_field[x1:x2, y1:y2] = platform_height
    
    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.6, 0.6
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    levels = [0, 1]
    for i in range(6):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        level = np.random.choice(levels)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, level)
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_6(length, width, field_resolution, difficulty):
    """Incline-stepped platforms forcing the quadruped to carefully navigate, climb, and descend to avoid stumbling or falling off."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and stair dimensions
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 1.2 - 0.2 * difficulty
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 * difficulty, 0.3 * difficulty
    stair_height_min, stair_height_max = 0.1 * difficulty, 0.4 * difficulty
    gap_length = 0.2 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_stairs(start_x, end_x, mid_y, direction, num_steps):
        step_length = (end_x - start_x) // num_steps
        step_height = np.linspace(stair_height_min, stair_height_max, num_steps + 1)
        half_width = platform_width // 2
        
        for step in range(num_steps):
            x1 = start_x + step * step_length
            x2 = x1 + step_length
            y1, y2 = mid_y - half_width, mid_y + half_width
            height_field[x1:x2, y1:y2] = step_height[step] + direction * (step / (num_steps + 1)) * step_height[step]

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.0, 0.4  # Polarity of dy will alternate instead of being random
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Set remaining area to be a pit
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    for i in range(7):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        # Alternate direction for stairs (-1 for down, 1 for up)
        direction = (-1) ** i
        
        # Add platform section before the stairs
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height)
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx

        # Add stairs
        num_steps = np.random.randint(3, 7)
        stair_length = m_to_idx(0.3) * num_steps
        add_stairs(cur_x, cur_x + stair_length + dx, mid_y + dy, direction, num_steps)
        cur_x += stair_length + dx + gap_length

    # Add final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_7(length, width, field_resolution, difficulty):
    """A course with moderate platforms and stepping stones targeting jumping and precise navigation while balancing difficulty and feasibility."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Dimensions for platforms and stepping stones
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 1.0 + 0.2 * difficulty  # Wider platforms
    platform_width = m_to_idx(platform_width)
    platform_height = 0.1 * difficulty

    stone_length = 0.5
    stone_length = m_to_idx(stone_length)
    stone_width = 0.5
    stone_width = m_to_idx(stone_width)
    stone_height = 0.05 + 0.15 * difficulty

    gap_length = 0.3 + 0.4 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = platform_height

    def add_stepping_stone(x_center, y_center):
        half_length = stone_length // 2
        half_width = stone_width // 2
        x1, x2 = x_center - half_length, x_center + half_length
        y1, y2 = y_center - half_width, y_center + half_width
        height_field[x1:x2, y1:y2] = stone_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(4):  # Set up 4 platforms
        dx = np.random.randint(-m_to_idx(0.1), m_to_idx(0.1))
        dy = np.random.randint(-m_to_idx(0.4), m_to_idx(0.4))
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)

        goals[i+1] = [cur_x + (platform_length + dx) // 2, mid_y + dy]

        cur_x += platform_length + dx + gap_length
    
    for i in range(4, 7):  # Set up 3 stepping stones
        dx = np.random.randint(-m_to_idx(0.1), m_to_idx(0.1))
        dy = np.random.randint(-m_to_idx(0.4), m_to_idx(0.4))
        stone_x = cur_x + dx
        stone_y = mid_y + dy
        add_stepping_stone(stone_x, stone_y)

        goals[i+1] = [stone_x, stone_y]
        
        cur_x += stone_length + gap_length
    
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    return height_field, goals

def set_terrain_8(length, width, field_resolution, difficulty):
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

def set_terrain_9(length, width, field_resolution, difficulty):
    """Complex obstacle course featuring alternating ramps and narrow platforms."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up obstacle dimensions
    platform_length = 1.0 - 0.3 * difficulty    # Between 0.7m and 1.0m
    platform_length_idx = m_to_idx(platform_length)
    platform_width = 0.8 + 0.2 * difficulty     # Between 0.8m and 1.0m
    platform_width_idx = m_to_idx(platform_width)
    ramp_height_min, ramp_height_max = 0.1, 0.3
    gap_length = 0.2 + 0.3 * difficulty         # Between 0.2m and 0.5m
    gap_length_idx = m_to_idx(gap_length)

    mid_y = m_to_idx(width // 2)

    def add_platform(start_x, end_x, y_center, height):
        half_width = platform_width_idx // 2
        x1, x2 = start_x, end_x
        y1, y2 = y_center - half_width, y_center + half_width
        height_field[x1:x2, y1:y2] = height

    def add_ramp(start_x, end_x, y_center, max_height):
        half_width = platform_width_idx // 2
        x1, x2 = start_x, end_x
        y1, y2 = y_center - half_width, y_center + half_width
        ramp_slope = np.linspace(0, max_height, x2 - x1)
        height_field[x1:x2, y1:y2] = ramp_slope[:, np.newaxis]

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # First goal at spawn area
    goals[0] = [spawn_length // 2, mid_y]

    cur_x = spawn_length
    height = 0.2  # Initial height for platforms, can vary

    for i in range(1, 8):
        if i % 2 == 0:
            # Add platform
            dx = np.random.randint(-m_to_idx(0.05), m_to_idx(0.05))
            dy = np.random.randint(-platform_width_idx // 2, platform_width_idx // 2)
            platform_start = cur_x + gap_length_idx
            platform_end = platform_start + platform_length_idx
            height = height + np.random.uniform(-0.1, 0.1)
            add_platform(platform_start, platform_end, mid_y + dy, height)
            goals[i] = [(platform_start + platform_end) // 2, mid_y + dy]
            cur_x = platform_end
        else:
            # Add ramp
            dx = np.random.randint(-m_to_idx(0.05), m_to_idx(0.05))
            dy = np.random.randint(-platform_width_idx // 2, platform_width_idx // 2)
            ramp_start = cur_x + gap_length_idx
            ramp_end = ramp_start + platform_length_idx
            ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
            add_ramp(ramp_start, ramp_end, mid_y + dy, ramp_height)
            goals[i] = [(ramp_start + ramp_end) // 2, mid_y + dy]
            cur_x = ramp_end

    return height_field, goals

# INSERT TERRAIN FUNCTION DEFINITIONS HERE
