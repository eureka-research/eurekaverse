
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
    """Alternating high steps and low platforms for the robot to jump across and climb."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set dimensions for high steps and low platforms
    high_step_height_min, high_step_height_max = 0.15 + 0.1 * difficulty, 0.25 + 0.2 * difficulty
    low_platform_height_min, low_platform_height_max = 0.0, 0.1 * difficulty
    step_length, platform_length = 0.8 + 0.2 * difficulty, 1.2 - 0.2 * difficulty
    step_length, platform_length = m_to_idx(step_length), m_to_idx(platform_length)
    gap_length = 0.2 + 0.2 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_step(start_x, height):
        x1, x2 = start_x, start_x + step_length
        y1, y2 = mid_y - m_to_idx(0.64), mid_y + m_to_idx(0.64)  # Width set to 1.28 meters
        height_field[x1:x2, y1:y2] = height

    def add_platform(start_x, height):
        x1, x2 = start_x, start_x + platform_length
        y1, y2 = mid_y - m_to_idx(1.0), mid_y + m_to_idx(1.0)  # Width set to 2 meters
        height_field[x1:x2, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0.0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    for i in range(3):  # Create 3 high steps
        high_step_height = np.random.uniform(high_step_height_min, high_step_height_max)
        low_platform_height = np.random.uniform(low_platform_height_min, low_platform_height_max)
        
        # Add alternating high step and low platform
        add_step(cur_x, high_step_height)
        goals[2 * i + 1] = [cur_x + step_length // 2, mid_y]
        cur_x += step_length + gap_length
        
        add_platform(cur_x, low_platform_height)
        goals[2 * i + 2] = [cur_x + platform_length // 2, mid_y]
        cur_x += platform_length + gap_length

    # Final low platform with goal
    add_platform(cur_x, low_platform_height_min)
    goals[7] = [cur_x + platform_length // 2, mid_y]

    return height_field, goals

def set_terrain_1(length, width, field_resolution, difficulty):
    """Narrow ledges with alternating heights for the robot to balance and navigate across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define parameters for platforms and gaps
    platform_length_min = 0.8 - 0.25 * difficulty
    platform_length_max = 1.2 - 0.1 * difficulty
    platform_width = 0.4 + 0.05 * difficulty
    platform_height_min = 0.0 + 0.2 * difficulty
    platform_height_max = 0.1 + 0.3 * difficulty
    gap_length_min = 0.1 + 0.05 * difficulty
    gap_length_max = 0.3 + 0.2 * difficulty

    platform_length_min, platform_length_max = m_to_idx([platform_length_min, platform_length_max])
    platform_width = m_to_idx(platform_width)
    gap_length_min, gap_length_max = m_to_idx([gap_length_min, gap_length_max])

    mid_y = m_to_idx(width) // 2
    half_width = platform_width // 2

    def add_platform(start_x, end_x, mid_y, height):
        """Adds a platform with a specified height."""
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[start_x:end_x, y1:y2] = height

    dx_offset = m_to_idx(0.1)
    dy_offset_min, dy_offset_max = m_to_idx([-0.2, 0.2])

    # Set spawn area to flat ground and the first goal
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(6):
        platform_length = np.random.randint(platform_length_min, platform_length_max)
        height = np.random.uniform(platform_height_min, platform_height_max)

        dy_offset = np.random.randint(dy_offset_min, dy_offset_max)
        add_platform(cur_x, cur_x + platform_length, mid_y + dy_offset, height)

        # Place goal at the middle of the platform
        goals[i+1] = [cur_x + platform_length // 2, mid_y + dy_offset]

        # Add a gap before the next platform
        gap_length = np.random.randint(gap_length_min, gap_length_max)
        cur_x += platform_length + gap_length

    # Ensure the final section is reachable
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_2(length, width, field_resolution, difficulty):
    """Serpentine pathways with varying heights and narrow bridges to test the robot's turning and balance abilities."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Setup parameters for serpentine pathways and bridges
    pathway_width = 0.4 + 0.6 * (1 - difficulty)
    pathway_width = m_to_idx(pathway_width)
    pathway_height_min, pathway_height_max = 0.1 * difficulty, 0.4 * difficulty
    bridge_length = 1.0 - 0.7 * difficulty
    bridge_length = m_to_idx(bridge_length)
    bridge_height_min, bridge_height_max = 0.2 * difficulty, 0.5 * difficulty

    y_center = m_to_idx(width / 2)
    serpentine_amplitude = m_to_idx(0.5 + 1.5 * difficulty)
    serpentine_frequency = 3 + 5 * difficulty

    def add_pathway_pattern(start_x, end_x, y_center, serpentine_amplitude, serpentine_frequency):
        half_width = pathway_width // 2
        for x in range(start_x, end_x):
            offset = int(serpentine_amplitude * np.sin(serpentine_frequency * 2 * np.pi * (x - start_x) / (end_x - start_x)))
            y1, y2 = y_center + offset - half_width, y_center + offset + half_width
            pathway_height = np.random.uniform(pathway_height_min, pathway_height_max)
            height_field[x, y1:y2] = pathway_height

    def add_bridge(start_x, start_y, end_x, end_y):
        if start_x > end_x or start_y > end_y:
            return
        height_diff = np.random.uniform(bridge_height_min, bridge_height_max)
        bridge_slope = np.linspace(0, height_diff, num=end_x - start_x)
        mid_y = (start_y + end_y) // 2
        for x in range(start_x, end_x):
            height_field[x, mid_y-2:mid_y+2] = bridge_slope[x-start_x]

    dx_min, dx_max = m_to_idx(-0.05), m_to_idx(0.05)
    dy_min, dy_max = m_to_idx(-0.2), m_to_idx(0.2)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), y_center]

    # Add serpentine pathways
    cur_x = spawn_length
    section_length = m_to_idx(2)
    for i in range(4):  # Four primary sections
        next_x = cur_x + section_length
        dy = np.random.randint(dy_min, dy_max)
        add_pathway_pattern(cur_x, next_x, y_center + dy, serpentine_amplitude, serpentine_frequency)
        goals[i+1] = [cur_x + section_length // 2, y_center + dy]
        cur_x = next_x + m_to_idx(0.1)

    # Add narrow bridges connecting pathways
    for i in range(4, 7):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_bridge(cur_x, y_center + dy, cur_x + bridge_length, y_center + dy)
        goals[i+1] = [cur_x + bridge_length // 2, y_center + dy]
        cur_x += bridge_length + m_to_idx(0.1)

    # Add final goal behind the last section of serpentine pathway or bridge
    goals[-1] = [cur_x + m_to_idx(0.5), y_center]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_3(length, width, field_resolution, difficulty):
    """Narrow beams, varying width platforms, and slopes to test balance, precision, and incline traversal."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define the size parameters based on difficulty
    min_beam_width = 0.4 + 0.1 * difficulty
    max_beam_width = 1.0 - 0.2 * difficulty
    min_platform_width = 1.0 + 0.2 * difficulty
    max_platform_width = 2.0 - 0.2 * difficulty
    min_height = 0.1 * difficulty
    max_height = 0.5 * difficulty
    gap_min = 0.2
    gap_max = 1.0

    mid_y = m_to_idx(width / 2)

    def add_beam_or_platform(start_x, end_x, mid_y, platform_width, height):
        half_width = platform_width // 2
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

    for i in range(6):  # Set up 6 obstacles
        # Determine if this is a beam, wide platform, or inclined ramp
        if i % 2 == 0:  # Use beams for even indices
            platform_width = np.random.uniform(min_beam_width, max_beam_width)
        else:  # Use wide platforms for odd indices
            platform_width = np.random.uniform(min_platform_width, max_platform_width)

        platform_length = 1.0 + 0.4 * difficulty
        platform_length = m_to_idx(platform_length)
        platform_height = np.random.uniform(min_height, max_height)
        
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        add_beam_or_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, m_to_idx(platform_width), platform_height)

        # Place a goal at each obstacle
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Create a gap between platforms
        gap_length = np.random.uniform(gap_min, gap_max) * difficulty + 0.1
        gap_length = m_to_idx(gap_length)

        cur_x += platform_length + dx + gap_length

    # Add final goal behind the last platform, filling in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_4(length, width, field_resolution, difficulty):
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

