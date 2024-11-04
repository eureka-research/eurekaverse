
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
    """Wide platforms and gentle ramps for the robot to navigate across and climb over with moderate difficulty."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_height_min, platform_height_max = 0.05, 0.15 + 0.25 * difficulty
    platform_length = 0.8 + 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 1.2 + 0.8 * difficulty
    platform_width = m_to_idx(platform_width)
    gap_length = 0.2 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)
    ramp_length = 1.5
    ramp_length = m_to_idx(ramp_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, y_center, height):
        y1, y2 = y_center - platform_width // 2, y_center + platform_width // 2
        height_field[start_x:end_x, y1:y2] = height

    def add_ramp(start_x, end_x, y_center, height_start, height_end):
        y1, y2 = y_center - platform_width // 2, y_center + platform_width // 2
        slant = np.linspace(height_start, height_end, num=end_x - start_x)
        height_field[start_x:end_x, y1:y2] = slant[:, None]

    # Set up a flat, initial spawn area
    start_x = m_to_idx(2)
    height_field[0:start_x, :] = 0
    goals[0] = [start_x - m_to_idx(0.5), mid_y]

    cur_x = start_x

    # Design a new terrain with alternating platforms and gentle ramps
    for i in range(6):
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        
        if i % 2 == 0:  # Add platform
            add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)
        else:  # Add gentle ramp
            add_ramp(cur_x, cur_x + ramp_length, mid_y, 0, platform_height)

        goals[i+1] = [cur_x + platform_length // 2, mid_y]

        # Add gap if it's a platform
        if i % 2 == 0:
            cur_x += platform_length + gap_length
        else:
            cur_x += ramp_length

    # Set final goal
    final_goal_x = cur_x + m_to_idx(0.5)
    goals[-1] = [final_goal_x, mid_y]
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
    """Gentle platforms and ramps with minor gaps for balanced challenge."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions
    platform_length = 1.0 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.4)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.1 * difficulty, 0.1 + 0.2 * difficulty
    gap_length = 0.1 + 0.3 * difficulty
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
        ramp_height = np.random.uniform(platform_height_min, platform_height_max)
        slant = np.linspace(0, ramp_height, num=y2-y1)[::direction]
        slant = slant[None, :]  # Add a dimension for broadcasting to x
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.05, 0.05
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.0, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Initial platform after flat spawn area
    cur_x = spawn_length
    for i in range(0, 6, 2):  # Set up 3 platforms interleaved with 2 ramps
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
        goals[i] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        cur_x += platform_length + dx + gap_length

        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        direction = (-1) ** i  # Alternate left and right ramps
        dy = dy * direction  # Alternate positive and negative y offsets
        add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, direction)
        goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        cur_x += platform_length + dx + gap_length

    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_3(length, width, field_resolution, difficulty):
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

