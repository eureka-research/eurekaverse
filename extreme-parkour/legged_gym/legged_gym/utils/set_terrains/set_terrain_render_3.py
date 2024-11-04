
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
    """Combination of narrow walkways and inclined platforms to test balance and maneuvering ability."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions
    platform_length = 1.0 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.5, 1.0)
    platform_width = m_to_idx(platform_width)  # Narrower platforms to increase difficulty
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.2 + 0.3 * difficulty
    gap_length = 0.1 + 0.7 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_narrow_walkway(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        walkway_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = walkway_height

    def add_inclined_surface(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        incline_height = np.random.uniform(platform_height_min, platform_height_max)
        incline_slope = np.linspace(0, incline_height, x2 - x1)
        incline_slope = incline_slope[:, None]  # Add a dimension for broadcasting to y
        height_field[x1:x2, y1:y2] = incline_slope

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2  # Reducing dy to make it easier for narrow paths
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Set remaining area to be a pit
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    for i in range(3):  # Set up 3 narrow walkways
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_narrow_walkway(cur_x, cur_x + platform_length + dx, mid_y + dy)
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

    for i in range(3, 6):  # Set up 3 inclined surfaces
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_inclined_surface(cur_x, cur_x + platform_length + dx, mid_y + dy)
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length
    
    # Add final goal behind the last walkway, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_1(length, width, field_resolution, difficulty):
    """Varied terrain with narrow walkways, pits, and platforms of different heights to test the quadruped's agility and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up obstacle dimensions
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.4)  # Moderate platform width for balance
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.2 + 0.3 * difficulty

    narrow_walkway_width = np.random.uniform(0.4, 0.6)
    narrow_walkway_width = m_to_idx(narrow_walkway_width)
    gap_length = 0.3 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, platform_height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = platform_height

    def add_walkway(start_x, end_x, mid_y):
        half_width = narrow_walkway_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = np.random.uniform(0.0, 0.1)

    def add_ramp(start_x, end_x, mid_y, direction):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(platform_height_min, platform_height_max)
        slant = np.linspace(0, ramp_height, num=y2-y1)[::direction]
        slant = slant[None, :]  # Add a dimension for broadcasting to x
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.0, 0.4  # Polarity of dy will alternate instead of being random
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Add sequence of obstacles
    cur_x = spawn_length
    obstacle_sequence = ["platform", "narrow_walkway", "platform", "ramp", "narrow_walkway", "platform", "pit"]

    for i, obstacle in enumerate(obstacle_sequence):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        if obstacle == "platform":
            platform_height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height)
            goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
            cur_x += platform_length + dx + gap_length
        elif obstacle == "narrow_walkway":
            add_walkway(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
            cur_x += platform_length + dx + gap_length
        elif obstacle == "ramp":
            direction = (-1) ** i  # Alternate left and right ramps
            dy = dy * direction  # Alternate positive and negative y offsets
            add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, direction)
            goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
            cur_x += platform_length + dx + gap_length
        elif obstacle == "pit":
            height_field[cur_x:cur_x + gap_length, :] = -1.0
            goals[i+1] = [cur_x + gap_length / 2, mid_y]
            cur_x += gap_length

    # Add final goal behind the last obstacle, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_2(length, width, field_resolution, difficulty):
    """Combination of narrow pathways, elevated platforms, and varying height ramps for balance and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up obstacle dimensions with variable heights and narrower pathways
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.7, 1.0 - 0.3 * difficulty)  # Narrower pathways
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.15 + 0.25 * difficulty
    ramp_height_min, ramp_height_max = 0.0 + 0.2 * difficulty, 0.1 + 0.4 * difficulty
    gap_length = 0.1 + 0.6 * difficulty  # Increase gap length
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
        ramp_heights = np.linspace(0, height, x2 - x1) if direction == "up" else np.linspace(height, 0, x2 - x1)
        for i in range(x2 - x1):
            height_field[x1 + i, y1:y2] = ramp_heights[i]

    dx_min, dx_max = -0.05, 0.05
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    for i in range(3):  # Set up 3 platforms
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height)
        goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

        # Add a narrow pathway connecting platforms
        pathway_width = np.random.uniform(0.4, 0.5)
        pathway_width = m_to_idx(pathway_width)
        half_pathway = pathway_width // 2
        path_y1, path_y2 = mid_y - half_pathway, mid_y + half_pathway
        height_field[cur_x - m_to_idx(0.1) : cur_x + m_to_idx(0.1), path_y1:path_y2] = 0.0

    for i in range(3, 6):  # Set up 3 ramps alternating in direction
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        direction = "up" if i % 2 == 0 else "down"
        add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, direction, ramp_height)
        goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Add narrow pathways between ramps
        cur_x += platform_length + dx + gap_length
        pathway_width = np.random.uniform(0.4, 0.5)
        pathway_width = m_to_idx(pathway_width)
        half_pathway = pathway_width // 2
        path_y1, path_y2 = mid_y - half_pathway, mid_y + half_pathway
        height_field[cur_x - m_to_idx(0.1) : cur_x + m_to_idx(0.1), path_y1:path_y2] = 0.0

    # Final stretch platform
    dx = np.random.randint(dx_min, dx_max)
    dy = np.random.randint(dy_min, dy_max)
    platform_height = np.random.uniform(platform_height_min, platform_height_max)
    add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height)
    goals[7] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
    cur_x += platform_length + dx + gap_length

    # Final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_3(length, width, field_resolution, difficulty):
    """Narrow steps with varied heights and short gaps for precision, agility, and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    
    step_length = 0.5 * (1 - 0.3 * difficulty)
    step_length = m_to_idx(step_length)
    step_width = 0.6 + 0.2 * difficulty
    step_width = m_to_idx(step_width)
    step_height_min, step_height_max = 0.1 + 0.1 * difficulty, 0.3 + 0.2 * difficulty
    gap_length = 0.2 + 0.4 * difficulty
    gap_length = m_to_idx(gap_length)
    
    mid_y = m_to_idx(width) // 2

    def add_step(start_x, end_x, mid_y, height):
        half_width = step_width // 2
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[start_x:end_x, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Initial assignment
    cur_x = spawn_length
    for i in range(6):  # Set up 6 steps
        step_height = np.random.uniform(step_height_min, step_height_max)
        add_step(cur_x, cur_x + step_length, mid_y, step_height)

        # Put goal in the center of the step
        goals[i+1] = [cur_x + step_length / 2, mid_y]

        # Move to the next position with a gap in between
        cur_x += step_length + gap_length

    # Add final combination challenge (steps and ramps)
    final_step_length = 1.0 * (1 - 0.3 * difficulty)
    final_step_length = m_to_idx(final_step_length)
    final_height = np.random.uniform(step_height_min, step_height_max)
    add_step(cur_x, cur_x + final_step_length, mid_y - step_width, final_height)
    goals[6] = [cur_x + final_step_length / 2, mid_y - step_width / 2]

    final_ramp_length = 2.0 * (1 - 0.3 * difficulty)
    final_ramp_length = m_to_idx(final_ramp_length)
    ramp_height = np.random.uniform(step_height_min, step_height_max)
    height_field[cur_x + final_step_length:cur_x + final_step_length + final_ramp_length, mid_y - step_width:mid_y + step_width] = np.linspace(final_height, -1, final_ramp_length)[:, None]
    goals[7] = [cur_x + final_step_length + final_ramp_length / 2, mid_y]

    # Terrain outside the course area
    cur_x += final_step_length + final_ramp_length
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_4(length, width, field_resolution, difficulty):
    """Series of ascending steep ramps and slipping platforms for the quadruped to navigate and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform dimensions
    platform_length_min = 1.0 - 0.2 * difficulty
    platform_length_max = platform_length_min + 0.3
    ramp_height_min = 0.1 + 0.3 * difficulty
    ramp_height_max = ramp_height_min + 0.15
    slip_plate_height = 0.05 + 0.2 * difficulty

    platform_length = np.random.uniform(platform_length_min, platform_length_max)
    platform_length, slip_plate_length = m_to_idx(platform_length), m_to_idx(1.2)
    platform_width = np.random.uniform(1.2, 1.5)
    platform_width = m_to_idx(platform_width)

    mid_y = m_to_idx(width) // 2

    def add_ramp(start_x, end_x, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = np.linspace(0, height, x2-x1)[:, None]

    def add_slip_plate(start_x, end_x):
        half_width = platform_width // 2
        y1, y2 = mid_y - half_width, mid_y + half_width
        height = np.random.uniform(0.0, slip_plate_height)
        height_field[start_x:end_x, y1:y2] = height

    # Flatten the spawn area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # Initial goal

    cur_x = spawn_length
    for i in range(4):
        # Add ramp
        add_ramp(cur_x, cur_x + platform_length, ramp_height_min + i * 0.05)
        goals[i + 1] = [cur_x + m_to_idx(0.5), mid_y]  # Place a goal on the ramp
        cur_x += platform_length

        # Add slip plate
        add_slip_plate(cur_x, cur_x + slip_plate_length)
        cur_x += slip_plate_length
    
    # Final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_5(length, width, field_resolution, difficulty):
    """Combination of ascending and descending platforms, sideways-facing ramps, and narrow walkways to test agility, balance, and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and ramp dimensions
    platform_length = np.random.uniform(1.0, 1.2) - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.2)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.2 * difficulty, 0.05 + 0.35 * difficulty
    ramp_height_min, ramp_height_max = 0.0 + 0.3 * difficulty, 0.1 + 0.45 * difficulty
    gap_length = 0.2 + 0.4 * difficulty
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

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.0, 0.4  # Polarity of dy will alternate instead of being random
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Set remaining area to be a pit to force the robot to jump from platform to platform
    height_field[spawn_length:, :] = -1.0

    # Add first platform
    cur_x = spawn_length
    add_platform(cur_x, cur_x + platform_length, mid_y)
    goals[1] = [cur_x + platform_length / 2, mid_y]
    cur_x += platform_length + gap_length

    for i in range(1, 6):  # Alternate platforms and ramps
        dx = np.random.randint(dx_min, dx_max)
        direction = (-1) ** i  # Alternate left and right ramps
        dy = np.random.randint(dy_min, dy_max) * direction
      
        if (i % 2 == 0):
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
        else:
            add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, direction)

        # Put goal in the center of the current platform/ramp
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += platform_length + dx + gap_length
    
    # Add final goal behind the last ramp/platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_6(length, width, field_resolution, difficulty):
    """Combination of varied height platforms with gaps and lateral ramps to challenge agility and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions
    platform_base_length = 0.8 - 0.2 * difficulty
    platform_length = m_to_idx(platform_base_length)
    platform_base_width = 0.6 - 0.1 * difficulty
    platform_width = m_to_idx(np.random.uniform(platform_base_width, platform_base_width + 0.3))
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.2 + 0.3 * difficulty
    gap_base_length = 0.2 + 0.4 * difficulty
    gap_length = m_to_idx(gap_base_length)

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
        slant = np.linspace(0, direction * ramp_height, num=x2-x1)[:, None]
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.1, 0.3
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(6):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        if i % 2 == 0:
            # Add platform
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        else:
            # Add ramp
            add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        cur_x += platform_length + dx + gap_length

    # Final goal set at end of last obstacle
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_7(length, width, field_resolution, difficulty):
    """Combination of variable-height platforms with transitions through sideways-facing ramps, testing balance and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and ramp dimensions
    platform_length = 1.2 - 0.2 * difficulty  # Slightly longer platforms
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.2)  # Increased width for balance
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.2 * difficulty, 0.35 * difficulty
    ramp_height_min, ramp_height_max = 0.1 * difficulty, 0.3 * difficulty
    gap_length = 0.2 + 0.5 * difficulty  # Moderate gap length
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(x_start, x_end, y_mid):
        half_width = platform_width // 2
        y_start, y_end = y_mid - half_width, y_mid + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x_start:x_end, y_start:y_end] = platform_height

    def add_ramp(x_start, x_end, y_mid, direction):
        half_width = platform_width // 2
        y_start, y_end = y_mid - half_width, y_mid + half_width
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        slant = np.linspace(0, ramp_height, num=x_end-x_start)[::direction]
        slant = slant[:, None]  # Adding a dimension for broadcasting to y-axis
        height_field[x_start:x_end, y_start:y_end] = slant

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4  # Range for y deviations
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Set remaining area to be a base height
    cur_x = spawn_length
    for i in range(4):  # Set up 4 platforms
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
        height_field[cur_x:cur_x + platform_length + dx, :] = -0.2  # Base height in between platforms

        # Put goal in the center of the platform
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += platform_length + dx + gap_length
    
    # Add sideways-facing ramps between platforms
    for i in range(4, 7):  # Set up 3 ramps
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        direction = (-1) ** i  # Alternate left and right ramps
        dy = dy * direction  # Alternate y offsets

        add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, direction)
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        
        cur_x += platform_length + dx + gap_length

    # Add final goal behind the last ramp, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_8(length, width, field_resolution, difficulty):
    """Mixed platforms, ramps, and narrow pathways with varied heights and gaps for improved agility and navigation balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform and ramp dimensions and difficulty adjustment
    platform_length = 0.8 + 0.2 * difficulty  # Platform length varies with difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.4)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 * difficulty, 0.35 * difficulty
    ramp_height_min, ramp_height_max = 0.1 * difficulty, 0.4 * difficulty
    gap_length = 0.2 * difficulty + 0.4
    gap_length = m_to_idx(gap_length)

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
        slant = np.linspace(0, height, num=x2-x1)[::direction]
        slant = slant[:, None]  # Add a dimension for broadcasting to y
        height_field[x1:x2, y1:y2] = slant

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    # First obstacle: Elevated platform
    platform_height = np.random.uniform(platform_height_min, platform_height_max)
    add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)
    goals[1] = [cur_x + platform_length / 2, mid_y]
    cur_x += platform_length + gap_length

    for i in range(1, 6):  # Set up mixed obstacles
        if i % 2 == 0:  # Alternate between ramps and narrow paths
            height = np.random.uniform(ramp_height_min, ramp_height_max)
            direction = (-1) ** i  # Alternate side directions
            add_ramp(cur_x, cur_x + platform_length, mid_y, height, direction)
        else:
            elevated_height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, cur_x + platform_length, mid_y, elevated_height)

        goals[i+1] = [cur_x + platform_length / 2, mid_y]
        cur_x += platform_length + gap_length

    # Add final elevated platform for goal
    final_height = np.random.uniform(platform_height_min, platform_height_max)
    add_platform(cur_x, cur_x + platform_length, mid_y, final_height)
    goals[7] = [cur_x + platform_length / 2, mid_y]

    return height_field, goals

def set_terrain_9(length, width, field_resolution, difficulty):
    """Platforms and inclined ramps with staggered steps to enhance navigation difficulty and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Parameters for difficulty
    platform_length_base = 0.8 + 0.2 * difficulty
    platform_length = m_to_idx(platform_length_base)
    platform_width = m_to_idx(0.6 + 0.4 * difficulty)
    platform_height_min, platform_height_max = 0.05 + 0.15 * difficulty, 0.15 + 0.3 * difficulty
    ramp_length = m_to_idx(1.0)
    gap_length = m_to_idx(0.4 + 0.5 * difficulty)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, length, width, center_y, height_range):
        half_width = width // 2
        platform_height = np.random.uniform(*height_range)
        height_field[start_x:start_x + length, center_y - half_width:center_y + half_width] = platform_height

    def add_inclined_ramp(start_x, end_x, width, center_y, start_height, end_height):
        half_width = width // 2
        ramp_heights = np.linspace(start_height, end_height, end_x - start_x)[:, None]
        height_field[start_x:end_x, center_y - half_width:center_y + half_width] += ramp_heights

    # Set initial flat ground where the quadruped spawns
    spawn_length = m_to_idx(2.0)
    height_field[:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    # Add alternating platforms and inclined ramps
    for i in range(6):
        if i % 2 == 0:
            add_platform(cur_x, platform_length, platform_width, mid_y, (platform_height_min, platform_height_max))
            goals[i + 1] = [cur_x + platform_length // 2, mid_y]
            cur_x += platform_length + gap_length
        else:
            start_height = np.random.uniform(platform_height_min, platform_height_max)
            end_height = np.random.uniform(platform_height_min, platform_height_max)
            add_inclined_ramp(cur_x, cur_x + ramp_length, platform_width, mid_y, start_height, end_height)
            goals[i + 1] = [cur_x + ramp_length // 2, mid_y]
            cur_x += ramp_length + gap_length

    # Final approach till the end
    add_platform(cur_x, platform_length, platform_width, mid_y, (platform_height_min, platform_height_max))
    goals[7] = [cur_x + platform_length // 2, mid_y]
    height_field[cur_x + platform_length:, :] = 0

    return height_field, goals

# INSERT TERRAIN FUNCTION DEFINITIONS HERE
