
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
    """Mixed obstacles with higher platforms, inclined ramps, and narrow paths."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up obstacle dimensions
    platform_length = np.random.uniform(0.8, 1.2) - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.2)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.2 + 0.4 * difficulty, 0.3 + 0.5 * difficulty
    ramp_height_min, ramp_height_max = 0.2 + 0.5 * difficulty, 0.3 + 0.6 * difficulty
    narrow_path_width = 0.5 
    narrow_path_width = m_to_idx(narrow_path_width)
    gap_length = 0.5 + 0.7 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height_min, height_max):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(height_min, height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_ramp(start_x, end_x, mid_y, height_min, height_max, direction):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(height_min, height_max)
        slant = np.linspace(0, ramp_height, num=y2-y1)[::direction]
        slant = slant[None, :]  # Add a dimension for broadcasting to x
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.1, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.5, 0.5
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Add first platform
    cur_x = spawn_length
    dx = np.random.randint(dx_min, dx_max)
    dy = np.random.randint(dy_min, dy_max)
    add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height_min, platform_height_max)
    goals[1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
    cur_x += platform_length + dx + gap_length

    for i in range(2, 7):
        if i % 2 == 0:  # Interleave platforms and ramps
            direction = (-1) ** i  # Alternate ramp directions
            dy = dy * direction  # Apply direction to dy
            add_ramp(cur_x, cur_x + platform_length, mid_y + dy, ramp_height_min, ramp_height_max, direction)
            goals[i] = [cur_x + platform_length / 2, mid_y + dy]
        else:
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height_min, platform_height_max)
            goals[i] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        cur_x += platform_length + dx + gap_length
    
    # Add final goal behind the last obstacle, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_1(length, width, field_resolution, difficulty):
    """Combined course with stairs and narrow platforms for the quadruped to navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up dimensions
    platform_length_min = 0.8 - 0.2 * difficulty
    platform_length_max = 1.1 - 0.2 * difficulty
    platform_width = np.random.uniform(0.6, 1.0)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1, 0.3 * difficulty
    step_height_min, step_height_max = 0.04, 0.12 * difficulty
    gap_length = 0.2 + 0.4 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(x, y, length, height):
        half_width = platform_width // 2
        x1, x2 = m_to_idx(x), m_to_idx(x + length)
        y1, y2 = m_to_idx(y) - half_width, m_to_idx(y) + half_width
        height_field[x1:x2, y1:y2] = height

    def add_steps(x, y, height, num_steps):
        step_length = platform_length_min / num_steps
        half_width = platform_width // 2
        for i in range(num_steps):
            x1 = m_to_idx(x + i * step_length)
            x2 = m_to_idx(x + (i + 1) * step_length)
            y1, y2 = m_to_idx(y) - half_width, m_to_idx(y) + half_width
            z = height * (i + 1) / num_steps
            height_field[x1:x2, y1:y2] = z

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Set remaining area to be a pit
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length

    # Add 2 stair segments
    for i in range(2):
        num_steps = 4
        height = np.random.uniform(step_height_min, step_height_max)
        add_steps(cur_x * field_resolution, mid_y * field_resolution, height, num_steps)

        # Put goal in the center of last step
        goals[i+1] = [cur_x + m_to_idx((num_steps / 2) * platform_length_min / num_steps), mid_y]

        cur_x += m_to_idx(platform_length_min) + gap_length

    # Add platforms and gaps
    for i in range(2, 7):
        length = np.random.uniform(platform_length_min, platform_length_max)
        height = np.random.uniform(platform_height_min, platform_height_max)
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        add_platform(cur_x * field_resolution, (mid_y + dy) * field_resolution, length, height)

        # Put goal in the center of the platform
        goals[i] = [cur_x + m_to_idx(length / 2) + dx, mid_y + dy]

        # Add gap
        cur_x += m_to_idx(length) + dx + gap_length

    # Add final goal behind the last segment, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_2(length, width, field_resolution, difficulty):
    """Combination of tilted platforms and narrow balance pathways to improve balance and fine motor skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16)

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and pathway dimensions
    platform_length = 1.0 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.5)
    platform_width = m_to_idx(platform_width)
    pathway_width = np.random.uniform(0.4, 0.6)
    pathway_width = m_to_idx(pathway_width)
    max_platform_height = 0.15 + 0.2 * difficulty
    gap_length = 0.3 + 0.2 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_pathway(start_x, end_x, mid_y, height, tilt=0):
        half_width = pathway_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slope = np.linspace(0, tilt, x2 - x1)
        for i in range(x2 - x1):
            height_field[x1 + i, y1:y2] = height + slope[i]

    dx_min, dx_max = -0.05, 0.05
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.0, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  
    
    current_x = spawn_length
    for i in range(4):  # A mix of platforms and tilted pathways
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        if i % 2 == 0:
            # Platform
            height = np.random.uniform(0, max_platform_height)
            add_platform(current_x, current_x + platform_length + dx, mid_y + dy, height)
            goals[i + 1] = [current_x + (platform_length + dx) / 2, mid_y + dy]
        else:
            # Tilted pathway
            height = np.random.uniform(0, max_platform_height / 2)
            tilt = np.random.uniform(0.05, 0.15) * (difficulty + 1)
            add_pathway(current_x, current_x + platform_length + dx, mid_y + dy, height, tilt)
            goals[i + 1] = [current_x + (platform_length + dx) / 2, mid_y + dy]

        current_x += platform_length + dx + gap_length

    # Add narrow balance pathways for the last segment
    for i in range(4, 7):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        height = np.random.uniform(0, max_platform_height / 3)
        add_pathway(current_x, current_x + platform_length + dx, mid_y + dy, height)
        goals[i + 1] = [current_x + (platform_length + dx) / 2, mid_y + dy]
        current_x += platform_length + dx + gap_length
    
    # Add final goal behind the last pathway, fill in the remaining gap
    goals[-1] = [current_x + m_to_idx(0.5), mid_y]
    height_field[current_x:, :] = 0

    return height_field, goals

def set_terrain_3(length, width, field_resolution, difficulty):
    """Combination of narrow bridges, stepping stones, and slanted platforms to test agility and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    
    bridge_length = 2.0 - 0.5 * difficulty
    bridge_length = m_to_idx(bridge_length)
    bridge_width = 0.3 + 0.2 * difficulty
    bridge_width = m_to_idx(bridge_width)
    stone_size = 0.4 + 0.1 * difficulty
    stone_size = m_to_idx(stone_size)
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.5, 1.0)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.05 + 0.1 * difficulty, 0.1 + 0.25 * difficulty
    slope_height_min, slope_height_max = 0.1 + 0.2 * difficulty, 0.3 + 0.4 * difficulty
    gap_length = 0.1 + 0.4 * difficulty
    gap_length = m_to_idx(gap_length)
    
    mid_y = m_to_idx(width) // 2
   
    def add_bridge(start_x, end_x, mid_y):
        half_width = bridge_width // 2
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[start_x:end_x, y1:y2] = 0.25 + 0.25 * difficulty

    def add_stepping_stone(center_x, center_y):
        half_size = stone_size // 2
        x1, x2 = center_x - half_size, center_x + half_size
        y1, y2 = center_y - half_size, center_y + half_size
        stone_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = stone_height

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_slant(start_x, end_x, mid_y, direction):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        incline_height = np.random.uniform(slope_height_min, slope_height_max)
        slant = np.linspace(0, incline_height, num=x2-x1)[::direction]
        slant = slant[:, None]  # Add a dimension for broadcasting
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # 1. Add a narrow bridge
    cur_x = spawn_length
    add_bridge(cur_x, cur_x + bridge_length, mid_y)
    goals[1] = [cur_x + bridge_length / 2, mid_y]
    cur_x += bridge_length + gap_length

    # 2. Add stepping stones
    for step in range(2):
        dx, dy = np.random.randint(dx_min, dx_max), np.random.randint(dy_min, dy_max)
        add_stepping_stone(cur_x + dx, mid_y + dy)
        goals[step + 2] = [cur_x + dx, mid_y + dy]
        cur_x += stone_size + gap_length

    # 3. Add a slant
    xy_slope_direction = [-1, 1]
    add_slant(cur_x, cur_x + platform_length, mid_y, np.random.choice(xy_slope_direction))
    goals[4] = [cur_x + platform_length / 2, mid_y]
    cur_x += platform_length + gap_length

    # 4. Add another stepping stone and finalize with narrow bridge
    add_stepping_stone(cur_x, mid_y)
    goals[5] = [cur_x + m_to_idx(0.2), mid_y]
    cur_x += stone_size + gap_length

    add_bridge(cur_x, cur_x + bridge_length, mid_y)
    goals[6] = [cur_x + bridge_length / 2, mid_y]
    cur_x += bridge_length + gap_length

    # 5. Add final goal behind the last ramp, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(1), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_4(length, width, field_resolution, difficulty):
    """Combination of ascending and descending platforms, sideways-facing ramps, and narrow walkways to challenge agility, balance, and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform, ramp, and walkway dimensions
    platform_length = 0.8 - 0.2 * difficulty  # Shorter platforms for higher difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.0)  # Keep platforms narrow
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.2 + 0.3 * difficulty
    ramp_length = 0.8 + 0.4 * difficulty  # Longer ramps for higher difficulty
    ramp_length = m_to_idx(ramp_length)
    ramp_height_min, ramp_height_max = 0.2 + 0.2 * difficulty, 0.3 + 0.5 * difficulty
    walkway_width = 0.4 + 0.2 * difficulty  # Narrow walkways
    walkway_width = m_to_idx(walkway_width)
    gap_length = 0.3 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        """Add a rectangular platform with a given height."""
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_ramp(start_x, end_x, mid_y, height_start, height_end):
        """Add an inclined ramp."""
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp = np.linspace(height_start, height_end, x2 - x1)[:, None]
        height_field[x1:x2, y1:y2] = ramp

    def add_walkway(start_x, end_x, mid_y, height):
        """Adds a narrow walkway."""
        half_width = walkway_width // 2
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
    for i in range(4):  # Set up 4 platforms, 3 ramps, and 2 walkways
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        # Add platform
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height)
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

        if i < 3:  # Add ramp after each platform except the last one
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)
            ramp_height_start = platform_height
            ramp_height_end = np.random.uniform(ramp_height_min, ramp_height_max)
            add_ramp(cur_x, cur_x + ramp_length + dx, mid_y + dy, ramp_height_start, ramp_height_end)
            goals[i+2] = [cur_x + (ramp_length + dx) / 2, mid_y + dy]
            cur_x += ramp_length + dx + gap_length

            if i % 2 == 0:  # Add walkway every other cycle
                dx = np.random.randint(dx_min, dx_max)
                dy = np.random.randint(dy_min, dy_max)
                walkway_height = ramp_height_end
                add_walkway(cur_x, cur_x + ramp_length + dx, mid_y + dy, walkway_height)
                goals[i+3] = [cur_x + (ramp_length + dx) / 2, mid_y + dy]
                cur_x += ramp_length + dx + gap_length

    # Add final goal behind the last obstacle, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_5(length, width, field_resolution, difficulty):
    """Combination of steep stepper platforms, inclined narrow pathways, and rolling ramps for testing balance and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions
    platform_length = 0.8 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 0.5 + 0.2 * difficulty
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.2, 0.4 + 0.4 * difficulty
    gap_length = 0.2 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_inclined_path(start_x, end_x, mid_y, height_start, height_end):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = np.linspace(height_start, height_end, x2 - x1)[:, None]

    def add_rolling_ramp(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = (np.sin(np.linspace(0, np.pi, x2 - x1)) * platform_height_max)
        height_field[x1:x2, y1:y2] = ramp_height[:, None]

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
    for i in range(2):
        # Add steep stepping platforms
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height)
        goals[1 + 2 * i] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

        # Add inclined narrow path
        height_start = np.random.uniform(platform_height_min, platform_height_max)
        height_end = np.random.uniform(platform_height_min, platform_height_max)
        add_inclined_path(cur_x, cur_x + platform_length + dx, mid_y + dy, height_start, height_end)
        goals[2 + 2 * i] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

    # Add final rolling ramp obstacle
    add_rolling_ramp(cur_x, cur_x + platform_length + m_to_idx(1), mid_y + np.random.randint(dy_min, dy_max))
    goals[-1] = [cur_x + m_to_idx(platform_length / 2 + 0.5), mid_y + np.random.randint(dy_min, dy_max)]

    return height_field, goals