def set_terrain_5(length, width, field_resolution, difficulty):
    """Combination of staircases, ramps, and small gaps to test climbing and jumping skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform, staircase, and ramp dimensions
    platform_length = 1.0 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.2, 1.6)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.2 + 0.4 * difficulty
    
    ramp_length = 1.2 - 0.3 * difficulty
    ramp_length = m_to_idx(ramp_length)
    ramp_width = platform_width
    ramp_height = 0.2 + 0.4 * difficulty

    gap_length = 0.4 + 0.3 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_ramp(start_x, end_x, mid_y, direction):
        half_width = ramp_width // 2
        height = np.linspace(0, ramp_height, end_x - start_x)
        if direction == 'down':
            height = height[::-1]
        for i in range(mid_y - half_width, mid_y + half_width):
            height_field[start_x:end_x, i] = height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length

    # Create mixed obstacles
    for i in range(6):
        # Randomly decide the obstacle type
        obstacle_type = np.random.choice(['platform', 'ramp_up', 'ramp_down'])

        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        if obstacle_type == 'platform':
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
            cur_x += platform_length + dx + gap_length
        elif obstacle_type == 'ramp_up':
            add_ramp(cur_x, cur_x + ramp_length + dx, mid_y + dy, 'up')
            goals[i + 1] = [cur_x + (ramp_length + dx) / 2, mid_y + dy]
            cur_x += ramp_length + dx + gap_length
        elif obstacle_type == 'ramp_down':
            add_ramp(cur_x, cur_x + ramp_length + dx, mid_y + dy, 'down')
            goals[i + 1] = [cur_x + (ramp_length + dx) / 2, mid_y + dy]
            cur_x += ramp_length + dx + gap_length

    # Add final goal behind the last obstacle
    goals[7] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_6(length, width, field_resolution, difficulty):
    """Alternating narrow walkways and wider platforms testing the robot's balance and navigation."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    length_idx = m_to_idx(length)
    width_idx = m_to_idx(width)
    height_field = np.zeros((length_idx, width_idx))
    goals = np.zeros((8, 2))

    narrow_walkway_width = 0.4 + 0.1 * difficulty  # Narrower walkways
    narrow_walkway_width = m_to_idx(narrow_walkway_width)
    platform_width = np.random.uniform(1.0, 1.5)  # Wider platforms
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.2 * difficulty, 0.4 * difficulty

    slope_length = 0.9 - 0.3 * difficulty
    slope_length = m_to_idx(slope_length)

    mid_y = width_idx // 2

    def add_narrow_walkway(start_x, end_x, mid_y):
        half_width = narrow_walkway_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = np.random.uniform(platform_height_min, platform_height_max)

    def add_wide_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = np.random.uniform(platform_height_min, platform_height_max)

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(1, 8):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        if i % 2 == 1:
            # Add narrow walkway
            add_narrow_walkway(cur_x, cur_x + slope_length + dx, mid_y + dy)
        else:
            # Add wide platform
            add_wide_platform(cur_x, cur_x + slope_length + dx, mid_y + dy)

        goals[i] = [cur_x + (slope_length + dx) / 2, mid_y + dy]
        cur_x += slope_length + dx  # No large gaps to reduce edge violations

    return height_field, goals

