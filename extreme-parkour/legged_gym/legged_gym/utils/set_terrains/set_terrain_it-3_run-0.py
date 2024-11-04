
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
    """Raised platforms with varying heights and narrow passages to test robot's agility and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and passage dimensions
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.2 - 0.1 * difficulty)  # Slightly reduce width
    platform_width = m_to_idx(platform_width)
    
    gap_length_min = 0.2
    gap_length_max = 0.8
    gap_length_min = m_to_idx(gap_length_min)
    gap_length_max = m_to_idx(gap_length_max)
    
    platform_height_min = 0.2 * difficulty
    platform_height_max = 0.4 + 0.2 * difficulty
    
    mid_y = m_to_idx(width) // 2
    
    def add_platform(x_start, x_end, y_center, height):
        half_width = platform_width // 2
        y1, y2 = y_center - half_width, y_center + half_width
        height_field[x_start:x_end, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]
    
    cur_x = spawn_length
    for i in range(7):  # Set up 6 platforms
        height = np.random.uniform(platform_height_min, platform_height_max)
        gap_length = np.random.randint(gap_length_min, gap_length_max)
        
        add_platform(cur_x, cur_x + platform_length, mid_y, height)
        goals[i+1] = [cur_x + platform_length // 2, mid_y]
        
        cur_x += platform_length + gap_length
        
        if i % 2 == 0 and i != 6:
            # Add a narrow passageway after 2 platforms
            passage_width = m_to_idx(0.35 + 0.15 * (1 - difficulty))
            passage_start = m_to_idx(0.2 + 0.3 * difficulty)
            passage_height = np.random.uniform(0.1, 0.2) * (difficulty + 1)
            height_field[cur_x:cur_x + passage_start, (mid_y - passage_width // 2):(mid_y + passage_width // 2)] = passage_height
            
            goals[i+1][0] += passage_start // 2
            cur_x += passage_start
    
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0
    
    return height_field, goals

def set_terrain_1(length, width, field_resolution, difficulty):
    """Dynamic platforms, rotating beams, and inclined ramps to test the quadruped's adaptability and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform parameters
    platform_length = 0.8 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.2)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.2 * difficulty, 0.05 + 0.28 * difficulty

    # Rotating beam parameters
    beam_length = 1.5 - 0.4 * difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = 0.4  # Narrower to test balance
    beam_width = m_to_idx(beam_width)
    
    # Ramp parameters 
    ramp_height_min, ramp_height_max = 0.1 + 0.2 * difficulty, 0.1 + 0.3 * difficulty
    ramp_length = 1.2 - 0.4 * difficulty 
    ramp_length = m_to_idx(ramp_length)
    gap_length = 0.1 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_rotating_beam(start_x, length, mid_y):
        half_width = beam_width // 2
        x1, x2 = start_x, start_x + length
        y1, y2 = mid_y - half_width, mid_y + half_width
        beam_height = (platform_height_min + platform_height_max) / 2  # Fixed height for rotating beam
        height_field[x1:x2, y1:y2] = beam_height

    def add_ramp(start_x, length, mid_y, direction):
        half_width = platform_width // 2
        x1, x2 = start_x, start_x + length
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        slant = np.linspace(0, ramp_height, num=y2-y1)[::direction]
        slant = slant[None, :]  # Broadcasting to x
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.0, 0.3  # Polarity for alternating
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)
    
    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(4):  # Setting up the course with various obstacles
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        if i % 2 == 0: 
            # Add a moving platform
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        else:
            # Add a rotating beam
            add_rotating_beam(cur_x, beam_length, mid_y + dy)
            goals[i+1] = [cur_x + (beam_length) / 2, mid_y + dy]
        
        # Add gap
        cur_x += platform_length + dx + gap_length

    for i in range(4, 6):  # Adding inclined ramps for the last section
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        direction = (-1) ** i  # Alternating left and right ramps
        dy = dy * direction

        add_ramp(cur_x, ramp_length + dx, mid_y + dy, direction)
        goals[i+1] = [cur_x + (ramp_length + dx) / 2, mid_y + dy]
        cur_x += ramp_length + dx + gap_length
        
    # Add final goal behind the last obstacle, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_2(length, width, field_resolution, difficulty):
    """Combines varied-height platforms, angled ramps, and small jumps to test balance, climbing, and jumping abilities."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Setup parameters for the platform and gap dimensions
    platform_length_min = 0.8 - 0.2 * difficulty
    platform_length_max = 1.2 - 0.1 * difficulty
    platform_width = np.random.uniform(0.4, 0.6)  # Narrower platforms
    platform_height_min, platform_height_max = 0.1 + 0.3 * difficulty, 0.2 + 0.4 * difficulty
    gap_length_min = 0.3 + 0.3 * difficulty
    gap_length_max = 0.5 + 0.5 * difficulty

    platform_length_min, platform_length_max = m_to_idx([platform_length_min, platform_length_max])
    platform_width = m_to_idx(platform_width)
    gap_length_min, gap_length_max = m_to_idx([gap_length_min, gap_length_max])
    mid_y = m_to_idx(width) // 2
    
    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_ramp(start_x, end_x, mid_y, height, direction):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slant = np.linspace(0, height, num=x2 - x1)[::direction]
        for i in range(y1, y2):
            height_field[x1:x2, i] = slant

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at the spawn point

    cur_x = spawn_length

    for i in range(5):  # We are going to set up 5 platforms and 2 angled ramps
        platform_length = np.random.randint(platform_length_min, platform_length_max)
        platform_height = np.random.uniform(platform_height_min, platform_height_max)

        # Create Platform
        add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)
        goals[i+1] = [cur_x + platform_length // 2, mid_y]

        # Add gap before the next platform
        cur_x += platform_length + np.random.randint(gap_length_min, gap_length_max)

    # Add ramps to increase complexity
    for i in range(5, 7):
        ramp_length = np.random.randint(platform_length_min, platform_length_max)
        ramp_height = np.random.uniform(platform_height_min, platform_height_max)

        # Alternating ramps
        direction = -1 if i % 2 == 0 else 1
        add_ramp(cur_x, cur_x + ramp_length, mid_y, ramp_height, direction)
        goals[i+1] = [cur_x + ramp_length // 2, mid_y]

        cur_x += ramp_length + np.random.randint(gap_length_min, gap_length_max)

    # Final goal just behind the last ramp/platform
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0  # Ensure flat ground after the last obstacle

    return height_field, goals

def set_terrain_3(length, width, field_resolution, difficulty):
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

def set_terrain_4(length, width, field_resolution, difficulty):
    """Staggered platforms and ramps with varying heights for the quadruped to balance, climb, and jump across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and ramp dimensions
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.6, 1.0)  # Slightly narrow platform widths
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 * difficulty + 0.1, 0.35 * difficulty + 0.2
    ramp_height_min, ramp_height_max = 0.2 * difficulty + 0.1, 0.4 * difficulty + 0.2
    gap_length = 0.2 + 0.6 * difficulty  # Moderately challenging gap lengths
    gap_length = m_to_idx(gap_length)
    
    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_ramp(start_x, end_x, mid_y, direction, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slant = np.linspace(0, height, num=x2-x1)[::direction]
        height_field[x1:x2, y1:y2] = np.broadcast_to(slant[:, None], (x2-x1, y2-y1))
    
    mid_y = m_to_idx(width) // 2
    dx_min, dx_max = m_to_idx(-0.1), m_to_idx(0.1)
    dy_shift = m_to_idx(0.2)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    height_field[spawn_length:, :] = -1.0  # Pit area
    
    cur_x = spawn_length
    direction = 1

    for i in range(6):
        dx = np.random.randint(dx_min, dx_max)
        dy = dy_shift if i % 2 == 0 else -dy_shift
        height = np.random.uniform(platform_height_min, platform_height_max if i % 2 == 0 else ramp_height_max)

        if i % 2 == 0:  # Add platforms
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, height)
        else:  # Add ramps
            add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, direction, height)
            direction *= -1  # Alternate ramp direction

        goals[i+1] = [cur_x + (platform_length + dx) // 2, mid_y + dy]

        cur_x += platform_length + dx + gap_length

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_5(length, width, field_resolution, difficulty):
    """Platforms and ramps with variable heights for the robot to navigate, focusing on balance and careful navigation."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and ramp dimensions
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.5)  # Maintain variable widths for platforms
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.2 * difficulty, 0.5 * difficulty
    ramp_height_min, ramp_height_max = 0.2 * difficulty, 0.5 * difficulty
    gap_length = 0.1 + 0.5 * difficulty  # Moderate gap lengths
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

    dx_min, dx_max = m_to_idx(-0.1), m_to_idx(0.1)
    dy_min, dy_max = m_to_idx(0.0), m_to_idx(0.4)  # Polarity of dy will alternate instead of being random

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Set remaining area to be a pit to force platform and ramp traversal
    height_field[spawn_length:, :] = -1.0

    # Add first platform
    cur_x = spawn_length
    dx = np.random.randint(dx_min, dx_max)
    dy = np.random.randint(dy_min, dy_max)
    add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
    goals[1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
    cur_x += platform_length + dx + gap_length

    for i in range(1, 6):  # Set up 5 ramps
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        direction = (-1) ** i  # Alternate left and right ramps
        dy = dy * direction  # Alternate positive and negative y offsets
        add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, direction)

        # Put goal in the center of the ramp
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += platform_length + dx + gap_length
    
    # Add final goal behind the last ramp, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
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
    """Narrow paths and elevated platforms with small gaps for precise navigation and controlled jumps."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Path and platform dimensions
    path_length = 1.0 - 0.3 * difficulty
    platform_length = 1.0 - 0.2 * difficulty
    path_length, platform_length = m_to_idx(path_length), m_to_idx(platform_length)
    path_width = 0.4 + 0.2 * difficulty
    path_width, platform_width = m_to_idx(path_width), m_to_idx(1.6 - 0.6 * difficulty)
    max_height = 0.3 + 0.3 * difficulty
    gap_max = 0.2 + 0.4 * difficulty
    mid_y = m_to_idx(width) // 2

    def add_path(start_x, end_x, center_y, width, height):
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = center_y - half_width, center_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_platform(start_x, end_x, center_y, width, height):
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = center_y - half_width, center_y + half_width
        height_field[x1:x2, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # Initial goal at spawn point
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    last_height = 0

    for i in range(1, 7):
        if i % 2 == 0:
            gap = np.random.uniform(0.1, gap_max)
            gap = m_to_idx(gap)
            next_height = np.random.uniform(last_height, max_height)
            add_platform(cur_x + gap, cur_x + gap + platform_length, mid_y, platform_width, next_height)
            goals[i] = [cur_x + gap + platform_length // 2, mid_y]
            cur_x += gap + platform_length
        else:
            next_height = np.random.uniform(last_height, max_height)
            add_path(cur_x, cur_x + path_length, mid_y, path_width, next_height)
            goals[i] = [cur_x + path_length // 2, mid_y]
            cur_x += path_length

        last_height = next_height

    # Set final goal behind the last platform
    goals[7] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_8(length, width, field_resolution, difficulty):
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


def set_terrain_9(length, width, field_resolution, difficulty):
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

# INSERT TERRAIN FUNCTION DEFINITIONS HERE
