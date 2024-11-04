
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
    """Series of hurdles and narrow paths forcing precise movements and jumps."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up hurdle dimensions
    hurdle_height_min, hurdle_height_max = 0.1 + 0.2 * difficulty, 0.3 + 0.3 * difficulty
    hurdle_width = 0.4 + 0.4 * difficulty
    hurdle_width = m_to_idx(hurdle_width)
    hurdle_gap_length = 0.6 + 1.0 * difficulty
    hurdle_gap_length = m_to_idx(hurdle_gap_length)

    mid_y = m_to_idx(width) // 2
    
    def add_hurdle(start_x, y):
        half_width = hurdle_width // 2
        x1, x2 = start_x, start_x + m_to_idx(0.3)
        y1, y2 = y - half_width, y + half_width
        hurdle_height = np.random.uniform(hurdle_height_min, hurdle_height_max)
        height_field[x1:x2, y1:y2] = hurdle_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [m_to_idx(1), mid_y]

    cur_x = spawn_length
    for i in range(6):  # Set up 6 hurdles
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_hurdle(cur_x + dx, mid_y + dy)

        # Put goal in front of each hurdle
        goals[i+1] = [cur_x + dx + m_to_idx(0.15), mid_y + dy]

        # Add gap
        cur_x += m_to_idx(0.3) + hurdle_gap_length

    # Add final goal behind the last hurdle, fill in the remaining area
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_1(length, width, field_resolution, difficulty):
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

def set_terrain_2(length, width, field_resolution, difficulty):
    """Obstacle course of barriers forcing the quadruped to weave and navigate narrow paths."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define barrier heights and widths
    barrier_height_min, barrier_height_max = 0.1 * difficulty, 0.4 * difficulty
    barrier_length_min, barrier_length_max = 0.3, 0.6
    barrier_width = 1.2 - 0.4 * difficulty  # Slightly wider at lower difficulty

    barrier_height = np.random.uniform(barrier_height_min, barrier_height_max)
    barrier_length = np.random.uniform(barrier_length_min, barrier_length_max)
    barrier_width = m_to_idx(barrier_width)
    barrier_length = m_to_idx(barrier_length)
    
    mid_y = m_to_idx(width) // 2

    # Helper function to add barriers
    def add_barrier(center_x, center_y):
        half_width = barrier_width // 2
        half_length = barrier_length // 2
        x1, x2 = center_x - half_length, center_x + half_length
        y1, y2 = center_y - half_width, center_y + half_width
        height_field[x1:x2, y1:y2] = barrier_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Define the path length between barriers
    path_length = m_to_idx(2.0 - difficulty)

    # Add barriers and goals
    cur_x = spawn_length
    for i in range(7):
        # Slight random offset to y direction
        offset_y = np.random.randint(-m_to_idx(0.5), m_to_idx(0.5))
        
        # Add barrier
        add_barrier(cur_x + path_length, mid_y + offset_y)
        
        # Place goal right before the barrier
        goals[i+1] = [cur_x + path_length - m_to_idx(0.2), mid_y + offset_y]

        # Update current x position
        cur_x += path_length + barrier_length

        # Alternate the barrier direction in y direction (Left-Right placement)
        mid_y = (mid_y + m_to_idx(width) // 2 + m_to_idx(1)) % m_to_idx(width)

    # Place final goal after last barrier
    final_goal_x = cur_x + path_length
    final_goal_y = mid_y
    goals[7] = [final_goal_x, final_goal_y]

    return height_field, goals

def set_terrain_3(length, width, field_resolution, difficulty):
    """Mix of precision stepping stones and narrow pathways with varying heights and slight gaps."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up obstacle dimensions
    # Platform height, stepping stones, and gap dimensions will vary with difficulty
    platform_length = 1.2 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.6, 1.0 + difficulty)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1, 0.5 * difficulty
    gap_length = 0.2 + 0.4 * difficulty
    gap_length = m_to_idx(gap_length)
    step_stone_width = np.random.uniform(0.3, 0.5)
    step_stone_width = m_to_idx(step_stone_width)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_stepping_stones(start_x, num_stones, mid_y):
        stone_spacing = m_to_idx(0.3)
        for i in range(num_stones):
            stone_x = start_x + i * (step_stone_width + stone_spacing)
            x1, x2 = stone_x, stone_x + step_stone_width
            y1, y2 = mid_y - step_stone_width // 2, mid_y + step_stone_width // 2
            stone_height = np.random.uniform(0, platform_height_max)
            height_field[x1:x2, y1:y2] = stone_height

    dx_min, dx_max = -0.1, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.0, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Initial platform
    cur_x = spawn_length
    dx = np.random.randint(dx_min, dx_max)
    dy = np.random.randint(dy_min, dy_max)
    add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
    goals[1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
    cur_x += platform_length + dx + gap_length

    # Middle section with stepping stones
    num_stones = 4
    add_stepping_stones(cur_x, num_stones, mid_y)
    goals[2] = [cur_x + (num_stones // 2) * (step_stone_width + m_to_idx(0.3)), mid_y]
    cur_x += num_stones * (step_stone_width + m_to_idx(0.3)) + gap_length
    
    for i in range(3, 6):  # Platforms with varying gaps and heights
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
        goals[i] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

    # Final section
    dx = np.random.randint(dx_min, dx_max)
    dy = np.random.randint(dy_min, dy_max)
    add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
    goals[6] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
    cur_x += platform_length + dx + gap_length

    # Add final goal behind the last platform, fill in the remaining gap
    goals[7] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_4(length, width, field_resolution, difficulty):
    """Easier platform traversing terrain with moderate gaps for the robot to navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions
    platform_length = 1.0 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.2, 2.0)  
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.1 * difficulty, 0.05 + 0.15 * difficulty
    gap_length = 0.1 + 0.4 * difficulty  
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    # Start position
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Set remaining area to be a pit and place platforms to jump across
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    for i in range(6):  # Set up 6 platforms
        add_platform(cur_x, cur_x + platform_length, mid_y)

        # Place goals at the center of each platform
        goals[i+1] = [cur_x + platform_length // 2, mid_y]

        # Move to the next platform position, factoring in the gap
        cur_x += platform_length + gap_length
    
    # Add final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_5(length, width, field_resolution, difficulty):
    """Introduces angled platforms, narrow stepping stones, and slopes for balanced traversal and precision stepping."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and obstacle dimensions
    platform_length = 0.8 - 0.3 * difficulty
    platform_length_idx = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.4, 0.6)  # Narrower platforms to increase difficulty
    platform_width_idx = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.05, 0.2 + 0.25 * difficulty
    gap_length = 0.4 + 0.6 * difficulty  # Wider gaps to increase jumping difficulty
    gap_length_idx = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_slanted_platform(x, y, height, direction):
        """Adds a platform with a height gradient to simulate an angled surface."""
        half_length = platform_length_idx // 2
        half_width = platform_width_idx // 2
        x_low, x_high = x - half_length, x + half_length
        y_low, y_high = y - half_width, y + half_width
        gradient = np.linspace(0, height, num=(y_high - y_low))
        if direction > 0:
            height_field[x_low:x_high, y_low:y_high] = np.tile(gradient[None, :], (x_high - x_low, 1))
        else:
            height_field[x_low:x_high, y_low:y_high] = np.tile(gradient[None, ::-1], (x_high - x_low, 1))

    def add_stepping_stone(x, y):
        """Adds a small, irregularly shaped stepping stone."""
        min_height = platform_height_min
        max_height = min_height + difficulty * 0.1
        stone_height = np.random.uniform(min_height, max_height)
        stone_area = (m_to_idx(0.4), m_to_idx(0.4))  # Small stone
        stone_x_low = x - stone_area[0] // 2
        stone_x_high = x + stone_area[0] // 2
        stone_y_low = y - stone_area[1] // 2
        stone_y_high = y + stone_area[1] // 2
        height_field[stone_x_low:stone_x_high, stone_y_low:stone_y_high] = stone_height

    spawn_length_idx = m_to_idx(2)
    height_field[0:spawn_length_idx, :] = 0
    goals[0] = [spawn_length_idx - m_to_idx(0.5), mid_y]

    cur_x = spawn_length_idx
    previous_height = 0

    for i in range(1, 7):
        if i % 2 == 0:
            add_slanted_platform(cur_x, mid_y, random.uniform(platform_height_min, platform_height_max), (-1) ** i)
        else:
            add_stepping_stone(cur_x, mid_y)

        goals[i] = [cur_x, mid_y]
        cur_x += platform_length_idx + gap_length_idx
        previous_height = random.uniform(platform_height_min, platform_height_max)

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]  # Final goal behind last obstacle
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_6(length, width, field_resolution, difficulty):
    """High platforms, steep ramps, and narrow ledges to test advanced climbing and precise navigation abilities."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set platform and ramp dimensions
    platform_length = 0.8 * (1.0 - 0.3 * difficulty)  # Slightly reduced length for higher frequency of obstacles
    platform_length = m_to_idx(platform_length)
    ramp_length = 1.0 * (1.0 - 0.3 * difficulty)
    ramp_length = m_to_idx(ramp_length)
    
    platform_width = np.random.uniform(0.6, 1.0)  # Narrower platform for higher precision
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.2 + 0.3 * difficulty, 0.4 + 0.4 * difficulty
    
    ramp_height_min, ramp_height_max = 0.1 + 0.4 * difficulty, 0.2 + 0.5 * difficulty
    gap_length = 0.15 + 0.75 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        """Add a platform to the height_field."""
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_ramp(start_x, end_x, mid_y, direction):
        """Add a ramp to the height_field."""
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        slant = np.linspace(0, ramp_height, num=(x2-x1))
        if direction < 0:
            slant = np.flip(slant)
        slant = slant[:, None]  # Add a dimension for broadcasting to y
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.08, 0.08
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Initial flat area
    cur_x = spawn_length

    # Add a sequence of high platforms and steep ramps
    for i in range(3):
        # High Platform
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
        goals[i*2+1] = [cur_x + (platform_length + dx) // 2, mid_y + dy]

        # Gap
        cur_x += platform_length + dx + gap_length
        
        # Steep Ramp
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        ramp_direction = -1 if i % 2 == 0 else 1
        add_ramp(cur_x, cur_x + ramp_length + dx, mid_y + dy, ramp_direction)
        goals[i*2+2] = [cur_x + (ramp_length + dx) // 2, mid_y + dy]

        # Gap
        cur_x += ramp_length + dx + gap_length

    # Final narrow ledges
    for j in range(1):
        # Narrow ledge
        ledge_length = m_to_idx(1.0)
        ledge_width = m_to_idx(0.5)
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        x1, x2 = cur_x, cur_x + ledge_length + dx
        y1, y2 = mid_y - ledge_width // 2 + dy, mid_y + ledge_width // 2 + dy
        ledge_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = ledge_height
        
        goals[7] = [cur_x + (ledge_length + dx) // 2, mid_y + dy]

        # No gap after final ledge
        cur_x += ledge_length + dx
   
    # Add final goal behind the last ledge
    goals[7] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_7(length, width, field_resolution, difficulty):
    """Combination of balance beams, stepping stones, and small platforms for varied but balanced testing."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Dimensions
    beam_length = 1.0 - 0.2 * difficulty    # Between 0.8m and 1.0m, easier than before
    beam_length = m_to_idx(beam_length)
    beam_width = 0.4 + 0.2 * difficulty     # Between 0.4m and 0.6m
    beam_width = m_to_idx(beam_width)
    platform_length = 1.0 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 0.8 + 0.2 * difficulty
    platform_width = m_to_idx(platform_width)
    stone_length = 0.5
    stone_length = m_to_idx(stone_length)
    stone_width = 0.5
    stone_width = m_to_idx(stone_width)
    stone_height = 0.1 + 0.2 * difficulty

    gap_length = 0.3 + 0.4 * difficulty     # Between 0.3m and 0.7m, easier than before
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, mid_y):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        beam_height = 0.1
        height_field[x1:x2, y1:y2] = beam_height
    
    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(0.1, 0.3)
        height_field[x1:x2, y1:y2] = platform_height

    def add_stepping_stone(x, y):
        half_length = stone_length // 2
        half_width = stone_width // 2
        x1, x2 = x - half_length, x + half_length
        y1, y2 = y - half_width, y + half_width
        height_field[x1:x2, y1:y2] = stone_height

    # Define the starting area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    for i in range(1, 8):
        if i % 3 == 1:
            # Add a balance beam
            dx = np.random.randint(-m_to_idx(0.1), m_to_idx(0.1))
            cur_x += dx
            add_beam(cur_x, cur_x + beam_length, mid_y)
            goals[i] = [cur_x + beam_length // 2, mid_y]
            cur_x += beam_length + gap_length
        elif i % 3 == 2:
            # Add a stepping stone
            dx = np.random.randint(-m_to_idx(0.1), m_to_idx(0.1))
            dy = np.random.randint(-m_to_idx(0.2), m_to_idx(0.2))
            cur_x += dx
            add_stepping_stone(cur_x, mid_y + dy)
            goals[i] = [cur_x + m_to_idx(0.5), mid_y + dy]
            cur_x += stone_length + gap_length
        else:
            # Add a platform
            dx = np.random.randint(-m_to_idx(0.1), m_to_idx(0.1))
            cur_x += dx
            add_platform(cur_x, cur_x + platform_length, mid_y)
            goals[i] = [cur_x + platform_length // 2, mid_y]
            cur_x += platform_length + gap_length

    # Set remaining area flat
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_8(length, width, field_resolution, difficulty):
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

def set_terrain_9(length, width, field_resolution, difficulty):
    """A combination of narrow beams, jumping gaps, and climbing platforms to challenge the quadruped's balance, agility, and jumping ability."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Dimensions and parameters for obstacles
    beam_length = 1.0 - 0.3 * difficulty    # Between 0.7m and 1.0m
    beam_length = m_to_idx(beam_length)
    beam_width = 0.3 + 0.2 * difficulty      # Between 0.3m and 0.5m
    beam_width = m_to_idx(beam_width)
    platform_length = 1.0 - 0.4 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 0.8 + 0.3 * difficulty
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.2 + 0.4 * difficulty
    gap_length = 0.3 + 0.5 * difficulty     # Between 0.3m and 0.8m
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, mid_y):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        beam_height = 0.1
        height_field[x1:x2, y1:y2] = beam_height
    
    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    # Define the starting area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    for i in range(1, 8):
        if i % 3 == 1:
            # Add a jumping gap
            cur_x += gap_length
            goals[i] = [cur_x + m_to_idx(0.5), mid_y]
        elif i % 3 == 2:
            # Add a beam
            dx = np.random.uniform(-0.1, 0.1)  # Slight variations
            cur_x += max(beam_length + m_to_idx(dx), gap_length)
            add_beam(cur_x, cur_x + beam_length, mid_y)
            goals[i] = [cur_x + beam_length // 2, mid_y]
        else:
            # Add a platform
            dx = np.random.uniform(-0.1, 0.1)  # Slight variations
            cur_x += max(platform_length + m_to_idx(dx), gap_length)
            add_platform(cur_x, cur_x + platform_length, mid_y)
            goals[i] = [cur_x + platform_length // 2, mid_y]

    # Set remaining area flat
    height_field[cur_x:, :] = 0

    return height_field, goals

# INSERT TERRAIN FUNCTION DEFINITIONS HERE