def set_terrain_7(length, width, field_resolution, difficulty):
    """A series of alternating steps and tilted platforms to test precise foot placement and balance in varied terrain."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Terrain and obstacle configurations
    step_height_base = 0.1
    step_height_var = 0.15 * difficulty
    step_length = 0.5
    platform_length = 1.2 - 0.5 * difficulty
    platform_width = 0.6 + 0.5 * difficulty
    platform_tilt_max = 0.1 + 0.3 * difficulty
    gap_length = 0.3 * difficulty

    step_length = m_to_idx(step_length)
    platform_length = m_to_idx(platform_length)
    platform_width = m_to_idx(platform_width)
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_step(start_x, height):
        width = m_to_idx(0.8)
        half_width = width // 2
        x1, x2 = start_x, start_x + step_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_tilted_platform(start_x, end_x, mid_y, tilt_angle):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        tilt = np.linspace(0, tilt_angle, y2 - y1)
        tilt = tilt[None, :]  # Add a dimension for broadcasting to x
        height_field[x1:x2, y1:y2] = tilt

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    current_x = spawn_length

    # Place alternating steps and tilted platforms
    for i in range(3):
        # Step
        step_height = step_height_base + random.uniform(-step_height_var, step_height_var)
        add_step(current_x, step_height)
        goals[i+1] = [current_x + step_length // 2, mid_y]
        current_x += step_length

        # Gap
        current_x += gap_length

        # Tilted platform
        tilt_angle = random.uniform(0, platform_tilt_max)
        add_tilted_platform(current_x, current_x + platform_length, mid_y, tilt_angle)
        goals[i+4] = [current_x + platform_length // 2, mid_y]
        current_x += platform_length

        # Gap
        current_x += gap_length

    # Add final goal at the end
    goals[-1] = [m_to_idx(11.5), mid_y]
    height_field[m_to_idx(11):, :] = 0

    return height_field, goals

def set_terrain_8(length, width, field_resolution, difficulty):
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

def set_terrain_9(length, width, field_resolution, difficulty):
    """Mixed terrain with stepping stones, gaps, and varying height platforms for the quadruped to navigate."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Terrain and obstacle parameters
    step_length = 0.4
    step_length_idx = m_to_idx(step_length)
    step_width = 0.4 + 0.2 * difficulty
    step_width_idx = m_to_idx(step_width)
    step_height_min, step_height_max = 0.1, 0.25 + 0.2 * difficulty
    gap_length = 0.2 + 0.5 * difficulty
    gap_length_idx = m_to_idx(gap_length)

    platform_length = 0.8 - 0.2 * difficulty
    platform_length_idx = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.2)
    platform_width_idx = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.05 + 0.2 * difficulty, 0.1 + 0.3 * difficulty
    
    mid_y = m_to_idx(width) // 2

    def add_step(start_x, mid_y):
        half_width = step_width_idx // 2
        x1 = start_x
        x2 = start_x + step_length_idx
        y1 = mid_y - half_width
        y2 = mid_y + half_width
        step_height = np.random.uniform(step_height_min, step_height_max)
        height_field[x1:x2, y1:y2] = step_height

    def add_gap(start_x, mid_y):
        half_width = step_width_idx // 2
        x1 = start_x
        x2 = start_x + gap_length_idx
        y1 = mid_y - half_width
        y2 = mid_y + half_width
        height_field[x1:x2, y1:y2] = -0.2
    
    def add_platform(start_x, mid_y):
        half_width = platform_width_idx // 2
        x1 = start_x
        x2 = start_x + platform_length_idx
        y1 = mid_y - half_width
        y2 = mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]
    
    cur_x = spawn_length

    # Add a series of steps, gaps, and platforms
    for i in range(3):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_step(cur_x, mid_y + dy)
        goals[i + 1] = [cur_x + step_length_idx // 2, mid_y + dy]
        cur_x += step_length_idx + dx + gap_length_idx
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_gap(cur_x, mid_y + dy)
        cur_x += gap_length_idx + dx
    
    for i in range(3):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, mid_y + dy)
        goals[4 + i] = [cur_x + platform_length_idx // 2, mid_y + dy]
        cur_x += platform_length_idx + dx + gap_length_idx

    # Add final goal behind the last platform
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_10(length, width, field_resolution, difficulty):
    """Narrow beams with varying heights and orientations for balance and precise navigation."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up beam dimensions
    beam_width = 0.4  # The narrow dimension of the beam
    beam_length = 3.0  # The longer dimension of the beam
    beam_height_min, beam_height_max = 0.1, 0.4 * difficulty 

    beam_width = m_to_idx(beam_width)
    beam_length = m_to_idx(beam_length)
    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, y_pos, height):
        """Places a beam on the height_field at given position and with given dimensions."""
        half_width = beam_width // 2
        start_y = y_pos - half_width
        end_y = y_pos + half_width
        height_field[start_x:end_x, start_y:end_y] = height

    # Initial flat terrain/spawn area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at the end of the spawn area

    # Parameters for beam placement
    x_step = m_to_idx(1.5)
    beam_gap = m_to_idx(0.5)

    cur_x = spawn_length

    for i in range(6):  # Set up 6 beams
        beam_height = np.random.uniform(beam_height_min, beam_height_max)
        cur_y = mid_y + m_to_idx(np.random.uniform(-0.8, 0.8))  # Introduce slight variability in y-position

        add_beam(cur_x, cur_x + beam_length, cur_y, beam_height)
        goals[i+1] = [cur_x + beam_length // 2, cur_y]  # Goal in the center of the beam
        
        cur_x += beam_length + beam_gap

    # Final goal at the far end of the course
    goals[-1] = [cur_x + m_to_idx(1.0), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_11(length, width, field_resolution, difficulty):
    """Alternate moving platforms and stepping stones across a pit for the robot to jump and balance"""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up moving platform and stepping stone dimensions
    platform_length = 0.8 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 0.8 + 0.3 * difficulty  # Decrease width for harder steps
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.3 + 0.25 * difficulty
    gap_length = 0.5 + 0.4 * difficulty  # Increase gap length with difficulty
    gap_length = m_to_idx(gap_length)

    stepping_stone_length = 0.4  # Small stepping stones
    stepping_stone_length = m_to_idx(stepping_stone_length)
    stepping_stone_width = stepping_stone_length
    stepping_stone_height = 0.05 + 0.2 * difficulty  # Increase height with difficulty

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_stepping_stone(x, y):
        half_length = stepping_stone_length // 2
        half_width = stepping_stone_width // 2
        x1, x2 = x - half_length, x + half_length
        y1, y2 = y - half_width, y + half_width
        height_field[x1:x2, y1:y2] = stepping_stone_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at the end of the spawn area

    cur_x = spawn_length
    for i in range(3):  # Set up 3 moving platforms
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
        goals[i * 2 + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        cur_x += platform_length + dx + gap_length

        # Adding stepping stones in between
        for j in range(2):
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)
            stone_x = cur_x + j * stepping_stone_length * 2
            stone_y = mid_y + dy
            add_stepping_stone(stone_x, stone_y)
            goals[i * 2 + 2] = [stone_x, stone_y]

        cur_x += stepping_stone_length * 2

    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_12(length, width, field_resolution, difficulty):
    """A series of dynamic elevating platforms for the robot to navigate and jump across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions and properties
    platform_length_base = 1.0
    platform_length_variation = 0.3 * difficulty
    platform_width = np.random.uniform(1.0, 1.2)  # Slightly narrower platforms
    platform_width = m_to_idx(platform_width)
    platform_height_base = 0.2 * difficulty
    platform_height_variation = 0.3  # Increased height variation for difficulty
    gap_length_base = 0.2
    gap_length_variation = 0.5 * difficulty  # Variable gap length with difficulty
    gap_length = m_to_idx(gap_length_base + gap_length_variation)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height_offset):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = platform_height_base + height_offset
        height_field[x1:x2, y1:y2] = platform_height

    dx_min, dx_max = -0.2, 0.2  # Increased dx variation for complexity
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_variation = 0.4  # maintaining the dy variation
    dy_variation = m_to_idx(dy_variation)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Set remaining area to be a pit
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    for i in range(6):  # Set up 6 platforms
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(-dy_variation, dy_variation)

        platform_length = m_to_idx(platform_length_base + platform_length_variation)
        height_offset = np.random.uniform(0, platform_height_variation)
        
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, height_offset)
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        cur_x += platform_length + dx + gap_length

    # Add final goal behind the last platform
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_13(length, width, field_resolution, difficulty):
    """Combines larger gaps, angled ramps, and narrow bridges for balance, climbing and jumping."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length_min = m_to_idx(0.8 - 0.2 * difficulty)
    platform_length_max = m_to_idx(1.2 + 0.2 * difficulty)
    platform_height_min, platform_height_max = 0.1 + 0.3 * difficulty, 0.2 + 0.6 * difficulty
    bridge_width = m_to_idx(0.4 - 0.1 * difficulty)
    gap_length_min = m_to_idx(0.3 + 0.7 * difficulty)
    gap_length_max = m_to_idx(0.5 + 0.9 * difficulty)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        y1, y2 = mid_y - m_to_idx(0.5), mid_y + m_to_idx(0.5)
        height_field[start_x:end_x, y1:y2] = height

    def add_ramp(start_x, end_x, mid_y, direction, height):
        y1, y2 = mid_y - m_to_idx(0.5), mid_y + m_to_idx(0.5)
        ramp_height = np.linspace(0, height, y2 - y1)[::direction]
        ramp_height = ramp_height[None, :]
        height_field[start_x:end_x, y1:y2] = ramp_height

    def add_bridge(start_x, end_x, mid_y, width_idx):
        y1, y2 = mid_y - width_idx // 2, mid_y + width_idx // 2
        height_field[start_x:end_x, y1:y2] = platform_height_max

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    segment_names = ["platform", "gap", "ramp", "bridge", "ramp", "gap"]

    for i, segment in enumerate(segment_names):
        if segment == "platform":
            length = np.random.randint(platform_length_min, platform_length_max)
            height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, cur_x + length, mid_y, height)
            goals[i + 1] = [cur_x + length // 2, mid_y]
        elif segment == "gap":
            length = np.random.randint(gap_length_min, gap_length_max)
            cur_x += length
            height_field[cur_x, :] = -1.0  # Representing the gap as a lower height
        elif segment == "ramp":
            length = np.random.randint(platform_length_min, platform_length_max)
            height = np.random.uniform(platform_height_min, platform_height_max)
            direction = 1 if i % 2 == 0 else -1  # Alternate ramps
            add_ramp(cur_x, cur_x + length, mid_y, direction, height)
            goals[i + 1] = [cur_x + length // 2, mid_y]
        else:  # bridge
            length = np.random.randint(platform_length_min, platform_length_max)
            add_bridge(cur_x, cur_x + length, mid_y, bridge_width)
            goals[i + 1] = [cur_x + length // 2, mid_y]

        # Move to the next starting x position
        cur_x += length

    # Add goal at the end
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_14(length, width, field_resolution, difficulty):
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

def set_terrain_15(length, width, field_resolution, difficulty):
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

def set_terrain_16(length, width, field_resolution, difficulty):
    """A series of inclined and varied platforms for the quadruped to navigate and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and obstacle dimensions
    platform_length_base = 0.8 + 0.2 * difficulty
    platform_length_variation = 0.3 * difficulty
    platform_width_min, platform_width_max = 0.4, 0.8  # Narrower for more difficulty
    platform_height_min, platform_height_max = 0.1, 0.4 * difficulty
    gap_length_base = 0.2
    gap_length_variation = 0.5 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_platform_or_ramp(start_x, end_x, y_mid, height, is_ramp=False, direction=1):
        half_width = m_to_idx(np.random.uniform(platform_width_min, platform_width_max) / 2)
        x1, x2 = start_x, end_x
        y1, y2 = y_mid - half_width, y_mid + half_width
        
        if is_ramp:
            incline = np.linspace(0, height * direction, x2 - x1)[:, None]
            height_field[x1:x2, y1:y2] = incline + height_field[x1, y1:y1+1]
        else:
            height_field[x1:x2, y1:y2] = height

    def add_goal(start_x, end_x, y_mid):
        goals.append([(start_x + end_x) / 2, y_mid])

    dx_min, dx_max = -0.2, 0.2
    dy_variation = 0.4  # Max shift along y-axis

    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_variation = m_to_idx(dy_variation)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Initial platform after spawn flat area
    cur_x = spawn_length
    for i in range(6):  # Create a variety of platforms and ramps
        platform_length = m_to_idx(platform_length_base + platform_length_variation * np.random.random())
        gap_length = m_to_idx(gap_length_base + gap_length_variation * np.random.random())

        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(-dy_variation, dy_variation)
        
        is_ramp = (i % 2 == 0)  # every alternate platform is a ramp
        height = np.random.uniform(platform_height_min, platform_height_max)
        direction = (-1) ** i  # alternate inclination direction for ramp
        
        add_platform_or_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, height, is_ramp, direction)
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        cur_x += platform_length + dx + gap_length

    # Final goal past the last platform
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_17(length, width, field_resolution, difficulty):
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

