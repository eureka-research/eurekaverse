
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
    """
    Combination of narrow beams, high platforms, and tilting surfaces to challenge the quadruped's agility, balance, and precision.
    """

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    # Initialize the height field
    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define parameters for obstacles
    platform_length = 1.0 - 0.2 * difficulty  # Smaller platforms at higher difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.7, 1.0)  # Narrower platforms
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.2 + 0.3 * difficulty, 0.35 + 0.45 * difficulty
    gap_length = 0.3 + 0.7 * difficulty  # Larger gaps as difficulty increases
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    # Place the initial flat area for spawning
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at spawn

    cur_x = spawn_length
    current_goal_index = 1

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_narrow_beam(start_x, end_x, mid_y):
        half_width = m_to_idx(0.2)  # Narrow beam width of 0.4 meters
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        beam_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = beam_height

    def add_tilting_surface(start_x, end_x, mid_y, tilt_direction):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        tilt_height = np.random.uniform(platform_height_min, platform_height_max)
        if tilt_direction == 'left':
            slant = np.linspace(0, tilt_height, num=x2-x1)
        else:
            slant = np.linspace(tilt_height, 0, num=x2-x1)
        height_field[x1:x2, y1:y2] = slant[:, None]  # Add a new axis for broadcasting

    for i in range(3):  # Set up platforms
        add_platform(cur_x, cur_x + platform_length, mid_y)
        goals[current_goal_index] = [cur_x + platform_length / 2, mid_y]
        cur_x += platform_length + gap_length
        current_goal_index += 1

    for i in range(2):  # Set up narrow beams
        add_narrow_beam(cur_x, cur_x + platform_length, mid_y)
        goals[current_goal_index] = [cur_x + platform_length / 2, mid_y]
        cur_x += platform_length + gap_length
        current_goal_index += 1

    for i in range(2):  # Set up tilting surfaces
        tilt_direction = 'left' if i % 2 == 0 else 'right'
        add_tilting_surface(cur_x, cur_x + platform_length, mid_y, tilt_direction)
        goals[current_goal_index] = [cur_x + platform_length / 2, mid_y]
        cur_x += platform_length + gap_length
        current_goal_index += 1

    # Final goal and fill remaining area with flat ground
    goals[7] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_1(length, width, field_resolution, difficulty):
    """Combination of varied height platforms, ramps, and gaps for the robot to navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up dimensions for platforms and ramps
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.2)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.15 + 0.2 * difficulty, 0.35 + 0.25 * difficulty
    gap_length = 0.15 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)
    ramp_length = 1.0 - 0.2 * difficulty
    ramp_length = m_to_idx(ramp_length)
    
    slope_min, slope_max = 0.1 + 0.2 * difficulty, 0.3 + 0.3 * difficulty
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
        ramp_height = np.random.uniform(slope_min, slope_max)
        slant = np.linspace(0, ramp_height, num=y2-y1)[::direction]
        slant = slant[None, :]  # Add a dimension for broadcasting to x
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.1, 0.3
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    for i in range(0, 3):  # Install 3 platforms with gaps
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

    for i in range(3, 6):  # Install 3 ramps with varying slopes
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        direction = (-1) ** (i % 2)  # Alternate left and right ramps
        dy = dy * direction  # Alternate positive and negative y offsets

        add_ramp(cur_x, cur_x + ramp_length + dx, mid_y + dy, direction)
        goals[i+1] = [cur_x + (ramp_length + dx) / 2, mid_y + dy]
        cur_x += ramp_length + dx + gap_length
    
    for i in range(6, 7):  # Install last platform with a gap
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length
    
    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_2(length, width, field_resolution, difficulty):
    """Diverse terrain with variable-height platforms, narrow bridges, and gentle ramps to challenge the quadruped's agility, precision, and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length_min = m_to_idx(0.8 - 0.2 * difficulty)
    platform_length_max = m_to_idx(1.2 - 0.2 * difficulty)
    gap_length_min = m_to_idx(0.3 + 0.2 * difficulty)
    gap_length_max = m_to_idx(0.6 + 0.3 * difficulty)
    platform_height_min, platform_height_max = 0.1 * difficulty, 0.4 * difficulty

    narrow_bridge_width = m_to_idx(0.4)
    ramp_length = m_to_idx(1.0)
    
    mid_y = m_to_idx(width) // 2
    spawn_length = m_to_idx(2)

    def add_platform(start_x, end_x, mid_y, height):
        half_width = m_to_idx(0.8) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_narrow_bridge(start_x, end_x, mid_y):
        half_width = narrow_bridge_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = 0  # Bridges will be flat but narrow

    def add_ramp(start_x, end_x, mid_y, base_height, peak_height, direction):
        half_width = m_to_idx(0.8) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_heights = np.linspace(base_height, peak_height, x2 - x1)
        if direction == "down":
            ramp_heights = ramp_heights[::-1]
        for i in range(x2 - x1):
            height_field[x1 + i, y1:y2] = ramp_heights[i]

    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    cur_y = mid_y

    obstacle_order = ['platform', 'bridge', 'ramp_up', 'ramp_down', 'platform', 'ramp_up', 'bridge']
    
    for i, obstacle in enumerate(obstacle_order):
        if obstacle == 'platform':
            platform_length = np.random.randint(platform_length_min, platform_length_max)
            platform_height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, cur_x + platform_length, cur_y, platform_height)
            goals[i + 1] = [cur_x + platform_length // 2, cur_y]
            cur_x += platform_length
        elif obstacle == 'bridge':
            bridge_length = np.random.randint(platform_length_min, platform_length_max)
            add_narrow_bridge(cur_x, cur_x + bridge_length, cur_y)
            goals[i + 1] = [cur_x + bridge_length // 2, cur_y]
            cur_x += bridge_length
        elif obstacle == 'ramp_up':
            ramp_height = np.random.uniform(platform_height_min, platform_height_max)
            add_ramp(cur_x, cur_x + ramp_length, cur_y, 0, ramp_height, "up")
            goals[i + 1] = [cur_x + ramp_length // 2, cur_y]
            cur_x += ramp_length
        elif obstacle == 'ramp_down':
            ramp_height = np.random.uniform(platform_height_min, platform_height_max)
            add_ramp(cur_x, cur_x + ramp_length, cur_y, ramp_height, 0, "down")
            goals[i + 1] = [cur_x + ramp_length // 2, cur_y]
            cur_x += ramp_length
        
        gap_length = np.random.randint(gap_length_min, gap_length_max)
        height_field[cur_x: cur_x + gap_length, :] = -1.0
        cur_x += gap_length

    goals[-1] = [cur_x + m_to_idx(0.5), cur_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_3(length, width, field_resolution, difficulty):
    """Narrow beams, sloped platforms, and varied height steps to challenge agility and precision."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    def add_ramp(start_x, end_x, mid_y, slope_up):
        half_width = platform_width // 2
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(platform_height_min, platform_height_max)
        ramp_slope = np.linspace(0, ramp_height, end_x - start_x) if slope_up else np.linspace(ramp_height, 0, end_x - start_x)
        height_field[start_x:end_x, y1:y2] = ramp_slope[:, None]

    def add_beam(start_x, end_x, mid_y, width):
        half_width = m_to_idx(width) // 2
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[start_x:end_x, y1:y2] = np.random.uniform(platform_height_min, platform_height_max)

    def add_irregular_step(start_x, end_x, mid_y):
        segment_length = (end_x - start_x) // 4
        for i in range(4):
            height = np.random.uniform(platform_height_min, platform_height_max)
            height_field[start_x + i * segment_length: start_x + (i + 1) * segment_length, mid_y - narrow_width // 2: mid_y + narrow_width // 2] = height
    
    # Dimension Setup
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.4)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.25 + 0.3 * difficulty
    gap_length = 0.3 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)

    narrow_width = m_to_idx(0.2 + 0.6 * difficulty)

    mid_y = m_to_idx(width) // 2
    
    # Set initial spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    # Sequence of ramps and obstacles
    for i in range(7):
        if i % 2 == 0:
            # Ramp
            slope_up = np.random.choice([True, False])
            add_ramp(cur_x, cur_x + platform_length, mid_y, slope_up)
        else:
            # Beam or Irregular Step
            if np.random.rand() < 0.5:
                add_beam(cur_x, cur_x + platform_length, mid_y, narrow_width)
            else:
                add_irregular_step(cur_x, cur_x + platform_length, mid_y)
 
        goals[i + 1] = [cur_x + platform_length / 2, mid_y]
        cur_x += platform_length + gap_length

    # Set remaining area to be flat ground
    height_field[cur_x:, :] = 0
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    return height_field, goals

def set_terrain_4(length, width, field_resolution, difficulty):
    """Variable-height platforms with moderate-sized gaps to enhance agility and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions
    platform_length_min = 0.8 - 0.2 * difficulty
    platform_length_max = platform_length_min + 0.5
    platform_width = np.random.uniform(1.2, 1.5)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1, 0.4 * difficulty
    gap_length_min = 0.1 + 0.2 * difficulty
    gap_length_max = 0.3 + 0.3 * difficulty

    mid_y = m_to_idx(width) // 2    

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_gap(start_x, length):
        x1, x2 = start_x, start_x + length
        height_field[x1:x2, :] = -1.0

    # Flatten the spawn area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(4):
        if i % 2 == 0:
            platform_length = np.random.uniform(platform_length_min, platform_length_max)
            platform_length = m_to_idx(platform_length)
            platform_height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)
            goals[i + 1] = [cur_x + platform_length / 2, mid_y]
            cur_x += platform_length
        else:
            gap_length = np.random.uniform(gap_length_min, gap_length_max)
            gap_length = m_to_idx(gap_length)
            add_gap(cur_x, gap_length)
            cur_x += gap_length

    for i in range(4, 8):
        platform_length = np.random.uniform(platform_length_min, platform_length_max)
        platform_length = m_to_idx(platform_length)
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)
        goals[i] = [cur_x + platform_length / 2, mid_y]
        cur_x += platform_length
        
        if i < 7: # avoid unnecessary gap after the last goal
            gap_length = np.random.uniform(gap_length_min, gap_length_max)
            gap_length = m_to_idx(gap_length)
            add_gap(cur_x, gap_length)
            cur_x += gap_length

    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_5(length, width, field_resolution, difficulty):
    """Combination of varied height platforms, narrow walkways, and ramps to challenge the robot's agility, balance, and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up obstacle dimensions
    platform_length = 1.0 - 0.3 * difficulty  # Shorter with higher difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.0)  # Narrower with higher difficulty
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1, 0.4 + 0.3 * difficulty
    ramp_length = 1.0 - 0.2 * difficulty
    ramp_length = m_to_idx(ramp_length)
    gap_length = m_to_idx(0.4 + 0.4 * difficulty)  # Longer gaps with higher difficulty
    
    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_ramp(start_x, end_x, mid_y, start_height, end_height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        z_values = np.linspace(start_height, end_height, num=x2-x1)[:, None]
        height_field[x1:x2, y1:y2] = z_values

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # First goal at the spawn area
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    obstacle_sequence = ["platform", "ramp_up", "narrow_walkway", "variable_height_platform", "gap", "ramp_down"]
    goal_idx = 1

    for obstacle in obstacle_sequence:
        dx = np.random.randint(-1, 2)

        if obstacle == "platform":
            platform_height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, cur_x + platform_length + dx, mid_y, platform_height)
            goals[goal_idx] = [cur_x + (platform_length + dx) / 2, mid_y]
            cur_x += platform_length + dx + gap_length

        elif obstacle == "ramp_up":
            ramp_height = np.random.uniform(0.2 + difficulty * 0.3, 0.5 + difficulty * 0.3)
            add_ramp(cur_x, cur_x + ramp_length, mid_y, 0.0, ramp_height)
            goals[goal_idx] = [cur_x + ramp_length / 2, mid_y]
            cur_x += ramp_length + gap_length

        elif obstacle == "narrow_walkway":
            walkway_length = platform_length // 2
            walkway_width = np.random.uniform(0.4, 0.6)
            walkway_width = m_to_idx(walkway_width)
            add_platform(cur_x, cur_x + walkway_length, mid_y, 0.0)
            goals[goal_idx] = [cur_x + walkway_length / 2, mid_y]
            cur_x += walkway_length + gap_length

        elif obstacle == "variable_height_platform":
            platform_height_1 = np.random.uniform(platform_height_min, platform_height_max)
            platform_height_2 = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, cur_x + platform_length // 2, mid_y, platform_height_1)
            cur_x += platform_length // 2 + gap_length // 2
            add_platform(cur_x, cur_x + platform_length // 2, mid_y, platform_height_2)
            goals[goal_idx] = [cur_x - (platform_length // 2 + gap_length // 2) / 2, mid_y]
            cur_x += platform_length // 2 + gap_length

        elif obstacle == "gap":
            add_platform(cur_x + gap_length, cur_x + gap_length + platform_length + dx, mid_y, platform_height_min)
            goals[goal_idx] = [cur_x + gap_length + (platform_length + dx) / 2, mid_y]
            cur_x += gap_length + platform_length + dx + gap_length

        elif obstacle == "ramp_down":
            add_ramp(cur_x, cur_x + ramp_length, mid_y, platform_height_max, 0.0)
            goals[goal_idx] = [cur_x + ramp_length / 2, mid_y]
            cur_x += ramp_length + gap_length

        goal_idx += 1

    # Final goal behind the last platform
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_6(length, width, field_resolution, difficulty):
    """Combination of ramps, platforms, and narrow paths to test agility, balance, and climbing skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define obstacle sizes based on difficulty
    platform_length = 0.8 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.2)
    platform_width = m_to_idx(platform_width)
    platform_height_range = [0.03 + 0.2 * difficulty, 0.1 + 0.3 * difficulty]
    ramp_height_range = [0.05 + 0.3 * difficulty, 0.15 + 0.4 * difficulty]
    narrow_path_width = 0.5 - 0.2 * difficulty
    narrow_path_width = m_to_idx(narrow_path_width)
    gap_length = 0.15 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, y_center, height):
        half_width = platform_width // 2
        y1, y2 = y_center - half_width, y_center + half_width
        height_field[start_x:end_x, y1:y2] = height

    def add_ramp(start_x, end_x, y_center, height, direction):
        half_width = platform_width // 2
        slope = np.linspace(0, height, end_x - start_x)[::direction]
        height_field[start_x:end_x, y_center-half_width:y_center+half_width] = slope[:, None] + np.zeros((end_x - start_x, 2 * half_width))

    def add_narrow_path(start_x, end_x, y_center, height):
        half_width = narrow_path_width // 2
        y1, y2 = y_center - half_width, y_center + half_width
        height_field[start_x:end_x, y1:y2] = height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(1, 7):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        if i % 2 == 0:
            # Add platform
            platform_height = np.random.uniform(*platform_height_range)
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height)
        elif i % 3 == 0:
            # Add ramp
            ramp_height = np.random.uniform(*ramp_height_range)
            direction = (-1) ** i  # Alternate direction to add variability
            add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, ramp_height, direction)
        else:
            # Add narrow path
            narrow_height = np.random.uniform(*platform_height_range)
            add_narrow_path(cur_x, cur_x + platform_length + dx, mid_y + dy, narrow_height)

        goals[i] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_7(length, width, field_resolution, difficulty):
    """Slanted platforms and narrow pathways to challenge agility and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Configure platform and pathway dimensions
    platform_length = 0.9 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    path_length = 1.2
    path_length = m_to_idx(path_length)
    platform_width = 1.0
    platform_width = m_to_idx(platform_width)
    path_width = 0.35 + 0.15 * difficulty
    path_width = m_to_idx(path_width)
    platform_height_min, platform_height_max = 0.2 * difficulty, 0.3 + 0.5 * difficulty
    path_height_min, path_height_max = 0.1 + 0.2 * difficulty, 0.15 + 0.25 * difficulty
    gap_length = 0.2 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_narrow_path(start_x, end_x, mid_y, height):
        half_width = path_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_slanted_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        slant = np.linspace(0, platform_height, num=(y2 - y1))
        slant = slant[None, :]  # Add a dimension for broadcasting to x
        height_field[x1:x2, y1:y2] = slant

    # Set up flat spawn area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # Start location

    cur_x = spawn_length

    # Platform 1 - narrow path
    path_height = np.random.uniform(path_height_min, path_height_max)
    add_narrow_path(cur_x, cur_x + path_length, mid_y, path_height)
    goals[1] = [cur_x + path_length / 2, mid_y]
    cur_x += path_length + gap_length

    # Platform 2 - slanted platform
    add_slanted_platform(cur_x, cur_x + platform_length, mid_y)
    goals[2] = [cur_x + platform_length / 2, mid_y]
    cur_x += platform_length + gap_length

    # Platform 3 - narrow path
    path_height = np.random.uniform(path_height_min, path_height_max)
    add_narrow_path(cur_x, cur_x + path_length, mid_y - m_to_idx(0.2), path_height)  # Shift slightly downward
    goals[3] = [cur_x + path_length / 2, mid_y - m_to_idx(0.2)]
    cur_x += path_length + gap_length

    # Platform 4 - slanted platform
    add_slanted_platform(cur_x, cur_x + platform_length, mid_y + m_to_idx(0.2))  # Shift slightly upward
    goals[4] = [cur_x + platform_length / 2, mid_y + m_to_idx(0.2)]
    cur_x += platform_length + gap_length

    # Platform 5 - narrow path
    path_height = np.random.uniform(path_height_min, path_height_max)
    add_narrow_path(cur_x, cur_x + path_length, mid_y, path_height)
    goals[5] = [cur_x + path_length / 2, mid_y]
    cur_x += path_length + gap_length

    # Platform 6 - slanted platform
    add_slanted_platform(cur_x, cur_x + platform_length, mid_y)
    goals[6] = [cur_x + platform_length / 2, mid_y]
    cur_x += platform_length + gap_length

    # Final goal after the last slanted platform
    goals[7] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_8(length, width, field_resolution, difficulty):
    """Alternating stepping stones with varying heights and turning points to enhance agility, precision, and turning navigation."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up stepping stone dimensions
    stone_length = m_to_idx(0.4)
    stone_width = m_to_idx(0.4)
    stone_height_min, stone_height_max = 0.1 * difficulty, 0.5 * difficulty
    gap_length_min, gap_length_max = m_to_idx(0.3), m_to_idx(0.8)

    mid_y = m_to_idx(width) // 2

    def add_stepping_stone(start_x, mid_y, length, width, height):
        """Add a raised stepping stone."""
        half_width = width // 2
        x1, x2 = start_x, start_x + length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    for i in range(7):
        gap_length = np.random.randint(gap_length_min, gap_length_max)
        stone_height = np.random.uniform(stone_height_min, stone_height_max)
        direction = i % 2  # Alternate the direction to create turning points
        offset_y = m_to_idx(0.4) if direction else -m_to_idx(0.4)

        add_stepping_stone(cur_x, mid_y + offset_y, stone_length, stone_width, stone_height)
        goals[i + 1] = [cur_x + stone_length / 2, mid_y + offset_y]

        cur_x += stone_length + gap_length

    # Final gap and goal
    cur_x += np.random.randint(gap_length_min, gap_length_max)
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_9(length, width, field_resolution, difficulty):
    """Enhanced multiple platforms with gentle slopes and gaps for the robot to climb and jump across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and slope dimensions
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.2)  # Slightly narrower paths
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.2 + 0.3 * difficulty
    slope_height_min, slope_height_max = 0.05 + 0.25 * difficulty, 0.2 + 0.35 * difficulty
    gap_length = 0.2 + 0.6 * difficulty  # Increased gap length
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_slope(start_x, end_x, mid_y, height, direction):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slope = np.linspace(0, height, num=x2-x1)
        slope = slope[:, None]  # Add a dimension for broadcasting to y
        height_field[x1:x2, y1:y2] = slope

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
    # We do this to force the robot to jump from platform to platform
    # Otherwise, the robot can just jump down and climb back up
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    for i in range(4):
        # Add platform
        height = np.random.uniform(platform_height_min, platform_height_max)
        add_platform(cur_x, cur_x + platform_length, mid_y, height)
        goals[i * 2 + 1] = [cur_x + platform_length / 2, mid_y]
        cur_x += platform_length

        # Add slope, alternating up and down slopes
        if i != 3:  # No slope after final platform
            direction = (-1) ** i  # Alternate up and down slopes
            height = np.random.uniform(slope_height_min, slope_height_max)
            add_slope(cur_x, cur_x + platform_length, mid_y, height, direction)
            goals[i * 2 + 2] = [cur_x + platform_length / 2, mid_y]
            cur_x += platform_length + gap_length

    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

# INSERT TERRAIN FUNCTION DEFINITIONS HERE
