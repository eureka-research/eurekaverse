
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
    """Complex terrain with mixed platforms, ramps, and narrow beams to challenge the quadruped's balance, jumping, and climbing abilities."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up dimensions for platforms, ramps, and beams
    platform_length = 1.0
    platform_length = m_to_idx(platform_length)
    platform_width = m_to_idx(np.random.uniform(0.8, 1.2))
    platform_height_min, platform_height_max = 0.2, 0.4
    
    ramp_length = platform_length // 2
    ramp_height_min, ramp_height_max = 0.3, 0.6

    beam_length = platform_length
    beam_width = m_to_idx(0.3)
    beam_height = 0.2

    gap_min, gap_max = m_to_idx(0.3), m_to_idx(0.7)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_ramp(start_x, end_x, mid_y, ramp_height):
        half_width = platform_width // 2
        r_height_per_step = ramp_height / (end_x - start_x)
        ramp_heights = np.linspace(0, ramp_height, end_x - start_x)
        for i, x in enumerate(range(start_x, end_x)):
            height_field[x, mid_y - half_width:mid_y + half_width] = ramp_heights[i]

    def add_beam(start_x, end_x, mid_y):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = beam_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0.0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    for i in range(3):  # Adding three sets of platform and ramps
        gap_length = np.random.randint(gap_min, gap_max)

        # Add Platform
        add_platform(cur_x, cur_x + platform_length, mid_y)
        goals[i * 2 + 1] = [cur_x + platform_length // 2, mid_y]
        cur_x += platform_length + gap_length

        # Add Ramp
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max + difficulty * 0.2)
        add_ramp(cur_x, cur_x + ramp_length, mid_y, ramp_height)
        goals[i * 2 + 2] = [cur_x + ramp_length // 2, mid_y]
        cur_x += ramp_length + gap_length

    # Add final beams
    for i in range(2):
        gap_length = np.random.randint(gap_min, gap_max)
        add_beam(cur_x, cur_x + beam_length, mid_y)
        goals[6 + i] = [cur_x + beam_length // 2, mid_y]
        cur_x += beam_length + gap_length

    # Add final goal behind the last obstacle
    goals[7] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_1(length, width, field_resolution, difficulty):
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

def set_terrain_2(length, width, field_resolution, difficulty):
    """Multiple elevated platforms and narrow bridges with variable heights and gaps to challenge the quadruped's agility, stability, and jumping abilities."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length_base = 1.0
    platform_length_variation = 0.2 * difficulty
    platform_length = m_to_idx(platform_length_base + platform_length_variation)

    platform_width_base = 1.0
    platform_width_variation = 0.2 * difficulty
    platform_width = m_to_idx(np.random.uniform(platform_width_base - platform_width_variation, platform_width_base + platform_width_variation))
    
    platform_height_min = 0.1 * difficulty
    platform_height_max = 0.4 * difficulty
    gap_length_base = 0.2
    gap_length_variation = 0.3 * difficulty
    gap_length = m_to_idx(gap_length_base + gap_length_variation)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_narrow_bridge(start_x, end_x, mid_y):
        narrow_width = m_to_idx(0.4 + 0.4 * difficulty)
        half_width = narrow_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        bridge_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = bridge_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_variation = m_to_idx(0.3)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Set remaining area to be a pit
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    for i in range(6):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(-dy_variation, dy_variation)

        # Alternate between platforms and narrow bridges
        if i % 2 == 0:
            platform_height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height)
            goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        else:
            add_narrow_bridge(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        cur_x += platform_length + dx + gap_length

    # Add final goal behind the last obstacle, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_3(length, width, field_resolution, difficulty):
    """Narrow beams, wide platforms, and varying height ramps for the robot to balance, climb, and jump."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Parameters for platforms and beams
    platform_length = 1.0 - 0.1 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.2, 2.0)  # Wider platforms
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.1 + 0.4 * difficulty
    gap_length = 0.2 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    beam_length = 1.0 - 0.2 * difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = 0.4 - 0.1 * difficulty  # Narrow beams
    beam_width = m_to_idx(beam_width)
    beam_height_min, beam_height_max = 0.1 + 0.2 * difficulty, 0.2 + 0.4 * difficulty

    mid_y = m_to_idx(width) // 2

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
        beam_height = np.random.uniform(beam_height_min, beam_height_max)
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
    for i in range(4):  # Create 4 platforms
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)

        # Put goal in the center of the platform
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += platform_length + dx + gap_length

    for i in range(4, 7):  # Create 3 beams
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_beam(cur_x, cur_x + beam_length + dx, mid_y + dy)

        # Put goal in the center of the beam
        goals[i+1] = [cur_x + (beam_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += beam_length + dx + gap_length

    # Add final goal behind the last beam, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_4(length, width, field_resolution, difficulty):
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

def set_terrain_5(length, width, field_resolution, difficulty):
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

def set_terrain_6(length, width, field_resolution, difficulty):
    """Multiple sideways-facing ramps, tall platforms, and varying pits for the robot to climb and jump across."""    

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Parameters for platforms and ramps
    platform_length = 1.2 - 0.5 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.2, 1.8)  # Increase platform width
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.3 * difficulty, 0.3 + 0.4 * difficulty
    ramp_height_min, ramp_height_max = 0.2 + 0.4 * difficulty, 0.4 + 0.5 * difficulty
    gap_length = 0.2 + 0.7 * difficulty  # Increase gap length
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

    dx_min, dx_max = -0.1, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.0, 0.5  # Increase dy range for more complexity
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at spawn

    # Set remaining area to be a pit
    height_field[spawn_length:, :] = -1.0

    # Add first platform
    cur_x = spawn_length
    dx = np.random.randint(dx_min, dx_max)
    dy = np.random.randint(dy_min, dy_max)
    add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
    goals[1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
    cur_x += platform_length + dx + gap_length

    for i in range(1, 6):  # Set up platforms and ramps
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        direction = (-1) ** i  # Alternate left/right for ramps
        dy = dy * direction

        # Insert ramps and platforms alternatively
        if i % 2: 
            add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, direction)
        else:
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
        
        # Put goal at each alternating obstacle
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length
    
    # Put the last goal behind the last obstacle
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_7(length, width, field_resolution, difficulty):
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

def set_terrain_8(length, width, field_resolution, difficulty):
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

def set_terrain_9(length, width, field_resolution, difficulty):
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

# INSERT TERRAIN FUNCTION DEFINITIONS HERE