def set_terrain_18(length, width, field_resolution, difficulty):
    """Combination of varied ramps, narrow bridges, and staggered platforms for increased challenge in climbing, balancing, and jumping."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Constants for obstacle dimensions
    platform_length = m_to_idx(1.0 - 0.2 * difficulty)
    platform_height = 0.2 * difficulty
    bridge_width = m_to_idx(0.4 * difficulty + 0.6)
    ramp_height = 0.25 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        y1, y2 = mid_y - m_to_idx(0.5), mid_y + m_to_idx(0.5)
        height_field[start_x:end_x, y1:y2] = height
    
    def add_ramp(start_x, end_x, mid_y, slope, direction):
        y1, y2 = mid_y - (slope * (end_x - start_x) // 2), mid_y + (slope * (end_x - start_x) // 2)
        if direction == 'up':
            height = np.linspace(0, ramp_height, end_x - start_x)
        else:
            height = np.linspace(ramp_height, 0, end_x - start_x)
        height_field[start_x:end_x, y1:y2] = height[:, None]

    def add_bridge(start_x, end_x, mid_y, width_idx):
        y1, y2 = mid_y - width_idx // 2, mid_y + width_idx // 2
        height_field[start_x:end_x, y1:y2] = platform_height

    def add_staggered_steps(start_x, end_x, mid_y):
        for i in range(start_x, end_x, m_to_idx(0.5)):
            step_height = np.random.uniform(0, platform_height)
            height_field[i:i + m_to_idx(0.5), mid_y - m_to_idx(0.25):mid_y + m_to_idx(0.25)] = step_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    obstacles = [
        {'type': 'platform', 'length': platform_length, 'height': platform_height},
        {'type': 'ramp', 'slope': 1, 'direction': 'up', 'length': platform_length},
        {'type': 'bridge', 'width': bridge_width, 'length': platform_length},
        {'type': 'steps', 'length': platform_length},
        {'type': 'ramp', 'slope': 1, 'direction': 'down', 'length': platform_length},
        {'type': 'platform', 'length': platform_length, 'height': platform_height}
    ]

    for i, obs in enumerate(obstacles, 1):
        if obs['type'] == 'platform':
            add_platform(cur_x, cur_x + obs['length'], mid_y, obs['height'])
        elif obs['type'] == 'ramp':
            add_ramp(cur_x, cur_x + obs['length'], mid_y, obs['slope'], obs['direction'])
        elif obs['type'] == 'bridge':
            add_bridge(cur_x, cur_x + obs['length'], mid_y, obs['width'])
        elif obs['type'] == 'steps':
            add_staggered_steps(cur_x, cur_x + obs['length'], mid_y)
        
        goals[i] = [cur_x + obs['length'] // 2, mid_y]
        cur_x += obs['length'] + m_to_idx(0.4 * difficulty)

    # Fill remaining area beyond the last obstacle and place final goal
    if cur_x < m_to_idx(length) - m_to_idx(1):
        add_platform(cur_x, m_to_idx(length), mid_y, 0)
    goals[-1] = [m_to_idx(11.5), mid_y]

    return height_field, goals

def set_terrain_19(length, width, field_resolution, difficulty):
    """Complex course with stepping stones, staggered platforms, and inclined ramps."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform dimensions and height range
    platform_length = 1.0
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.9, 1.2)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.1 * difficulty, 0.3 + 0.3 * difficulty

    gap_length = m_to_idx(0.3 + 0.6 * difficulty)
    
    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_stepping_stones(start_x, num_stones, mid_y):
        stone_length = m_to_idx(0.4)
        stone_width = m_to_idx(0.4)
        stone_height_range = 0.0 + 0.25 * difficulty, 0.1 + 0.35 * difficulty

        for i in range(num_stones):
            platform_height = np.random.uniform(*stone_height_range)
            step_x = start_x + i * (stone_length + gap_length)
            add_platform(step_x, step_x + stone_length, mid_y + (np.random.randint(-2, 3) * stone_width), platform_height)

    def add_ramp(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_slope = np.linspace(0, height, num=end_x - start_x)
        height_field[x1:x2, y1:y2] = ramp_slope[:, np.newaxis]

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0.0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    
    # Add first platform
    platform_height = np.random.uniform(platform_height_min, platform_height_max)
    add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)
    goals[1] = [cur_x + platform_length / 2, mid_y]
    cur_x += platform_length + gap_length

    # Add stepping stones
    add_stepping_stones(cur_x, 3, mid_y)  # 3 stepping stones
    goals[2] = [cur_x + platform_length, mid_y]

    cur_x += 3 * m_to_idx(0.4) + 3 * gap_length

    # Add staggered platform with narrow bridges
    stagger_x = [cur_x, cur_x + platform_length + gap_length, cur_x + 2 * (platform_length + gap_length)]
    stagger_y = [mid_y - m_to_idx(1), mid_y, mid_y + m_to_idx(1)]
    for x, y in zip(stagger_x, stagger_y):
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        add_platform(x, x + platform_length, y, platform_height)

    goals[3] = [stagger_x[-1] + platform_length / 2, stagger_y[-1]]
    cur_x = stagger_x[-1] + platform_length + gap_length

    # Add inclined ramp
    ramp_height = np.random.uniform(0.3 + 0.3 * difficulty, 0.5 + 0.5 * difficulty)
    add_ramp(cur_x, cur_x + platform_length, mid_y, ramp_height)
    goals[4] = [cur_x + platform_length / 2, mid_y]
    cur_x += platform_length + gap_length

    # Add final set of platforms
    for i in range(3):  # 3 platforms
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        add_platform(cur_x, cur_x + platform_length, mid_y + m_to_idx(i * 0.2), platform_height)
        goals[5 + i] = [cur_x + platform_length / 2, mid_y + m_to_idx(i * 0.2)]
        cur_x += platform_length + gap_length

    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals  # Return the desired terrain and goals

