
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

def set_terrain_1(length, width, field_resolution, difficulty):
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

def set_terrain_2(length, width, field_resolution, difficulty):
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

def set_terrain_3(length, width, field_resolution, difficulty):
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

def set_terrain_4(length, width, field_resolution, difficulty):
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

def set_terrain_5(length, width, field_resolution, difficulty):
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

def set_terrain_6(length, width, field_resolution, difficulty):
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

def set_terrain_7(length, width, field_resolution, difficulty):
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

def set_terrain_8(length, width, field_resolution, difficulty):
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

def set_terrain_9(length, width, field_resolution, difficulty):
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

def set_terrain_10(length, width, field_resolution, difficulty):
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

def set_terrain_11(length, width, field_resolution, difficulty):
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

def set_terrain_12(length, width, field_resolution, difficulty):
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

def set_terrain_13(length, width, field_resolution, difficulty):
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

def set_terrain_14(length, width, field_resolution, difficulty):
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

def set_terrain_15(length, width, field_resolution, difficulty):
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

def set_terrain_16(length, width, field_resolution, difficulty):
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


def set_terrain_17(length, width, field_resolution, difficulty):
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

def set_terrain_18(length, width, field_resolution, difficulty):
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

def set_terrain_19(length, width, field_resolution, difficulty):
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

def set_terrain_20(length, width, field_resolution, difficulty):
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

def set_terrain_21(length, width, field_resolution, difficulty):
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

def set_terrain_22(length, width, field_resolution, difficulty):
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

def set_terrain_23(length, width, field_resolution, difficulty):
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

def set_terrain_24(length, width, field_resolution, difficulty):
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

def set_terrain_25(length, width, field_resolution, difficulty):
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

