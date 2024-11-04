
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

def set_terrain_1(length, width, field_resolution, difficulty):
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

def set_terrain_2(length, width, field_resolution, difficulty):
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

def set_terrain_3(length, width, field_resolution, difficulty):
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

def set_terrain_4(length, width, field_resolution, difficulty):
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

def set_terrain_5(length, width, field_resolution, difficulty):
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

def set_terrain_6(length, width, field_resolution, difficulty):
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

def set_terrain_7(length, width, field_resolution, difficulty):
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

def set_terrain_8(length, width, field_resolution, difficulty):
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

def set_terrain_9(length, width, field_resolution, difficulty):
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

# INSERT TERRAIN FUNCTION DEFINITIONS HERE