def set_terrain_20(length, width, field_resolution, difficulty):
    """Series of stepping stones of varying widths combined with ascending and descending platforms traversing pits."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_width_min = 0.4 + 0.1 * difficulty
    platform_width_max = 0.6 + 0.2 * difficulty
    platform_length_min = 0.4 + 0.1 * difficulty
    platform_length_max = 1.0 + 0.3 * difficulty
    step_height_min = 0.05 * difficulty
    step_height_max = 0.3 * difficulty
    gap_length_min = 0.2
    gap_length_max = 0.5 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = m_to_idx(np.random.uniform(platform_width_min, platform_width_max)) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = m_to_idx(-0.1), m_to_idx(0.1)
    dy_min, dy_max = m_to_idx(-0.2), m_to_idx(0.2)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Add platforms
    cur_x = spawn_length
    current_height = 0

    for i in range(7):
        platform_length = m_to_idx(np.random.uniform(platform_length_min, platform_length_max))
        current_gap = m_to_idx(np.random.uniform(gap_length_min, gap_length_max))
        next_height = current_height + np.random.uniform(step_height_min, step_height_max) * (-1 if i % 2 == 0 else 1)
        
        add_platform(cur_x, cur_x + platform_length, mid_y, current_height)
        
        goals[i + 1] = [cur_x + platform_length / 2, mid_y]

        cur_x += platform_length + current_gap
        current_height = next_height

    # Add final goal beyond last step
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_21(length, width, field_resolution, difficulty):
    """Obstacle course with staggered platforms and diagonal beams to test balance, climbing, and orientation adjustments."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and beam dimensions
    platform_length = 1.0 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.9, 1.2)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.3 * difficulty, 0.2 + 0.4 * difficulty

    beam_length = 1.2  # Slightly longer to increase difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = 0.4  # Narrow beams for balance
    beam_width = m_to_idx(beam_width)
    beam_height_min, beam_height_max = 0.2, 0.4 + 0.4 * difficulty

    gap_length = 0.2 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_beam(start_x, end_x, mid_y, slope_direction):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        beam_slope = np.linspace(0, slope_direction * (beam_height_max - beam_height_min), num=x2 - x1)
        height_field[x1:x2, y1:y2] = beam_slope[:, np.newaxis]

    dx_min, dx_max = -0.15, 0.15
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.25, 0.25
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0.0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    next_height = np.random.uniform(platform_height_min, platform_height_max)

    for i in range(4):  # First set 4 platforms in a staggered pattern
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, next_height)

        goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length
        next_height = np.random.uniform(platform_height_min, platform_height_max)

    previous_height = next_height

    for i in range(4, 7):  # Now set 3 diagonal beams for balance challenges
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        direction = (-1) ** i  # Alternate slope direction

        add_beam(cur_x, cur_x + beam_length + dx, mid_y + dy, direction)
        goals[i + 1] = [cur_x + (beam_length + dx) / 2, mid_y + dy]
        cur_x += beam_length + dx + gap_length
        previous_height = np.random.uniform(beam_height_min, beam_height_max)

    # Add final goal behind the last beam 
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0.0

    return height_field, goals

def set_terrain_22(length, width, field_resolution, difficulty):
    """Higher platforms, wider gaps, and lateral transitions to test robot's balance and navigation abilities."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set dimensions and positions for platforms and gaps
    platform_size = 1.0 - 0.3 * difficulty  # Platforms become smaller with difficulty
    platform_size_idx = m_to_idx(platform_size)
    platform_width = np.random.uniform(0.9, 1.2)
    platform_width_idx = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.15 * difficulty, 0.3 * difficulty  # Higher platforms
    gap_length = 0.3 + 0.5 * difficulty  # Wider gaps with difficulty
    gap_length_idx = m_to_idx(gap_length)

    mid_y = m_to_idx(width / 2)

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width_idx // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_beam(start_x, end_x, mid_y):
        beam_width = 0.4  # Narrow beam width
        beam_width_idx = m_to_idx(beam_width)
        half_width = beam_width_idx // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        beam_height = platform_height_max  # Consistent height for review
        height_field[x1:x2, y1:y2] = beam_height
        
    def add_ramp(start_x, end_x, mid_y, direction):
        """Adds a sloped ramp for the robot to ascend or descend."""
        half_width = platform_width_idx // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(platform_height_min, platform_height_max)
        slant = np.linspace(0, ramp_height, num=y2-y1)[::direction]
        slant = slant[None, :]
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = m_to_idx(2)
    
    # First platform to get started
    add_platform(cur_x, cur_x + platform_size_idx, mid_y)
    goals[1] = [cur_x + platform_size_idx // 2, mid_y]
    
    cur_x += platform_size_idx + gap_length_idx

    for i in range(2, 8, 2):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        # Add a beam obstacle
        add_beam(cur_x, cur_x + platform_size_idx + dx, mid_y + dy)
        goals[i] = [cur_x + (platform_size_idx + dx) // 2, mid_y + dy]
        cur_x += platform_size_idx + dx + gap_length_idx
        
        # Add a sideways-facing ramp
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        direction = (-1) ** i
        dy = dy * direction

        add_ramp(cur_x, cur_x + platform_size_idx + dx, mid_y + dy, direction)
        goals[i + 1] = [cur_x + (platform_size_idx + dx) // 2, mid_y + dy]
        cur_x += platform_size_idx + dx + gap_length_idx

    # Final flat area to end the course
    goals[7] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_23(length, width, field_resolution, difficulty):
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

def set_terrain_24(length, width, field_resolution, difficulty):
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

def set_terrain_25(length, width, field_resolution, difficulty):
    """Series of mid-width platforms, shallow ramps, and gaps to balance climbing, balancing, and jumping needs."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform and ramp dimensions
    platform_length = 1.2 - 0.2 * difficulty  # Slightly longer platforms
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.3)  # Wider platforms for less edge errors
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.1 * difficulty, 0.3 + 0.2 * difficulty  # Reasonable heights
    ramp_height_min, ramp_height_max = 0.1 + 0.2 * difficulty, 0.2 + 0.3 * difficulty
    gap_length = 0.2 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_ramp(start_x, end_x, mid_x, direction):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        slant = np.linspace(0, ramp_height, num=x2-x1)[::direction]
        slant = slant[:, None]  # Add a dimension for broadcasting to y
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.0, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set initial flat ground for spawning
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(5):  # Mix 5 platforms and ramps
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        if i % 2 == 0:  # Add platform
            platform_height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height)
        else:  # Add ramp
            direction = (-1) ** (i // 2)  # Alternate direction for ramps
            add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, direction)

        # Set goal location in the center of current feature
        goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Move to the next section
        cur_x += platform_length + dx + gap_length

    # Final goal behind the last platform
    goals[-2] = [cur_x, mid_y]
    
    # Ensure the final gap is realistic and has a clearance
    gap_for_last_platform = platform_length + dx + gap_length // 2
    cur_x += gap_for_last_platform
    height_field[cur_x - m_to_idx(0.1):, :] = 0
    
    goals[-1] = [cur_x, mid_y]

    return height_field, goals