def set_terrain_6(length, width, field_resolution, difficulty):
    """Combination of varied height ramps, narrow pathways, interleaved platforms with moderate gaps to challenge balance, precision, and edge discipline."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define some common dimensions and gaps, adjusted for difficulty
    platform_base_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_base_length)
    narrow_path_width = 0.4 + 0.1 * difficulty
    platform_width = m_to_idx(narrow_path_width)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.05 + 0.35 * difficulty
    gap_length = 0.15 + 0.4 * difficulty
    gap_length = m_to_idx(gap_length)
    
    mid_y = m_to_idx(width) // 2
    
    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_ramp(start_x, end_x, mid_y, direction=1):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(platform_height_min, platform_height_max)
        slant = np.linspace(0, direction * ramp_height, num=y2-y1)[None, :]
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.1, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    rotation = 1

    for i in range(7):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        if i % 2 == 0:
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        else:
            add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, direction=rotation)
            rotation *= -1
            goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        cur_x += platform_length + dx + gap_length

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0
    
    return height_field, goals

def set_terrain_7(length, width, field_resolution, difficulty):
    """Combination of offset platforms, inclined ramps, and narrow balance beams to challenge agility, balance, and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set dimensions for platforms, ramps, and beams with appropriate adjustments based on difficulty level
    platform_length_min = 0.8 - 0.2 * difficulty
    platform_length_max = 1.2 - 0.3 * difficulty
    platform_height_min, platform_height_max = 0.1 * difficulty, 0.3 * difficulty

    beam_length_min = 1.2 - 0.5 * difficulty
    beam_width = np.random.uniform(0.4, 0.6)
    beam_height = 0.15 * difficulty
    
    ramp_length = 1.0
    ramp_height_min, ramp_height_max = 0.2, 0.3 + 0.2 * difficulty
    
    gap_length_min = 0.2 + 0.1 * difficulty
    gap_length_max = 0.5 + 0.2 * difficulty
    
    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, mid_y, end_x=None):
        if end_x is None:
            end_x = start_x + np.random.randint(m_to_idx(platform_length_min), m_to_idx(platform_length_max))
        half_width = np.random.randint(m_to_idx(0.8), m_to_idx(1.2)) // 2
        height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[start_x:end_x, mid_y - half_width:mid_y + half_width] = height
        return end_x

    def add_beam(start_x, mid_y):
        end_x = start_x + m_to_idx(beam_length_min + (beam_length_min * difficulty))
        half_width = m_to_idx(beam_width) // 2
        height_field[start_x:end_x, mid_y - half_width:mid_y + half_width] = beam_height
        return end_x

    def add_ramp(start_x, mid_y, ascending=True):
        end_x = start_x + m_to_idx(ramp_length)
        half_width = np.random.randint(m_to_idx(0.8), m_to_idx(1.2)) // 2
        height_start = 0 if ascending else np.random.uniform(ramp_height_min, ramp_height_max)
        height_end = np.random.uniform(ramp_height_min, ramp_height_max) if ascending else 0
        slant = np.linspace(height_start, height_end, end_x - start_x)[:, None]
        height_field[start_x:end_x, mid_y - half_width:mid_y + half_width] = slant
        return end_x

    # Set initial flat terrain
    spawn_length = m_to_idx(2)
    height_field[:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length

    # First offset platform
    cur_x = add_platform(cur_x, mid_y + m_to_idx(np.random.uniform(-1.0, 1.0)))
    goals[1] = [cur_x - (cur_x - spawn_length) / 2, mid_y]

    # Second obstacle - Ascending Ramp
    cur_x += m_to_idx(np.random.uniform(gap_length_min, gap_length_max))
    cur_x = add_ramp(cur_x, mid_y, ascending=True)
    goals[2] = [cur_x - m_to_idx(ramp_length) / 2, mid_y]
    
    # Third obstacle - Offset narrow beam
    cur_x += m_to_idx(np.random.uniform(gap_length_min, gap_length_max))
    cur_x = add_beam(cur_x, mid_y + m_to_idx(np.random.uniform(-0.5, 0.5)))
    goals[3] = [cur_x - m_to_idx(beam_length_min) / 2, mid_y]

    # Fourth obstacle - Descending Ramp
    cur_x += m_to_idx(np.random.uniform(gap_length_min, gap_length_max))
    cur_x = add_ramp(cur_x, mid_y, ascending=False)
    goals[4] = [cur_x - m_to_idx(ramp_length) / 2, mid_y + m_to_idx(np.random.uniform(-1.0, 1.0))]

    # Fifth obstacle - Elevated Platform
    cur_x += m_to_idx(np.random.uniform(gap_length_min, gap_length_max))
    cur_x = add_platform(cur_x, mid_y + m_to_idx(np.random.uniform(-1.5, 1.5)))
    goals[5] = [cur_x - np.random.randint(m_to_idx(platform_length_min), m_to_idx(platform_length_max)) // 2, mid_y + m_to_idx(np.random.uniform(-1.5, 1.5))]

    # Sixth obstacle - Offset narrow beam
    cur_x += m_to_idx(np.random.uniform(gap_length_min, gap_length_max))
    cur_x = add_beam(cur_x, mid_y + m_to_idx(np.random.uniform(-0.5, 0.5)))
    goals[6] = [cur_x - (cur_x - spawn_length) // 2, mid_y + m_to_idx(np.random.uniform(-0.5, 0.5))]

    # Seventh obstacle - Ascending Ramp and final goal
    cur_x += m_to_idx(np.random.uniform(gap_length_min, gap_length_max))
    cur_x = add_ramp(cur_x, mid_y, ascending=True)
    goals[7] = [cur_x - m_to_idx(ramp_length) / 2, mid_y]

    return height_field, goals

def set_terrain_8(length, width, field_resolution, difficulty):
    """Complex terrain featuring narrower pathways, varying heights, and more turning points."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set parameters to control obstacle dimensions based on difficulty
    narrow_path_length = 0.7 + 0.2 * difficulty 
    narrow_path_length = m_to_idx(narrow_path_length)
    narrow_path_width = np.random.uniform(0.4, 0.8)  # Narrower paths
    narrow_path_width = m_to_idx(narrow_path_width)
    platform_height_min, platform_height_max = 0.3 * difficulty, 0.5 * difficulty
    gap_length = 0.3 + 0.4 * difficulty
    gap_length = m_to_idx(gap_length)
    
    def add_platform(start_x, end_x, mid_y, width):
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    mid_y = m_to_idx(width) // 2

    # Set spawn area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]
    
    cur_x = spawn_length

    # Challenge 1: Narrow, straight path
    add_platform(cur_x, cur_x + narrow_path_length, mid_y, narrow_path_width)
    goals[1] = [cur_x + narrow_path_length / 2, mid_y]
    cur_x += narrow_path_length + gap_length

    # Challenge 2: Elevated platform requiring precise descent
    elevated_platform_length = 1.0 - 0.1 * difficulty
    elevated_platform_length = m_to_idx(elevated_platform_length)
    elevated_platform_width = np.random.uniform(0.8, 1.2)
    elevated_platform_width = m_to_idx(elevated_platform_width)
    
    add_platform(cur_x, cur_x + elevated_platform_length, mid_y, elevated_platform_width)
    goals[2] = [cur_x + elevated_platform_length / 2, mid_y]
    cur_x += elevated_platform_length + gap_length

    # Challenge 3: Narrow, curved path (forcing a turn)
    narrow_path_turn_angle = 45 * difficulty  # Degrees
    narrow_path_turn_angle_rad = np.deg2rad(narrow_path_turn_angle)
    
    turn_path_length = int(narrow_path_length * np.cos(narrow_path_turn_angle_rad))
    turn_path_width = int(narrow_path_length * np.sin(narrow_path_turn_angle_rad))
    
    add_platform(cur_x, cur_x + turn_path_length, mid_y + turn_path_width, narrow_path_width)
    
    goals[3] = [cur_x + turn_path_length / 2, mid_y + turn_path_width]
    cur_x += turn_path_length + gap_length

    # Challenge 4: Elevated narrow path
    elevated_path_height = np.random.uniform(0.4 * difficulty, 0.6 * difficulty)
    
    elevated_narrow_path_length = 0.8 + 0.1 * difficulty
    elevated_narrow_path_length = m_to_idx(elevated_narrow_path_length)
    height_field[cur_x:cur_x + elevated_narrow_path_length, mid_y - narrow_path_width//2:mid_y + narrow_path_width//2] = elevated_path_height
    
    goals[4] = [cur_x + elevated_narrow_path_length / 2, mid_y]
    cur_x += elevated_narrow_path_length + gap_length

    # Challenge 5: Alternating platforms
    platform_lengths = [m_to_idx(0.7 + 0.2 * difficulty), m_to_idx(1.0 - 0.2 * difficulty)]
    
    for i in range(2):
        add_platform(cur_x, cur_x + platform_lengths[i], mid_y + ((-1)**i * m_to_idx(0.4)), narrow_path_width)
        goals[5+i] = [cur_x + platform_lengths[i] / 2, mid_y + ((-1)**i * m_to_idx(0.4))]
        cur_x += platform_lengths[i] + gap_length
        
    # Final goal on the ground
    final_goal_distance = m_to_idx(0.8)
    goals[-1] = [cur_x + final_goal_distance / 2, mid_y]
    
    height_field[cur_x:, :] = 0
    
    return height_field, goals

def set_terrain_9(length, width, field_resolution, difficulty):
    """Complex terrain with stepping stones, varying slopes, and narrow beams."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Parameters based on difficulty
    platform_length = m_to_idx(0.6 + 0.4 * difficulty)
    platform_width = m_to_idx(np.random.uniform(1.0, 1.2))
    platform_height_min, platform_height_max = 0.1 * difficulty, 0.2 + 0.3 * difficulty
    slope_length = m_to_idx(1.0)
    narrow_beam_length = m_to_idx(1.0)
    narrow_beam_width = m_to_idx(0.4 - 0.1 * difficulty)
    gap_length = m_to_idx(0.3 + 0.5 * difficulty)
    pit_depth = -1.0

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[start_x:end_x, mid_y-half_width:mid_y+half_width] = platform_height

    def add_slope(start_x, end_x, mid_y, height_start, height_end):
        slope = np.linspace(height_start, height_end, end_x - start_x)[:, None]
        slice_width = platform_width // 2
        height_field[start_x:end_x, mid_y-slice_width:mid_y+slice_width] = slope

    def add_narrow_beam(start_x, end_x, mid_y):
        half_width = narrow_beam_width // 2
        beam_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[start_x:end_x, mid_y-half_width:mid_y+half_width] = beam_height

    # Set up initial flat area for spawning
    spawn_length = m_to_idx(2.0)
    height_field[:spawn_length, :] = 0
    goals[0] = [spawn_length / 2, mid_y]  # First goal at spawn area

    cur_x = spawn_length

    # Stepping stones
    for i in range(2):
        add_platform(cur_x, cur_x + platform_length, mid_y)
        goals[i+1] = [cur_x + platform_length / 2, mid_y]
        cur_x += platform_length + gap_length

    # Add slopes
    for i in range(2):
        height_start = np.random.uniform(platform_height_min, platform_height_max)
        height_end = np.random.uniform(platform_height_min, platform_height_max)
        add_slope(cur_x, cur_x + slope_length, mid_y, height_start, height_end)
        goals[i+3] = [cur_x + slope_length / 2, mid_y]
        cur_x += slope_length + gap_length

    # Narrow beams
    for i in range(2):
        add_narrow_beam(cur_x, cur_x + narrow_beam_length, mid_y)
        goals[i+5] = [cur_x + narrow_beam_length / 2, mid_y]
        cur_x += narrow_beam_length + gap_length

    # Final platform for the last goal
    add_platform(cur_x, cur_x + platform_length, mid_y)
    goals[7] = [cur_x + platform_length / 2, mid_y]

    return height_field, goals

# INSERT TERRAIN FUNCTION DEFINITIONS HERE