def set_terrain_26(length, width, field_resolution, difficulty):
    """Multiple platforms, ramps, and gaps of increasing difficulty"""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set platform, ramp dimensions and gap lengths
    platform_length = 1.2 - 0.4 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 0.6  # Keep the platform width fixed
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.2 + 0.2 * difficulty, 0.3 + 0.4 * difficulty
    gap_length = 0.5 + 0.5 * difficulty  # Increase gap length with difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(x_start, x_end, mid_y, height):
        y_half_width = platform_width // 2
        y1, y2 = mid_y - y_half_width, mid_y + y_half_width
        height_field[x_start:x_end, y1:y2] = height

    def add_ramp(start_x, end_x, mid_y, height, direction):
        y_half_width = platform_width // 2
        y1, y2 = mid_y - y_half_width, mid_y + y_half_width
        ramp_height = np.linspace(0, height, num=end_x-start_x)
        ramp_height = ramp_height[None, :]  # add a new axis for broadcasting to y
        ramp_height = ramp_height[::direction]  # reverse the ramp if direction is -1
        height_field[start_x:end_x, y1:y2] = ramp_height.T

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    for i in range(6):
        height = np.random.uniform(platform_height_min, platform_height_max)

        if i % 2 == 0:
            # Add a platform
            add_platform(cur_x, cur_x + platform_length, mid_y, height)
            goals[i+1] = [cur_x + platform_length / 2, mid_y]
        else:
            # Add a ramp
            direction = (-1) ** i  # Alternate slope directions
            add_ramp(cur_x, cur_x + platform_length, mid_y, height, direction)
            goals[i+1] = [cur_x + platform_length / 2, mid_y]
        
        # Adding a gap between obstacles
        cur_x += platform_length + dx_min + np.random.randint(dx_max) + gap_length

    # Add final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_27(length, width, field_resolution, difficulty):
    """Multiple platforms and narrow beams traversing a pit for the robot to navigate across."""
   
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and beam dimensions
    platform_length = 0.8 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 0.7 + 0.3 * difficulty
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.3 * difficulty, 0.2 + 0.5 * difficulty
    
    beam_length = 0.6 + 0.2 * difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = 0.3 + 0.1 * difficulty
    beam_width = m_to_idx(beam_width)
    beam_height = 0.15 + 0.2 * difficulty

    gap_length = 0.2 + 0.4 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_beam(start_x, end_x, mid_y, height):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = -0.05, 0.1  # Smaller variance to keep a challenging but manageable terrain
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Set remaining area to be a pit to ensure navigation from platform to platform
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    for i in range(4):  # Set up 4 platforms with gaps
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + platform_length, mid_y + dy)

        # Put goal in the center of the platform
        goals[i+1] = [cur_x + (platform_length // 2), mid_y + dy]

        # Add gap
        cur_x += platform_length + dx + gap_length

    for i in range(2):  # Set up 2 beams with gaps
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_beam(cur_x, cur_x + beam_length, mid_y + dy, beam_height)

        # Put goal at the start of the beam
        goals[5 + i] = [cur_x + (beam_length // 2), mid_y + dy]

        # Add gap
        cur_x += beam_length + dx + gap_length
    
    # Add final goal at the end
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_28(length, width, field_resolution, difficulty):
    """Mixed course with platforms, narrow beams, and tilted beams for agility and stability."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Course parameters
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width_specs = [np.random.uniform(1.0, 1.1), np.random.uniform(0.4, 0.7)]
    platform_width_specs = [m_to_idx(pw) for pw in platform_width_specs]
    platform_height_min, platform_height_max = 0.1 * difficulty, 0.4 * difficulty
    gap_length = 0.2 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)
    ramp_length = m_to_idx(1.5 - 0.5 * difficulty)

    mid_y = m_to_idx(width / 2)

    def add_platform(start_x, end_x, mid_y, width_spec):
        half_width = width_spec // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_beam(start_x, end_x, mid_y, width_spec):
        half_width = width_spec // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = np.random.uniform(0.1 * difficulty, 0.4 * difficulty)

    def add_tilted_beam(start_x, end_x, mid_y, direction, width_spec):
        half_width = width_spec // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(0.2, 0.6) * difficulty
        slant = np.linspace(0, ramp_height, num=end_x - start_x)[::direction]  # Create gradient
        height_field[x1:x2, y1:y2] = slant[:, None]

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.0, 0.5
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(7):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        if i % 3 == 0:
            obstacle = add_platform
            width_spec = platform_width_specs[0]
        elif i % 3 == 1:
            obstacle = add_beam
            width_spec = platform_width_specs[1]
        else:
            obstacle = add_tilted_beam
            width_spec = platform_width_specs[1]
            direction = 1 if i % 2 == 0 else -1

        if obstacle == add_tilted_beam:
            obstacle(cur_x, cur_x + ramp_length + dx, mid_y + dy, direction, width_spec)
            goals[i+1] = [cur_x + ramp_length // 2 + dx // 2, mid_y + dy]
            cur_x += ramp_length + dx + gap_length
        else:
            obstacle(cur_x, cur_x + platform_length + dx, mid_y + dy, width_spec)
            goals[i+1] = [cur_x + platform_length // 2, mid_y + dy]
            cur_x += platform_length + dx + gap_length

    # Set the final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_29(length, width, field_resolution, difficulty):
    """Multiple platforms connected by ramps and small gaps for balancing and climbing."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and ramp dimensions
    platform_length = 1.0 - 0.15 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.4) 
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.1 * difficulty, 0.2 + 0.25 * difficulty
    ramp_height_min, ramp_height_max = 0.0 + 0.3 * difficulty, 0.2 + 0.35 * difficulty
    gap_length = 0.1 + 0.3 * difficulty  
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_ramp(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        slant = np.linspace(0, ramp_height, num=y2-y1)
        slant = slant[None, :]  # Add a dimension for broadcasting to x
        height_field[x1:x2, y1:y2] = slant

    def add_safe_zone(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = 0

    dx_min, dx_max = -0.1, 0.1 
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.0, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    dx = np.random.randint(dx_min, dx_max)
    dy = np.random.randint(dy_min, dy_max)
    
    add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
    goals[1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
    cur_x += platform_length + dx + gap_length

    for i in range(1, 6):  # Set up 5 ramps
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        if i % 2 == 1:
            add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy)
        else:
            add_safe_zone(cur_x, cur_x + platform_length + dx, mid_y + dy)

        goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

    # Add final goal to the flat area beyond last obstacle
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0.0

    return height_field, goals

def set_terrain_30(length, width, field_resolution, difficulty):
    """Varying-width platforms and balance beams with small gaps, testing balance and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    balance_beam_length = 1.0 - 0.4 * difficulty
    balance_beam_length = m_to_idx(balance_beam_length)
    platform_width_min, platform_width_max = 0.4, 0.8 + 0.6 * difficulty
    beam_width = 0.3
    beam_width = m_to_idx(beam_width)
    platform_height_min, platform_height_max = 0.0 + 0.2 * difficulty, 0.05 + 0.25 * difficulty
    gap_length = 0.1 + 0.4 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, mid_y):
        width = np.random.uniform(platform_width_min, platform_width_max)
        width = m_to_idx(width)
        half_width = width // 2
        x1 = start_x
        x2 = start_x + platform_length
        y1 = mid_y - half_width
        y2 = mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height
        
    def add_balance_beam(start_x, mid_y):
        half_width = beam_width // 2
        x1 = start_x
        x2 = start_x + balance_beam_length
        y1 = mid_y - half_width
        y2 = mid_y + half_width
        beam_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = beam_height

    dx_min, dx_max = m_to_idx(-0.05), m_to_idx(0.05)  # Slight horizontal variability
    dy_min, dy_max = m_to_idx(-0.2), m_to_idx(0.2)  # Slight vertical variability

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    for i in range(4):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        # Add platform or balance beam alternately
        if i % 2 == 0:
            add_platform(cur_x, mid_y + dy)
            goals[i + 1] = [cur_x + platform_length / 2, mid_y + dy]
            cur_x += platform_length + dx + gap_length
        else:
            add_balance_beam(cur_x, mid_y + dy)
            goals[i + 1] = [cur_x + balance_beam_length / 2, mid_y + dy]
            cur_x += balance_beam_length + dx + gap_length

    # Add extra challenges towards the end to increase difficulty
    for i in range(4, 6):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        # Add platform or balance beam alternately with increased width variability
        if i % 2 == 0:
            platform_width_min += difficulty
            platform_width_max += difficulty
            add_platform(cur_x, mid_y + dy)
            goals[i + 1] = [cur_x + platform_length / 2, mid_y + dy]
            cur_x += platform_length + dx + gap_length
        else:
            add_balance_beam(cur_x, mid_y + dy)
            goals[i + 1] = [cur_x + balance_beam_length / 2, mid_y + dy]
            cur_x += balance_beam_length + dx + gap_length

    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_31(length, width, field_resolution, difficulty):
    """Mixed obstacles including wide platforms, uneven stepping stones, and gentle slopes for agility and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform parameters
    platform_width = np.random.uniform(1.2, 1.8)
    platform_width = m_to_idx(platform_width)
    platform_length = 1.5 - 0.5 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_height_min, platform_height_max = 0.1 * difficulty, 0.3 * difficulty

    # Stepping stone parameters
    stepping_stone_size = 0.5
    stepping_stone_size = m_to_idx(stepping_stone_size)
    stepping_stone_height_min, stepping_stone_height_max = 0.05 * difficulty, 0.2 * difficulty

    # Slope parameters
    slope_width = platform_width
    slope_length = 1.5 - 0.5 * difficulty
    slope_length = m_to_idx(slope_length)
    slope_height_min, slope_height_max = 0.1 * difficulty, 0.25 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_stepping_stone(mid_x, mid_y, height):
        half_size = stepping_stone_size // 2
        x1, x2 = mid_x - half_size, mid_x + half_size
        y1, y2 = mid_y - half_size, mid_y + half_size
        height_field[x1:x2, y1:y2] = height

    def add_slope(start_x, end_x, mid_y, height):
        half_width = slope_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slope = np.linspace(0, height, num=x2-x1)[:, None]  # Creating gradual slope
        height_field[x1:x2, y1:y2] = slope

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # First goal at the end of the flat area
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    dx_min, dx_max = m_to_idx(-0.1), m_to_idx(0.1)
    dy_min, dy_max = m_to_idx(-0.4), m_to_idx(0.4)

    # Add first wide platform
    add_platform(cur_x, cur_x + platform_length, mid_y, np.random.uniform(platform_height_min, platform_height_max))
    goals[1] = [cur_x + platform_length // 2, mid_y]
    cur_x += platform_length + m_to_idx(0.5)

    # Add series of stepping stones
    for i in range(2, 6):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_stepping_stone(cur_x + dx, mid_y + dy, np.random.uniform(stepping_stone_height_min, stepping_stone_height_max))
        goals[i] = [cur_x + dx, mid_y + dy]
        cur_x += stepping_stone_size + m_to_idx(0.5)

    # Add final slope
    slope_height = np.random.uniform(slope_height_min, slope_height_max)
    add_slope(cur_x, cur_x + slope_length, mid_y, slope_height)
    goals[-2] = [cur_x + slope_length // 2, mid_y]
    cur_x += slope_length + m_to_idx(0.5)

    # Last goal at the end
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0  # Ensure no further obstacles

    return height_field, goals

def set_terrain_32(length, width, field_resolution, difficulty):
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

def set_terrain_33(length, width, field_resolution, difficulty):
    """Series of different height platforms for the robot to jump onto and adapt its approach."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions for varying heights and gaps
    platform_length = 0.8 - 0.2 * difficulty  # Decreased length to make it jumpier
    platform_length = m_to_idx(platform_length)
    platform_width = 0.4 + 0.4 * (1 - difficulty)  # Narrow platforms
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1, 0.8 * difficulty  # Varied heights
    gap_length = 0.3 + 0.5 * difficulty  # Larger gaps
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Start creating platforms and gaps after spawn area
    cur_x = spawn_length

    for i in range(7):  # 7 platforms
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)

        # Put goal at the center of the platform
        goals[i+1] = [cur_x + platform_length // 2, mid_y]

        # Add gap
        cur_x += platform_length + gap_length
    
    # Add final goal beyond the last platform
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_34(length, width, field_resolution, difficulty):
    """Mixed terrain including uneven steps, narrow planks, and tilted surfaces for the quadruped to navigate through."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Constants
    platform_length = 1.0 - 0.3 * difficulty  # Adjusted for difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 0.3 + 0.05 * difficulty
    platform_width = m_to_idx(platform_width)
    pit_depth = -1.0
    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_plank(start_x, end_x, mid_y, height, tilt):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slant = np.linspace(0, tilt, num=x2-x1)[:, None]  # tilt effect
        height_field[x1:x2, y1:y2] = height + slant

    def add_gap(cur_x):
        # Set gap area to pit depth
        height_field[cur_x:cur_x + gap_length, :] = pit_depth
        return cur_x + gap_length

    dx_min, dx_max = -0.1, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)
    tilt_range = 0.0, 0.05 + 0.1 * difficulty

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Set remaining area to be a pit and platforms
    cur_x = spawn_length
    for i in range(6):  # Set up 6 mixed platforms and bridges
        dx = np.random.randint(dx_min, dx_max)
        height_min, height_max = 0.1 * difficulty, 0.5 * difficulty
        platform_height = np.random.uniform(height_min, height_max)
        dy = np.random.randint(dy_min, dy_max)
        if i % 2 == 0:
            # Plank with slope
            tilt = np.random.uniform(*tilt_range)
            add_plank(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height, tilt)
        else:
            # Regular platform
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height)

        # Put goal in the center of the platform/plank
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Add gap
        gap_length = m_to_idx(0.1 + 0.5 * difficulty)
        cur_x = add_gap(cur_x + platform_length + dx)
    
    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_35(length, width, field_resolution, difficulty):
    """Complex course with staggered elevated platforms and sideways facing ramps to challenge balance, precision, and incline traversal."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions
    platform_length = 0.8 + 0.4 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.2 + 0.2 * difficulty)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.3 + 0.5 * difficulty
    gap_length = 0.2 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_ramp(start_x, end_x, mid_y, direction, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.linspace(0, height, x2 - x1)[::direction]
        ramp_height = ramp_height[:, None]  # Broadcasting for y-axis width
        height_field[x1:x2, y1:y2] = ramp_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Set remaining area to potential pits to enforce the robot to stay on platforms
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    for i in range(6):  # Set up platforms and ramps
        if i % 2 == 0:  # Platforms at even indices
            platform_height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)
            height = platform_height
        else:  # Ramps at odd indices
            ramp_height = np.random.uniform(platform_height_min, platform_height_max)
            direction = 1 if i % 4 == 1 else -1  # Just alternating the direction
            add_ramp(cur_x, cur_x + platform_length, mid_y, direction, ramp_height)
            height = ramp_height

        # Place goals in the middle of each platform or ramp
        goals[i+1] = [cur_x + platform_length / 2, mid_y]

        # Add gap
        cur_x += platform_length + gap_length

    # Add final goal behind the last platform/ramp, fill in remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_36(length, width, field_resolution, difficulty):
    """Series of interconnected platforms and tilted planes to test the quadruped's balance and navigation abilities."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and plane dimensions
    platform_length = 1.5 - 0.5 * difficulty
    platform_length = m_to_idx(platform_length)
    small_platform_length = 0.6 - 0.2 * difficulty
    small_platform_length = m_to_idx(small_platform_length)
    obstacle_width = np.random.uniform(1.0, 1.2)
    obstacle_width = m_to_idx(obstacle_width)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.3 + 0.4 * difficulty
    ramp_height_min, ramp_height_max = 0.1 + 0.3 * difficulty, 0.2 + 0.5 * difficulty
    gap_length = 0.3 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, center_y):
        half_width = obstacle_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = center_y - half_width, center_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_ramp(start_x, end_x, center_y, slope_direction):
        half_width = obstacle_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = center_y - half_width, center_y + half_width
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        slant = np.linspace(0, ramp_height, num=y2-y1)[::slope_direction]
        slant = slant[None, :]  # Add a dimension for broadcasting to x
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.2, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.1, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Set remaining area to be a pit
    height_field[spawn_length:, :] = -1.0

    # Add first large platform
    cur_x = spawn_length
    dx = np.random.randint(dx_min, dx_max)
    dy = np.random.randint(dy_min, dy_max)
    add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
    goals[1] = [cur_x + (platform_length + dx) / 2, mid_y]
    cur_x += platform_length + dx + gap_length

    # Add interconnected ramps and small platforms
    for i in range(2, 6):
        if i % 2 == 0:  # Add small platform
            add_platform(cur_x, cur_x + small_platform_length, mid_y)
            cur_x += small_platform_length
        else:  # Add ramp
            slope_direction = (-1) ** (i // 2)  # Alternate direction
            add_ramp(cur_x, cur_x + platform_length // 2, mid_y, slope_direction)
            cur_x += platform_length // 2
            add_ramp(cur_x, cur_x + platform_length // 2, mid_y, -slope_direction)
            cur_x += platform_length // 2
        
        goals[i] = [cur_x - platform_length // 4, mid_y]
        cur_x += gap_length
    
    # Add last ramp and fill in remaining area
    slope_direction = 1 if (len(goals) - 1) % 2 else -1  # Alternate direction
    add_ramp(cur_x, cur_x + platform_length, mid_y, slope_direction)
    goals[-1] = [cur_x + platform_length / 2, mid_y]
    height_field[cur_x + platform_length:, :] = 0

    return height_field, goals

def set_terrain_37(length, width, field_resolution, difficulty):
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

def set_terrain_38(length, width, field_resolution, difficulty):
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

def set_terrain_39(length, width, field_resolution, difficulty):
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

# INSERT TERRAIN FUNCTION DEFINITIONS HERE