def set_terrain_4(length, width, field_resolution, difficulty):
    """Narrow raised pathways and varying height platforms for the robot to navigate and balance."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Dimensions and height ranges for narrow pathways and platforms
    path_length = 1.2 - 0.3 * difficulty
    path_length = m_to_idx(path_length)
    path_width = 0.4 + 0.2 * (1 - difficulty)  # Narrower paths at higher difficulty
    path_width = m_to_idx(path_width)
    path_height_min, path_height_max = 0.1 + 0.2 * difficulty, 0.4 + 0.2 * difficulty

    gap_length = 0.2 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_path(start_x, end_x, mid_y, randomize_height=True):
        """Adds a narrow raised path."""
        half_width = path_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width 
        path_height = np.random.uniform(path_height_min, path_height_max) if randomize_height else 0.0
        height_field[x1:x2, y1:y2] = path_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    for i in range(6):
        dx = np.random.randint(m_to_idx(-0.1), m_to_idx(0.1))
        x1 = cur_x
        x2 = cur_x + path_length + dx

        # Alternate between heights and flat sections
        if i % 2 == 0:
            add_path(x1, x2, mid_y)
            goals[i+1] = [cur_x + (path_length + dx) // 2, mid_y]
        else:
            add_path(x1, x2, mid_y, randomize_height=False)
            goals[i+1] = [cur_x + (path_length + dx) // 2, mid_y]
        
        cur_x += path_length + dx + gap_length
    
    # Add final goal behind the last path, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_5(length, width, field_resolution, difficulty):
    """Narrow bridges and balancing beams for the robot to walk and balance across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up bridge and beam dimensions
    min_beam_width = 0.4
    max_beam_width = 1.0 - difficulty * 0.6
    min_gap_length = 0.2
    max_gap_length = 0.5
    beam_height = 0.2 + difficulty * 0.3

    mid_y = m_to_idx(width) // 2

    def add_balancing_beam(start_x, end_x, mid_y, beam_width):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = beam_height

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
    for i in range(6):  # Set up 6 balancing beams
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        beam_width = np.random.uniform(min_beam_width, max_beam_width)
        beam_length = 1.0
        beam_length = m_to_idx(beam_length)
        gap_length = np.random.uniform(min_gap_length, max_gap_length)
        gap_length = m_to_idx(gap_length)

        add_balancing_beam(cur_x, cur_x + beam_length + dx, mid_y + dy, m_to_idx(beam_width))

        # Put goal in the center of the beam
        goals[i+1] = [cur_x + (beam_length + dx) // 2, mid_y + dy]

        # Add gap
        cur_x += beam_length + dx + gap_length
    
    # Add final goal behind the last balancing beam, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_6(length, width, field_resolution, difficulty):
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

def set_terrain_7(length, width, field_resolution, difficulty):
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

def set_terrain_8(length, width, field_resolution, difficulty):
    """Complex terrain with narrow pathways, high platforms, long gaps, and ramps to increase difficulty."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and ramp dimensions
    platform_length = 1.2 - 0.25 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.4 * difficulty + 1.0)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.2 * difficulty, 0.3 * difficulty
    ramp_height_min, ramp_height_max = 0.5 * difficulty, 0.7 * difficulty
    gap_length = 0.4 + 0.6 * difficulty
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
        slant = np.linspace(0, ramp_height, num=y2-y1)[::direction]
        slant = slant[None, :]  # Add a dimension for broadcasting to x
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.15, 0.15
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # More dynamic obstacles
    cur_x = spawn_length
    for i in range(3):  # Create alternating platforms and ramps
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        if i % 2 == 0:
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
        else:
            direction = (-1) ** i
            add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, direction)

        # Put goal in the center of the obstacle
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += platform_length + dx + gap_length

    # Final more complex obstacles: narrow pathways and higher platforms
    for i in range(3, 6):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)

        # Add very narrow pathways for the challenge
        pathway_width = m_to_idx(0.5)
        y1, y2 = mid_y + dy - pathway_width // 2, mid_y + dy + pathway_width // 2
        pathway_height = np.random.uniform(0.5 * difficulty, 0.7 * difficulty)
        height_field[cur_x:cur_x + platform_length + dx, y1:y2] = pathway_height

        # Put goal at the end of the pathway
        goals[i+1] = [cur_x + (platform_length + dx) / 2, (y1 + y2) / 2]

        # Add gap
        cur_x += platform_length + dx + gap_length

    # Add last challenging obstacle: long ramp to a high platform
    dx = np.random.randint(dx_min, dx_max)
    dy = np.random.randint(dy_min, dy_max)
    add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, direction=1)
    goals[6] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
    
    cur_x += platform_length + dx + gap_length
    last_height = np.random.uniform(platform_height_min, platform_height_max)
    platform_height = last_height
    height_field[cur_x:,:platform_width] = platform_height

    goals[-1] = [cur_x + m_to_idx(1.0), mid_y]

    return height_field, goals

def set_terrain_9(length, width, field_resolution, difficulty):
    """Combination of narrow beams, incline ramps, and platform jumps to test climbing, jumping, and balancing abilities of the quadruped robot."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up ramp, beam, and platform dimensions
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    ramp_length = 1.0
    ramp_length = m_to_idx(ramp_length)
    ramp_height = 0.15 + 0.1 * difficulty
    narrow_beam_width = 0.35  # Narrow beam width
    narrow_beam_width = m_to_idx(narrow_beam_width)
    
    mid_y = m_to_idx(width) // 2
    
    def add_ramp(start_x, end_x, mid_y, height):
        """Add an incline or decline ramp to the height_field."""
        half_width = m_to_idx(0.4)
        for x in range(start_x, end_x):
            ramp_incline = (x - start_x) / (end_x - start_x) * height
            height_field[x, mid_y - half_width: mid_y + half_width] = ramp_incline
    
    def add_platform(start_x, end_x, mid_y, height):
        """Add a flat platform to the height_field."""
        half_width = m_to_idx(0.6)
        height_field[start_x:end_x, mid_y - half_width: mid_y + half_width] = height

    def add_narrow_beam(start_x, end_x, mid_y, height):
        """Add a narrow balance beam to the height_field."""
        half_width = narrow_beam_width // 2
        height_field[start_x:end_x, mid_y - half_width: mid_y + half_width] = height
    
    dx_min, dx_max = 0, 0  # Ensure no horizontal randomness within feature
    dy_min, dy_max = -0.2, 0.2  # Slight random deviation on y direction
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    
    # Add ramp
    dy = np.random.randint(dy_min, dy_max)
    add_ramp(cur_x, cur_x + ramp_length, mid_y + dy, ramp_height)
    goals[1] = [cur_x + ramp_length // 2, mid_y + dy]
    cur_x += ramp_length + m_to_idx(0.1)
    
    # Add narrow beam
    dy = np.random.randint(dy_min, dy_max) 
    add_narrow_beam(cur_x, cur_x + platform_length, mid_y + dy, ramp_height)
    goals[2] = [cur_x + platform_length // 2, mid_y + dy]
    cur_x += platform_length + m_to_idx(0.1)

    # Add middle-platform jumps
    dy = 0
    add_platform(cur_x, cur_x + platform_length, mid_y + dy, ramp_height + 0.1)
    goals[3] = [cur_x + platform_length // 2, mid_y + dy]
    cur_x += platform_length + m_to_idx(0.1)
    
    # Add narrow beam
    dy = np.random.randint(dy_min, dy_max) 
    add_narrow_beam(cur_x, cur_x + platform_length, mid_y + dy, ramp_height + 0.2)
    goals[4] = [cur_x + platform_length // 2, mid_y + dy]
    cur_x += platform_length + m_to_idx(0.1)

    # Add final decline ramp
    add_ramp(cur_x, cur_x + ramp_length, mid_y, -ramp_height)
    goals[5] = [cur_x + ramp_length // 2, mid_y]
    cur_x += ramp_length

    # Place final high goal on flat terrain behind last ramp
    add_platform(cur_x, cur_x + platform_length, mid_y, 0)
    goals[-2] = [cur_x + platform_length // 2, mid_y]
    cur_x += platform_length
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    return height_field, goals

# INSERT TERRAIN FUNCTION DEFINITIONS HERE