def set_terrain_26(length, width, field_resolution, difficulty):
    """Series of stepping stones and undulating terrains to challenge the robot's balance and agility."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Setup stepping stone and undulating terrain dimensions
    stone_length = 0.6 - 0.2 * difficulty
    stone_length = m_to_idx(stone_length)
    stone_width = 0.6 - 0.2 * difficulty
    stone_width = m_to_idx(stone_width)
    stone_height_min, stone_height_max = 0.05 + 0.15 * difficulty, 0.15 + 0.3 * difficulty
    undulation_amplitude = 0.05 + 0.15 * difficulty
    
    gap_length_min = 0.3 + 0.4 * difficulty
    gap_length_min = m_to_idx(gap_length_min)
    gap_length_max = 0.5 + 0.6 * difficulty
    gap_length_max = m_to_idx(gap_length_max)
    
    mid_y = m_to_idx(width) // 2

    def add_stepping_stone(start_x, mid_y):
        half_length = stone_length // 2
        half_width = stone_width // 2
        x1, x2 = start_x - half_length, start_x + half_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        stone_height = np.random.uniform(stone_height_min, stone_height_max)
        height_field[x1:x2, y1:y2] = stone_height

    def add_undulation(start_x, end_x):
        x1, x2 = start_x, end_x
        y_indices = np.arange(0, m_to_idx(width))
        undulation_heights = undulation_amplitude * np.sin(np.linspace(0, 4 * np.pi, y_indices.size))
        height_field[x1:x2, :] += undulation_heights[np.newaxis, :]
    
    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    
    for i in range(3):  # Set up 3 stepping stones
        cur_x += np.random.randint(gap_length_min, gap_length_max)
        add_stepping_stone(cur_x, mid_y)

        # Put goal in the center of the stepping stone
        goals[i+1] = [cur_x, mid_y]
    
    cur_x += np.random.randint(gap_length_min, gap_length_max)
    segment_length = int(m_to_idx(12) // 3)
    
    for i in range(4, 7):  # Set up undulating terrain between stones
        add_undulation(cur_x, cur_x + segment_length)
        mid_y_shift = (-1)**i * m_to_idx(0.8)  # Alternate shifts to the undulating path
        cur_x = cur_x + segment_length
        goals[i] = [cur_x - segment_length // 2, mid_y + mid_y_shift]

    # Add final flat area
    final_length = m_to_idx(2)
    height_field[cur_x:cur_x + final_length, :] = 0
    # Set final goal
    goals[-1] = [cur_x + final_length - m_to_idx(0.5), mid_y]

    return height_field, goals

def set_terrain_27(length, width, field_resolution, difficulty):
    """Staggered stepping stones of varying heights and gaps to test agility and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up stepping stone dimensions and properties
    stone_length_min = 0.4
    stone_length_max = 1.2
    stone_width_min = 0.4
    stone_width_max = 1.0
    stone_height_min = 0.1 + 0.2 * difficulty
    stone_height_max = 0.3 + 0.4 * difficulty
    gap_min = 0.2
    gap_max = 0.6

    # Convert dimensions to indices
    stone_length_min_idx = m_to_idx(stone_length_min)
    stone_length_max_idx = m_to_idx(stone_length_max)
    stone_width_min_idx = m_to_idx(stone_width_min)
    stone_width_max_idx = m_to_idx(stone_width_max)
    gap_min_idx = m_to_idx(gap_min)
    gap_max_idx = m_to_idx(gap_max)

    mid_y = m_to_idx(width) // 2

    def add_stepping_stone(start_x, stone_length, stone_width, mid_y, stone_height):
        half_width = stone_width // 2
        end_x = start_x + stone_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[start_x:end_x, y1:y2] = stone_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    for i in range(6):  # Set up 6 stepping stones
        stone_length = random.randint(stone_length_min_idx, stone_length_max_idx)
        stone_width = random.randint(stone_width_min_idx, stone_width_max_idx)
        stone_height = random.uniform(stone_height_min, stone_height_max)
        
        add_stepping_stone(cur_x, stone_length, stone_width, mid_y, stone_height)
        
        # Put the goal at the center of each stone
        goals[i + 1] = [cur_x + stone_length // 2, mid_y]

        # Adding a gap between stones
        gap_length = random.randint(gap_min_idx, gap_max_idx)
        cur_x += stone_length + gap_length

    # Add the final goal at the end of the course
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_28(length, width, field_resolution, difficulty):
    """Alternating platforms with narrow bridges and zigzag paths for advanced navigation and balance testing."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    mid_y = m_to_idx(width / 2)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Initial platform parameters
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = m_to_idx(0.4)  # Narrow platform
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.3 + 0.5 * difficulty
    gap_length = 0.1 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    cur_x = spawn_length
    for i in range(6):
        dx = random.randint(-m_to_idx(0.1), m_to_idx(0.1))
        dy = random.randint(-m_to_idx(0.4), m_to_idx(0.4))
        platform_height = random.uniform(platform_height_min, platform_height_max)

        # Add platform
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height)
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Add narrow bridge or gap
        cur_x += platform_length + dx + gap_length
        if i % 2 == 1:  # Add narrow bridge every other platform
            bridge_length = m_to_idx(0.6 + 0.5 * difficulty)
            bridge_width = m_to_idx(0.2)
            bridge_mid_y = mid_y + random.randint(-m_to_idx(0.5), m_to_idx(0.5))
            height_field[cur_x:cur_x + bridge_length, bridge_mid_y - bridge_width//2:bridge_mid_y + bridge_width//2] = platform_height

            goals[i+1] = [cur_x + bridge_length // 2, bridge_mid_y]
            cur_x += bridge_length

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_29(length, width, field_resolution, difficulty):
    """Challenging balance on narrow beams with gaps and varying heights."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Parameters (increase obstacle complexity based on difficulty)
    platform_width_min, platform_width_max = 0.3, 0.5  # Narrower beams for balance testing
    gap_width = 0.4 + 0.6 * difficulty  # Increase gap width with difficulty
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.15 + 0.35 * difficulty

    platform_width_min, platform_width_max = m_to_idx([platform_width_min, platform_width_max])
    gap_width = m_to_idx(gap_width)
    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, length, width, height, mid_y, offset_y=0):
        half_width = width // 2
        height_field[start_x:start_x+length, mid_y - half_width + offset_y : mid_y + half_width + offset_y] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at the spawn point

    # Create terrain
    cur_x = spawn_length
    obstacle_count = 0

    while obstacle_count < 7:
        # Determine platform parameters
        platform_length = m_to_idx(0.8)
        platform_width = np.random.randint(platform_width_min, platform_width_max)
        platform_height = np.random.uniform(platform_height_min, platform_height_max)

        # Create platform
        add_platform(cur_x, platform_length, platform_width, platform_height, mid_y)

        # Set goal on the platform
        goals[obstacle_count+1] = [cur_x + platform_length // 2, mid_y]

        # Add gap before the next platform leading to variability in difficulty
        cur_x += platform_length + gap_width

        obstacle_count += 1

    # Provide extra challenge before the final goal
    final_platform_height = max(platform_height_min, platform_height_max)
    cur_x += gap_width
    add_platform(cur_x, platform_length, platform_width_max, final_platform_height, mid_y)
    goals[-1] = [cur_x + platform_length // 2, mid_y]

    # Fill the rest of the terrain to flat ground
    height_field[cur_x+platform_length:, :] = 0

    return height_field, goals

def set_terrain_30(length, width, field_resolution, difficulty):
    """Combination of platforms and ramps to traverse a pit for the robot to climb on and jump across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define dimensions and properties of platforms and ramps
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.2)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.2 * difficulty, 0.1 + 0.3 * difficulty
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
        ramp_height = np.random.uniform(platform_height_min, platform_height_max)
        slant = np.linspace(0, ramp_height, num=x2-x1)
        slant = slant[::direction]
        slant = slant[:, None]  # Add a dimension for broadcasting to y
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy = m_to_idx(0.4)  # Consistent y offset

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Set remaining area to be a pit
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    for i in range(4):  # Set up 4 platforms
        dx = np.random.randint(dx_min, dx_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y)

        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y]

        cur_x += platform_length + dx + gap_length

    for i in range(4, 7):  # Set up 3 ramps
        dx = np.random.randint(dx_min, dx_max)
        direction = (-1) ** i  # Alternate left and right ramps
        add_ramp(cur_x, cur_x + platform_length + dx, mid_y, direction)

        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y]

        cur_x += platform_length + dx + gap_length
    
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_31(length, width, field_resolution, difficulty):
    """Tilted platforms and narrow beams for the robot to balance and climb."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Parameters for obstacles
    platform_width = 0.6  # width in meters for narrow beams
    platform_height_base = 0.1  # base height for platforms
    platform_height_incr = 0.1 * difficulty  # height increment based on difficulty
    gap_length_base = 0.2  # base gap length in meters
    gap_length_incr = 0.1 * difficulty  # gap length increment based on difficulty
    
    def add_platform(start_x, end_x, y_center, tilt_direction=0):
        """
        Adds a tilted platform to the height_field.
        """
        width_idx = m_to_idx(platform_width)
        half_width = width_idx // 2
        x1, x2 = start_x, end_x
        y1, y2 = y_center - half_width, y_center + half_width
        height = platform_height_base + platform_height_incr * difficulty
        if tilt_direction != 0:
            # Create a linear gradient for the tilt
            slope = np.linspace(0, height, y2 - y1) * tilt_direction
            for i in range(x1, x2):
                height_field[i, y1:y2] = slope
        else:
            height_field[x1:x2, y1:y2] = height

    mid_y = m_to_idx(width) // 2
    spawn_length = m_to_idx(2)
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Set spawn area to flat ground
    height_field[0:spawn_length, :] = 0

    cur_x = spawn_length
    segments = 7  # Number of segments including both platforms and beams

    for i in range(segments):
        tilt_direction = (-1) ** i  # Alternate tilt direction
        segment_length = np.random.uniform(0.8, 1.2)  # length of each segment in meters
        segment_length_idx = m_to_idx(segment_length)
        add_platform(cur_x, cur_x + segment_length_idx, mid_y, tilt_direction)
        
        # Set goal in the middle of the segment
        goals[i+1] = [cur_x + segment_length_idx // 2, mid_y]
        
        # Add gap between segments
        gap_length = gap_length_base + gap_length_incr
        cur_x += segment_length_idx + m_to_idx(gap_length)
    
    # Add final goal at the end
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals


def set_terrain_32(length, width, field_resolution, difficulty):
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

def set_terrain_33(length, width, field_resolution, difficulty):
    """Combines jumping gaps, narrow platforms, and varied-height platforms for the quadruped to navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Parameters
    platform_width_min, platform_width_max = 0.4, 1.0  # Testing balance by making platforms narrower
    gap_width = 0.2 + 0.5 * difficulty  # Increase gap width with difficulty
    platform_height_min, platform_height_max = 0.05 + 0.20 * difficulty, 0.1 + 0.35 * difficulty

    platform_width_min, platform_width_max = m_to_idx([platform_width_min, platform_width_max])
    gap_width = m_to_idx(gap_width)
    mid_y = m_to_idx(width) // 2

    # Function to create a platform
    def add_platform(start_x, length, width, height, mid_y):
        half_width = width // 2
        height_field[start_x:start_x+length, mid_y-half_width:mid_y+half_width] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at the spawn point

    # Create terrain
    cur_x = spawn_length
    for i in range(7):
        # Determine platform parameters
        platform_length = m_to_idx(1.0)  # Fixed length for uniformity
        platform_width = np.random.randint(platform_width_min, platform_width_max)
        platform_height = np.random.uniform(platform_height_min, platform_height_max)

        # Create platform
        add_platform(cur_x, platform_length, platform_width, platform_height, mid_y)

        # Set goal on the platform
        goals[i+1] = [cur_x + platform_length // 2, mid_y]
        
        # Add gap before the next platform
        cur_x += platform_length + gap_width

    # Fill the rest of the terrain to flat ground
    height_field[cur_x:, :] = 0
    goals[-1] = [m_to_idx(length) - m_to_idx(0.5), mid_y]  # Make sure final goal is within bounds

    return height_field, goals

def set_terrain_34(length, width, field_resolution, difficulty):
    """Alternating platforms and narrow beams for climbing and jumping skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        if isinstance(m, (list, tuple)):
            return [round(i / field_resolution) for i in m]
        return np.round(m / field_resolution).astype(np.int16)

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width_min, platform_width_max = 0.4, 1.5  # Range of widths
    platform_height_min, platform_height_max = 0.1, 0.4  # Adjusted heights
    
    gap_length = 0.2 + 0.3 * difficulty  # Moderate gap length
    gap_length = m_to_idx(gap_length)
    
    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height, width):
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

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
    for i in range(6):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        platform_width = np.random.uniform(platform_width_min, platform_width_max)
        platform_width = m_to_idx(platform_width)

        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height, platform_width)
        goals[i+1] = [cur_x + (platform_length + dx) // 2, mid_y + dy]

        # Add gap
        cur_x += platform_length + dx + gap_length
    
    # Final descent ramp
    final_platform_length = m_to_idx(2)
    add_platform(cur_x, cur_x + final_platform_length, mid_y, 0, final_platform_length // 2)
    goals[-1] = [cur_x + final_platform_length // 2, mid_y]

    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_35(length, width, field_resolution, difficulty):
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

def set_terrain_36(length, width, field_resolution, difficulty):
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

def set_terrain_37(length, width, field_resolution, difficulty):
    """Combination of stairs, narrow beams, and sloped surfaces traversing a pit for the robot to climb on and jump across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Distance between key features
    gap_length = 0.4 + 0.4 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    # Function to add stairs
    def add_stairs(start_x, end_x, mid_y, steps, step_height):
        half_width = m_to_idx(0.6)  # making stairs wider
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        stair_spacing = (x2 - x1) // steps
        for i in range(steps):
            height_field[x1 + i * stair_spacing : x1 + (i + 1) * stair_spacing, y1:y2] = i * step_height

    # Function to add beams
    def add_beam(start_x, end_x, mid_y):
        half_width = m_to_idx(0.4)  # narrow beams
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        beam_height = np.random.uniform(0.15, 0.3)
        height_field[x1:x2, y1:y2] = beam_height

    # Function to add slopes
    def add_slope(start_x, end_x, mid_y, direction):
        half_width = m_to_idx(0.5)
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slope_height = np.random.uniform(0.1 + 0.1 * difficulty, 0.25 + 0.25 * difficulty)
        slant = np.linspace(0, slope_height, num=x2-x1)
        if direction == 'up':
            height_field[x1:x2, y1:y2] = slant[:, None]
        else:
            height_field[x1:x2, y1:y2] = slant[::-1][:, None]

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at the end of the spawn area

    # Set remaining area to be a pit
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    features = ['stair', 'beam', 'slope'] * 2  # Repeat feature types
    random.shuffle(features)

    for i in range(6):  # Set up 6 features
        dx = random.randint(-m_to_idx(0.1), m_to_idx(0.1))
        if features[i] == 'stair':
            add_stairs(cur_x, cur_x + m_to_idx(1.2) + dx, mid_y, 5, 0.1 + 0.1 * difficulty)
        elif features[i] == 'beam':
            add_beam(cur_x, cur_x + m_to_idx(1.0) + dx, mid_y)
        elif features[i] == 'slope':
            direction = 'up' if i % 2 == 0 else 'down'
            add_slope(cur_x, cur_x + m_to_idx(1.0) + dx, mid_y, direction)

        # Put goal in the center of each feature
        goals[i+1] = [cur_x + (m_to_idx(1.0) + dx) / 2, mid_y]

        # Add gap
        cur_x += m_to_idx(1.0) + dx + gap_length

    # Add final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_38(length, width, field_resolution, difficulty):
    """Combination of varying height platforms and angle ramps for the quadruped to climb up and jump across."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up dimensions for platforms and ramps
    platform_length = 0.8 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width_min, platform_width_max = 0.8, 1.2
    platform_width_min = m_to_idx(platform_width_min)
    platform_width_max = m_to_idx(platform_width_max)
    platform_height_min, platform_height_max = 0.1, 0.3
    platform_height_min = platform_height_min * difficulty
    platform_height_max = platform_height_max * difficulty
    gap_length = 0.4 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)
    
    ramp_length = 1.2 - 0.2 * difficulty
    ramp_length = m_to_idx(ramp_length)
    ramp_height_min, ramp_height_max = 0.1, 0.35
    ramp_height_min = ramp_height_min * difficulty
    ramp_height_max = ramp_height_max * difficulty
    
    cur_x = m_to_idx(2)   # Start position after the spawn
    mid_y = m_to_idx(width // 2)
    
    def add_platform(x, y_mid):
        """Adds a platform."""
        half_width = np.random.randint(platform_width_min//2, platform_width_max//2)
        height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x:x + platform_length, y_mid - half_width:y_mid + half_width] = height
        return x + platform_length, height
    
    def add_ramp(x, y_mid, height, slope):
        """Adds a ramp."""
        half_width = np.random.randint(platform_width_min//2, platform_width_max//2)
        rem_height = slope * (height_field.shape[0] - x)
        rem_height = min(rem_height, height * 0.5)
        new_height = height + rem_height
        heights = np.linspace(height, new_height, ramp_length)
        for i in range(ramp_length):
            height_field[x + i, y_mid - half_width:y_mid + half_width] = heights[i]
        return x + ramp_length, new_height
    
    # Make the first goal just in front to start
    goals[0] = [m_to_idx(2) - m_to_idx(0.5), mid_y]
    
    # Create a series of platforms and ramps
    for i in range(7):
        if i % 2 == 0:
            cur_x, cur_height = add_platform(cur_x, mid_y)
        else:
            cur_x, cur_height = add_ramp(cur_x, mid_y, cur_height, 0.5)
        if i < 7-1:  # Add goals only for the first 7
            goals[i + 1] = [cur_x - platform_length // 2, mid_y]
        cur_x += gap_length  # Leave a gap after each obstacle

    # Add final goal slightly beyond the last obstacle
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    return height_field, goals

def set_terrain_39(length, width, field_resolution, difficulty):
    """A blend of curved inclines and varied-width platforms to navigate carefully and balance across obstacles."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform and incline dimensions
    platform_length_base = 1.0 - 0.2 * difficulty
    platform_width_range = (1.0, 1.6)
    platform_height_min, platform_height_max = 0.1, 0.5 * difficulty
    incline_length = 1.0 - 0.2 * difficulty
    incline_length = m_to_idx(incline_length)
    gap_length_base = 0.1 + 0.4 * difficulty
    mid_y = m_to_idx(width) // 2

    def add_platform_segment(start_x, width_range, height_range):
        half_width = m_to_idx(np.random.uniform(*width_range)) // 2
        x1, x2 = start_x, start_x + m_to_idx(platform_length_base)
        y_center = mid_y + np.random.randint(-m_to_idx(0.5), m_to_idx(0.5))
        y1, y2 = y_center - half_width, y_center + half_width
        platform_height = np.random.uniform(*height_range)
        height_field[x1:x2, y1:y2] = platform_height
        return x2, y_center

    def add_incline(start_x, direction):
        half_width = m_to_idx(platform_width_range[0]) // 2
        x1, x2 = start_x, start_x + incline_length
        if direction > 0:
            slant = np.linspace(0, difficulty * 0.5, num=x2-x1)[:, None]
        else:
            slant = np.linspace(difficulty * 0.5, 0, num=x2-x1)[:, None]
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] += slant

    x_start = m_to_idx(2)
    goals[0] = [x_start - m_to_idx(0.5), mid_y]

    # Setting platforms with variations
    for i in range(4):
        x_start, y_center = add_platform_segment(x_start, platform_width_range, (platform_height_min, platform_height_max))
        goals[i+1] = [x_start - m_to_idx(platform_length_base / 2), y_center]
        x_start += m_to_idx(gap_length_base)
    
    # Adding an incline path
    add_incline(x_start, direction=1)
    goals[5] = [x_start + incline_length // 2, mid_y]

    x_start += incline_length + m_to_idx(gap_length_base)

    # Setting remaining varied-height platforms
    for i in range(2):
        x_start, y_center = add_platform_segment(x_start, platform_width_range, (platform_height_min, platform_height_max))
        goals[6+i] = [x_start - m_to_idx(platform_length_base / 2), y_center]
        x_start += m_to_idx(gap_length_base)

    # Final goal and reset terrain to flat toward the end.
    goals[7] = [x_start + m_to_idx(0.5), mid_y]
    height_field[x_start:, :] = 0

    return height_field, goals

# INSERT TERRAIN FUNCTION DEFINITIONS HERE
