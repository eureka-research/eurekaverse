
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
    """Narrow paths and inclined planes for testing balance and climbing."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    narrow_path_width = 0.4
    narrow_path_width = m_to_idx(narrow_path_width)
    max_incline_height = 0.25 + 0.25 * difficulty  # Up to 0.5 meters
    incline_length = 2.0  # 2 meters
    incline_length = m_to_idx(incline_length)
    flat_length = 1.5 - 0.5 * difficulty  # Between 1.5 to 1 meter
    
    mid_y = m_to_idx(width) // 2

    def add_narrow_path(start_x, end_x, mid_y):
        half_width = narrow_path_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = 0  # Flat path at ground level

    def add_incline(start_x, end_x, mid_y, max_height):
        incline_slope = max_height / (end_x - start_x)
        half_width = narrow_path_width // 2
        for i in range(start_x, end_x):
            height_field[i, mid_y - half_width:mid_y + half_width] = (i - start_x) * incline_slope

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
    alternating = True  # To alternate between narrow path and incline
    for i in range(6):  # Creating 6 segments
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        if alternating:
            end_x = cur_x + m_to_idx(flat_length) + dx
            add_narrow_path(cur_x, end_x, mid_y + dy)
            # adding goals at the end of narrow paths
            goals[i+1] = [cur_x + (m_to_idx(flat_length) + dx) / 2, mid_y + dy]
        else:
            end_x = cur_x + incline_length + dx
            max_height = max_incline_height * (np.random.rand() + 0.5)  # Random height up to defined max
            add_incline(cur_x, end_x, mid_y + dy, max_height)
            # adding goals at the end of inclines
            goals[i+1] = [cur_x + (incline_length + dx) / 2, mid_y + dy]
        
        cur_x = end_x
        alternating = not alternating  # Switch between path and incline

    # Add final goal at the edge of the terrain, fill in the remaining gap
    final_length = m_to_idx(length) - cur_x
    height_field[cur_x:, :] = 0
    goals[-1] = [cur_x + final_length / 2, mid_y]

    return height_field, goals

def set_terrain_1(length, width, field_resolution, difficulty):
    """Narrow bridges of varying heights for the robot to cross."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up bridge dimensions
    bridge_length = m_to_idx(1.5)  # Fixed length of bridges in quantized units
    min_bridge_width = 0.4  # Minimum width of bridges
    max_bridge_width = 1.0 - 0.3 * difficulty  # Width decreases with difficulty
    min_bridge_height = 0.05  # Minimum height of bridges
    max_bridge_height = 0.3 * difficulty  # Height increases with difficulty

    mid_y = m_to_idx(width / 2)
    
    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)
    
    def add_bridge(start_x, end_x, mid_y, width, height):
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(6):  # Set up 6 bridges
        bridge_width = m_to_idx(np.random.uniform(min_bridge_width, max_bridge_width))
        bridge_height = np.random.uniform(min_bridge_height, max_bridge_height)

        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        add_bridge(cur_x, cur_x + bridge_length + dx, mid_y + dy, bridge_width, bridge_height)
        
        # Put goal in the center of the bridge
        goals[i+1] = [cur_x + (bridge_length + dx) // 2, mid_y + dy]
        
        # Add gap
        cur_x += bridge_length + dx + m_to_idx(0.1 + 0.3 * difficulty)

    # Add final goal
    goals[-1] = [m_to_idx(length) - m_to_idx(0.5), mid_y]
    
    # Ensure last bridge and goal is walkable
    height_field[cur_x:, :] = 0

    return height_field, goals


def set_terrain_2(length, width, field_resolution, difficulty):
    """Narrow beams and wider platforms for precision and control tests."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up beam and platform dimensions
    beam_width = 0.4  # Narrow beams for precision
    beam_width = m_to_idx(beam_width)
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.2, 1.8)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.05, 0.3 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_beam(x, y, length):
        x2 = x + length
        y1, y2 = y - beam_width // 2, y + beam_width // 2
        height_field[x:x2, y1:y2] = platform_height

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = platform_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Starting platform
    platform_height = np.random.uniform(platform_height_min, platform_height_max)
    start_x = spawn_length
    end_x = start_x + platform_length
    add_platform(start_x, end_x, mid_y)
    current_x = end_x
    
    # Set goals and obstacles
    goals[1] = [(start_x + end_x)//2, mid_y]  # First goal on starting platform

    for i in range(2, 8):  # Set up 7 obstacles (beams and platforms)
        obstacle_type = random.choice(["beam", "platform"])
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        platform_height = np.random.uniform(platform_height_min, platform_height_max)

        if obstacle_type == "beam":
            beam_length = m_to_idx(1.0 + 0.5 * difficulty)
            add_beam(current_x + dx, mid_y + dy, beam_length)
            goals[i] = [current_x + dx + beam_length // 2, mid_y + dy]
            current_x += dx + beam_length
        
        elif obstacle_type == "platform":
            gap_length = m_to_idx(0.5 + 0.5 * difficulty)
            start_x = current_x + dx + gap_length
            end_x = start_x + platform_length
            add_platform(start_x, end_x, mid_y + dy)
            goals[i] = [(start_x + end_x)//2, mid_y + dy]
            current_x = end_x + dx

    return height_field, goals

def set_terrain_3(length, width, field_resolution, difficulty):
    """Urban environment with benches, ramps, and stair-like elevations for the robot to navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int32) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    
    # Set up obstacle dimensions
    bench_length = m_to_idx(1.0)
    bench_width = m_to_idx(0.4)
    bench_height = 0.2 + 0.2 * difficulty
    
    ramp_length = m_to_idx(1.0)
    ramp_width = m_to_idx(1.0)
    ramp_height = 0.1 + 0.2 * difficulty
    
    stair_steps = int(3 + 3 * difficulty)
    stair_height = 0.05 + 0.05 * difficulty
    stair_step_height = stair_height / stair_steps
    
    stair_depth = m_to_idx(0.2)
    stair_width = m_to_idx(1.0)
    
    mid_y = m_to_idx(width) // 2

    def add_bench(x_start, y_start, height):
        x_end = x_start + bench_length
        y_end = y_start + bench_width
        height_field[x_start:x_end, y_start:y_end] = height

    def add_ramp(x_start, y_start, height):
        x_end = x_start + ramp_length
        y_end = y_start + ramp_width
        for x in range(x_start, x_end):
            ramp_slope = height / (ramp_length - 1)
            height_field[x, y_start:y_end] = ramp_slope * (x - x_start)
    
    def add_stairs(x_start, y_start):
        for step in range(stair_steps):
            x_end = x_start + stair_depth
            y_end = y_start + stair_width
            height = stair_step_height * (step + 1)
            height_field[x_start:x_end, y_start:y_end] = height
            x_start = x_end

    # Set initial flat area
    flat_length = m_to_idx(2)
    height_field[:flat_length, :] = 0

    # Initial goal
    goals[0] = [flat_length - m_to_idx(0.5), mid_y]

    # Add random arrangement of benches, ramps, and stairs
    current_x = flat_length
    obstacle_types = ['bench', 'ramp', 'stairs']
    
    for i in range(1, 8):
        obstacle = random.choice(obstacle_types)

        if obstacle == 'bench':
            y_pos = mid_y - bench_width // 2
            add_bench(current_x, y_pos, bench_height)
            goals[i] = [current_x + bench_length // 2, mid_y]
            current_x += bench_length + m_to_idx(0.2)  # Add a small gap between obstacles

        elif obstacle == 'ramp':
            y_pos = mid_y - ramp_width // 2
            add_ramp(current_x, y_pos, ramp_height)
            goals[i] = [current_x + ramp_length // 2, mid_y]
            current_x += ramp_length + m_to_idx(0.2)  # Add a small gap between obstacles
   
        elif obstacle == 'stairs':
            y_pos = mid_y - stair_width // 2
            stair_length = stair_depth * stair_steps
            add_stairs(current_x, y_pos)
            goals[i] = [current_x + stair_length // 2, mid_y]
            current_x += stair_length + m_to_idx(0.2)  # Add a small gap between obstacles

    # Fill in flat ground after the last obstacle and set the final goal
    height_field[current_x:, :] = 0
    goals[-1] = [current_x + m_to_idx(0.5), mid_y]

    return height_field, goals

def set_terrain_4(length, width, field_resolution, difficulty):
    """Series of narrow raised beams and paths for balance and maneuvering."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Narrow raised beams dimensions
    path_width = 0.3 + 0.3 * difficulty  # wider paths for easier difficulty
    path_width = m_to_idx(path_width)
    path_height = 0.2 + 0.3 * difficulty
    gap_length = 0.1 + 0.4 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_path(start_x, end_x, mid_y, height):
        half_width = path_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

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
    for i in range(6):  # Set up 6 narrow paths/beams
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        path_length = m_to_idx(1.0 + 0.5 * difficulty)
        add_path(cur_x, cur_x + path_length + dx, mid_y + dy, path_height)

        # Put goal in the center of the path
        goals[i+1] = [cur_x + (path_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += path_length + dx + gap_length
    
    # Add final goal after the last path, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_5(length, width, field_resolution, difficulty):
    """Stepped platforms and narrow beams for the robot to navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Initialize parameters
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.6)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.05, 0.2 + 0.3 * difficulty
    gap_length = 0.1 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)
    
    beam_width = max(0.4, 0.6 - 0.4 * difficulty)
    beam_width = m_to_idx(beam_width)
    beam_length = 1.0 + 1.5 * difficulty
    beam_length = m_to_idx(beam_length)

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_beam(start_x, end_x, mid_y):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        beam_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = beam_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    mid_y = m_to_idx(width / 2)

    # Set flat spawn area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Starting from the initial spawn point
    cur_x = spawn_length
    step_count = 0
    
    while cur_x < m_to_idx(length) - beam_length - gap_length - 1 and step_count < 7:
        if step_count % 2 == 0:  # Add platforms
            dx = np.random.randint(dx_min // 2, dx_max // 2)
            dy = np.random.randint(dy_min // 2, dy_max // 2)
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[step_count + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
            cur_x += platform_length + dx + gap_length
        else:  # Add beams
            dx = np.random.randint(dx_min // 2, dx_max // 2)
            dy = np.random.randint(dy_min // 2, dy_max // 2)
            add_beam(cur_x, cur_x + beam_length + dx, mid_y + dy)
            goals[step_count + 1] = [cur_x + (beam_length + dx) / 2, mid_y + dy]
            cur_x += beam_length + dx + gap_length
        step_count += 1

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_6(length, width, field_resolution, difficulty):
    """Stepping stones for the robot to navigate, requiring precise movements and small jumps."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define stone dimensions
    stone_length = 0.4 + (0.6 * difficulty)  # Stones get larger with difficulty
    stone_length = m_to_idx(stone_length)
    stone_width = np.random.uniform(0.4, 0.8)  # Random width between 0.4m and 0.8m
    stone_width = m_to_idx(stone_width)
    stone_height_min, stone_height_max = 0.05, 0.3
    gap_length = 0.2 + (0.5 * difficulty)  # Gaps get larger with difficulty
    gap_length = m_to_idx(gap_length)

    spawn_area_length = m_to_idx(2)
    mid_y = m_to_idx(width / 2)

    def add_stone(start_x, mid_y):
        half_width = stone_width // 2
        x1, x2 = start_x, start_x + stone_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        stone_height = np.random.uniform(stone_height_min, stone_height_max) * difficulty
        height_field[x1:x2, y1:y2] = stone_height

    # Set spawn area to flat ground
    height_field[0:spawn_area_length, :] = 0
    goals[0] = [m_to_idx(1), mid_y]  # First goal at spawn

    cur_x = spawn_area_length
    dx_min, dx_max = -0.2, 0.2  # Random offset for stones
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    for i in range(6):  # Setup 6 stones
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_stone(cur_x + dx, mid_y + dy)

        # Place goal in the center of the stone
        goals[i+1] = [cur_x + dx + stone_length / 2, mid_y + dy]

        # Create gap for next stone
        cur_x += stone_length + gap_length

    # Add final goal just past the last stone
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    return height_field, goals

def set_terrain_7(length, width, field_resolution, difficulty):
    """Stepping stones for the quadruped to navigate across, testing precise balancing and hopping."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up stepping stone dimensions
    stone_length = 0.4
    stone_width = 0.4
    stone_length = m_to_idx(stone_length)
    stone_width = m_to_idx(stone_width)
    stone_height_min = 0.1 + 0.1 * difficulty  # minimum stone height
    stone_height_max = 0.2 + 0.2 * difficulty  # maximum stone height
    gap_length = 0.2 + 0.5 * difficulty  # distance between stones
    gap_length = m_to_idx(gap_length)

    spawn_length = m_to_idx(2)
    
    # Set spawn area to flat ground
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), m_to_idx(width) // 2]  

    cur_x = spawn_length
    cur_y = m_to_idx(width) // 2

    for i in range(1, 8):  # Set up 7 stepping stones
        step_height = np.random.uniform(stone_height_min, stone_height_max)
        x1, x2 = cur_x, cur_x + stone_length
        y1, y2 = cur_y - stone_width // 2, cur_y + stone_width // 2

        # Add the stepping stone
        height_field[x1:x2, y1:y2] = step_height

        # Set goal at the center of the new stone
        goals[i] = [(x1 + x2) // 2, cur_y]

        # Move to the next stone position
        if i < 7:  # Don't add gaps after the last stone
            cur_x += stone_length + gap_length
            cur_y += random.choice([-gap_length, gap_length])  # Randomize vertical shift of stones

    return height_field, goals

def set_terrain_8(length, width, field_resolution, difficulty):
    """Series of hurdles to test the quadruped's jumping ability and coordination."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Constants and terrain boundaries
    length_idx, width_idx = m_to_idx(length), m_to_idx(width)
    spawn_length = m_to_idx(2)
    goal_spacing = length_idx // 8  # Spread goals evenly over the course length
    mid_y = width_idx // 2

    # Set up hurdle dimensions
    hurdle_length = m_to_idx(0.4)
    hurdle_width = m_to_idx(0.8)
    hurdle_gap = m_to_idx(1.0 - 0.6 * difficulty)  # Increase gap size based on difficulty
    hurdle_height_min, hurdle_height_max = 0.1, 0.2 + 0.1 * difficulty

    # Nested function to add hurdles
    def add_hurdle(start_x, mid_y):
        half_width = hurdle_width // 2
        y1, y2 = mid_y - half_width, mid_y + half_width
        hurdle_height = np.random.uniform(hurdle_height_min, hurdle_height_max)
        height_field[start_x:start_x + hurdle_length, y1:y2] = hurdle_height

    # Set spawn area to flat ground
    height_field[:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at the spawn

    # Place hurdles and corresponding goals
    cur_x = spawn_length
    for i in range(1, 8):
        add_hurdle(cur_x, mid_y)
        goals[i] = [cur_x + hurdle_length + hurdle_gap // 2, mid_y]  # Goals in the middle of gaps between hurdles
        cur_x += hurdle_length + hurdle_gap

    # Ensure the last part of the terrain remains flat after the final hurdle
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_9(length, width, field_resolution, difficulty):
    """Narrow elevated walkways with varying heights and a final wide platform."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    
    # Calculation helper
    def add_elevated_walkway(start_x, end_x, y_center, width, height):
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = y_center - half_width, y_center + half_width
        height_field[x1:x2, y1:y2] = height

    # Set the width and height of the narrow walkway based on difficulty
    narrow_walkway_width = 0.4 + 0.4 * (1 - difficulty)  # from 0.8 to 0.4 meters
    narrow_walkway_width = m_to_idx(narrow_walkway_width)
    narrow_walkway_height_min = 0.2 * difficulty
    narrow_walkway_height_max = 0.4 * difficulty
    
    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    mid_y = m_to_idx(width) // 2
    goals[0] = [spawn_length, mid_y]

    # Add narrow elevated walkways
    cur_x = spawn_length
    length_per_walkway = m_to_idx(1)  # each walkway is 1m long
    for i in range(6):
        # Random height within the specified range based on difficulty
        height = np.random.uniform(narrow_walkway_height_min, narrow_walkway_height_max)
        add_elevated_walkway(cur_x, cur_x + length_per_walkway, mid_y, narrow_walkway_width, height)
        
        # Put goal in the middle of the current walkway
        goals[i+1] = [cur_x + length_per_walkway / 2, mid_y]
        
        # Move to the next position (including some gap to challenge jumping)
        cur_x += length_per_walkway + m_to_idx(0.1 + 0.1 * difficulty)
    
    # Final wide platform
    wide_platform_length = m_to_idx(1.5)
    wide_platform_width = m_to_idx(1.5)
    wide_platform_height = narrow_walkway_height_max
    add_elevated_walkway(cur_x, cur_x + wide_platform_length, mid_y, wide_platform_width, wide_platform_height)
    
    goals[-1] = [cur_x + wide_platform_length / 2, mid_y]
    return height_field, goals

# INSERT TERRAIN FUNCTION DEFINITIONS HERE