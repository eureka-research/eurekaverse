
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
    Combination of vertical walls, narrow paths, high platforms, and angled ramps to challenge climbing and balance.
    """
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]
    
    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    
    # Dimensions and parameters for obstacles
    platform_length = 0.8 - 0.2 * difficulty  # Smaller platforms at higher difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.4, 0.6)  # Narrow paths
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.15 + 0.3 * difficulty, 0.25 + 0.4 * difficulty
    ramp_height_min, ramp_height_max = 0.2 + 0.3 * difficulty, 0.3 + 0.5 * difficulty
    gap_length = 0.25 + 0.75 * difficulty  # Wider gaps at higher difficulty
    gap_length = m_to_idx(gap_length)
    
    def add_vertical_wall(start_x, end_x, mid_y):
        height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[start_x:end_x, mid_y] = height

    def add_narrow_path(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        path_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = path_height

    def add_ramp(start_x, end_x, mid_y, direction):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        slant = np.linspace(0, ramp_height, num=y2-y1)[::direction]
        slant = slant[None, :]  # Add a dimension for broadcasting to x
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.05, 0.05  # Smaller x variations to ensure obstacle spacing
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.1, 0.4  # Slightly larger y offsets for increased lateral movement
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Initial flat spawn area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length + m_to_idx(0.2), m_to_idx(width) // 2]

    cur_x = spawn_length + m_to_idx(0.5)
    mid_y = m_to_idx(width) // 2
    current_goal_index = 1  # Start from the second goal

    # Adding vertical walls
    for i in range(2):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_vertical_wall(cur_x, cur_x + platform_length + dx, mid_y + dy)
        goals[current_goal_index] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length
        current_goal_index += 1

    # Adding narrow paths
    for i in range(2):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_narrow_path(cur_x, cur_x + platform_length + dx, mid_y + dy)
        goals[current_goal_index] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length
        current_goal_index += 1

    # Adding ramps
    for i in range(2):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        direction = (-1) ** i  # Alternating left and right ramps
        dy = dy * direction  # Alternate positive and negative y offsets
        add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, direction)
        goals[current_goal_index] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length
        current_goal_index += 1

    # Adding final goal behind the last obstacle
    goals[current_goal_index] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0  # Smooth landing area

    return height_field, goals

def set_terrain_1(length, width, field_resolution, difficulty):
    """Combination of narrow beams, variable-height steps, and wide gaps for advanced navigation and balance testing."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.2)  # Slightly narrower platforms
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.2 + 0.3 * difficulty
    gap_length = 0.2 + 0.5 * difficulty  # Moderate gaps
    gap_length = m_to_idx(gap_length)

    beam_width = np.random.uniform(0.4, 0.6)  # Narrower beams
    beam_width = m_to_idx(beam_width)
    beam_height = np.random.uniform(0.25, 0.4)  # Higher beams for balance

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
        height_field[x1:x2, y1:y2] = beam_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at spawn

    cur_x = spawn_length
    for i in range(2):  # Initial two standard platforms
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

    for i in range(3):  # Next three narrow beams
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_beam(cur_x, cur_x + platform_length + dx, mid_y + dy)  # Narrow beams for balance
        goals[i+3] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

    for i in range(2):  # Final two wider platforms with heights
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
        goals[i+6] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_2(length, width, field_resolution, difficulty):
    """Narrow beams, varying height platforms, and small ramps for enhanced precision and agility."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_height_min, platform_height_max = 0.05 + 0.2 * difficulty, 0.1 + 0.3 * difficulty
    beam_width = m_to_idx(np.random.uniform(0.4, 0.6))
    small_ramp_height = 0.1 + 0.3 * difficulty
    small_ramp_length = m_to_idx(1.0)

    mid_y = m_to_idx(width) // 2
    spawn_length = m_to_idx(2)

    def add_platform(start_x, end_x, mid_y, height):
        half_width = m_to_idx(0.8) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_beam(start_x, end_x, mid_y):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = 0  # Beams are flat but narrow

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

    # Sequence of 6 obstacles mixing beams, platforms, and small ramps
    for i in range(6):
        if i % 3 == 0:
            beam_length = np.random.randint(m_to_idx(1.0), m_to_idx(1.5))
            add_beam(cur_x, cur_x + beam_length, mid_y)
            goals[i + 1] = [cur_x + beam_length // 2, mid_y]
            cur_x += beam_length + m_to_idx(0.3)
        elif i % 3 == 1:
            platform_length = np.random.randint(m_to_idx(1.0), m_to_idx(1.2))
            platform_height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)
            goals[i + 1] = [cur_x + platform_length // 2, mid_y]
            cur_x += platform_length + m_to_idx(0.3)
        else:
            ramp_height = np.random.uniform(small_ramp_height / 2, small_ramp_height)
            add_ramp(cur_x, cur_x + small_ramp_length, mid_y, 0, ramp_height, "up")
            goals[i + 1] = [cur_x + small_ramp_length // 2, mid_y]
            cur_x += small_ramp_length + m_to_idx(0.3)

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_3(length, width, field_resolution, difficulty):
    """Combination of staggered platforms, sloped ramps, and intermediate stepping stones."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Terrain dimension setup
    platform_length = 1.2 - 0.4 * difficulty  # Decreased length for higher difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.2)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.2 + 0.4 * difficulty
    gap_length = 0.3 + 0.4 * difficulty  # Increased gap length
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[start_x:end_x, y1:y2] = height

    def add_ramp(start_x, end_x, mid_y, ramp_height, ascend=True):
        half_width = platform_width // 2
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_range = np.linspace(0, ramp_height, end_x - start_x) if ascend else np.linspace(ramp_height, 0, end_x - start_x)
        height_field[start_x:end_x, y1:y2] = height_range[:, None]

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground and initial goal
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(4):  # Introduction of stairs, platforms and alternating ramps
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        if i % 3 == 0:
            height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, height)
            goals[i+1] = [cur_x + platform_length // 2, mid_y + dy]
        elif i % 3 == 1:
            ramp_height = np.random.uniform(platform_height_min, platform_height_max)
            add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, ramp_height, ascend=True)
            goals[i+1] = [cur_x + platform_length // 2, mid_y + dy]
        else:
            ramp_height = np.random.uniform(platform_height_min, platform_height_max)
            add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, ramp_height, ascend=False)
            goals[i+1] = [cur_x + platform_length // 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

    # Final straight stretch with small stepping stones
    stone_width = m_to_idx(0.4)
    num_stones = 3
    stone_heights = np.linspace(0.1, 0.3, num_stones)
    for j in range(num_stones):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        stone_x = cur_x + j * (stone_width + gap_length // num_stones)
        add_platform(stone_x, stone_x + stone_width + dx, mid_y + dy, stone_heights[j])
        goals[5 + j] = [stone_x + stone_width // 2, mid_y + dy]
    cur_x += num_stones * (stone_width + gap_length // num_stones)

    # Final goal behind the last small platform
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_4(length, width, field_resolution, difficulty):
    """Combination of alternating ramps, platforms, and narrow walkways to test comprehensive skills including balance, agility, and trajectory control."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_height_min, platform_height_max = 0.0 + 0.2 * difficulty, 0.05 + 0.25 * difficulty
    ramp_height_min, ramp_height_max = 0.0 + 0.5 * difficulty, 0.05 + 0.55 * difficulty
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    gap_length = 0.2 + 0.4 * difficulty  # Moderate gap lengths
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, width, height):
        half_width = m_to_idx(width) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_ramp(start_x, end_x, mid_y, width, height, direction):
        half_width = m_to_idx(width) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slant = np.linspace(0, height, num=x2-x1)[::direction]
        slant = slant[:, None]  # Add a dimension for broadcasting to y
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)
    
    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    # Add first straightforward platform
    for i in range(4):
        if i % 2 == 0:  # Alternate between platform and ramp
            platform_height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, cur_x + platform_length, mid_y, np.random.uniform(1.0, 1.3), platform_height)
            goals[i+1] = [cur_x + platform_length / 2, mid_y]
            cur_x += platform_length + gap_length
        else:
            ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
            add_ramp(cur_x, cur_x + platform_length, mid_y, np.random.uniform(0.8, 1.2), ramp_height, (-1) ** i)
            goals[i+1] = [cur_x + platform_length / 2, mid_y]
            cur_x += platform_length + gap_length

        # Add slalom-type pattern with goals slightly offset
        if i % 2 == 0 and i != 0:
            dy = np.random.randint(dy_min, dy_max)
            cur_y = mid_y + dy
            if cur_y < m_to_idx(1.0 / 2) or cur_y > m_to_idx(width - 1.0 / 2):
                dy = -dy
            goals[i+1, 1] += dy

    # Add final goal behind the last obstacle, ensure it's achievable
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_5(length, width, field_resolution, difficulty):
    """Combination of platforms, ramps, and slalom barriers for agility and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not isinstance(m, (list, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform and ramp dimensions
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.6)
    platform_width = m_to_idx(platform_width)

    min_platform_height = 0.1
    max_platform_height = min_platform_height + (difficulty * 0.2)
    min_ramp_height = 0.1 * difficulty
    max_ramp_height = 0.5 * difficulty

    gap_length = 0.3 + (0.3 * difficulty)
    gap_length = m_to_idx(gap_length)

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
        z_values = np.linspace(start_height, end_height, num=x2 - x1)[:, None]
        height_field[x1:x2, y1:y2] = z_values

    def add_slalom_barrier(x, mid_y, height):
        width = m_to_idx(0.4)  # Narrow slalom
        half_width = width // 2
        x1, y1, y2 = x, mid_y - half_width, mid_y + half_width
        height_field[x1, y1:y2] = height

    # Set starting area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Initial flat platform
    cur_x = spawn_length
    platform_height = np.random.uniform(min_platform_height, max_platform_height)
    add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)
    goals[1] = [cur_x + platform_length / 2, mid_y]

    # First ramp
    cur_x += platform_length + gap_length
    ramp_height = np.random.uniform(min_ramp_height, max_ramp_height)
    add_ramp(cur_x, cur_x + platform_length, mid_y, 0, ramp_height)
    goals[2] = [cur_x + platform_length / 2, mid_y]

    # First slalom barrier
    cur_x += platform_length + gap_length
    barrier_height = np.random.uniform(min_platform_height, max_platform_height)
    add_slalom_barrier(cur_x, mid_y, barrier_height)
    goals[3] = [cur_x + gap_length / 2, mid_y + m_to_idx(0.5) * (-1) ** 3]  # Left or right

    # Second platform
    cur_x += gap_length
    platform_height = np.random.uniform(min_platform_height, max_platform_height)
    add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)
    goals[4] = [cur_x + platform_length / 2, mid_y]

    # Second ramp
    cur_x += platform_length + gap_length
    ramp_height = np.random.uniform(min_ramp_height, max_ramp_height)
    add_ramp(cur_x, cur_x + platform_length, mid_y, 0, ramp_height)
    goals[5] = [cur_x + platform_length / 2, mid_y]

    # Second slalom barrier
    cur_x += platform_length + gap_length
    barrier_height = np.random.uniform(min_platform_height, max_platform_height)
    add_slalom_barrier(cur_x, mid_y, barrier_height)
    goals[6] = [cur_x + gap_length / 2, mid_y + m_to_idx(0.5) * (-1) ** 4]  # Left or right

    # Final platform and goal
    cur_x += gap_length
    platform_height = np.random.uniform(min_platform_height, max_platform_height)
    add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)
    goals[7] = [cur_x + platform_length + m_to_idx(0.5), mid_y]

    return height_field, goals

def set_terrain_6(length, width, field_resolution, difficulty):
    """Terrain with varied climbing obstacles, sideways ramps, and stepping stones to test agility, precision, and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up obstacle dimensions
    step_size = m_to_idx(0.4 + 0.2 * difficulty)
    platform_width_min, platform_width_max = 0.6, 1.0 - 0.2 * difficulty
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.2 + 0.4 * difficulty
    gap_length_min, gap_length_max = 0.2 + 0.3 * difficulty, 0.4 + 0.5 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = np.random.uniform(platform_width_min, platform_width_max) / 2
        half_width = m_to_idx(half_width)
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_ramp(start_x, end_x, mid_y, start_height, end_height):
        half_width = np.random.uniform(platform_width_min, platform_width_max) / 2
        half_width = m_to_idx(half_width)
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_heights = np.linspace(start_height, end_height, x2 - x1)[:, None]
        height_field[x1:x2, y1:y2] = ramp_heights

    def add_stepping_stones(start_x, mid_y, num_stones, step_height):
        half_step = step_size // 2
        for i in range(num_stones):
            x1, x2 = start_x + i * step_size, start_x + (i + 1) * step_size
            y1, y2 = mid_y - half_step, mid_y + half_step
            height_field[x1:x2, y1:y2] = step_height
    
    # Flattens initial spawn area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Generate obstacles
    cur_x = spawn_length
    for i in range(3):  # Steps and platforms alternation
        # Add stepping stones
        gap_length = np.random.uniform(gap_length_min, gap_length_max)
        cur_x += m_to_idx(gap_length)
        add_stepping_stones(cur_x, mid_y, 3, np.random.uniform(platform_height_min, platform_height_max))
        goals[i+1] = [cur_x + 1.5 * step_size, mid_y]

        # Add platform
        gap_length = np.random.uniform(gap_length_min, gap_length_max)
        cur_x += m_to_idx(gap_length)
        end_x = cur_x + m_to_idx(np.random.uniform(1.0, 1.5))
        add_platform(cur_x, end_x, mid_y, np.random.uniform(platform_height_min, platform_height_max))
        goals[i+2] = [(cur_x + end_x) / 2, mid_y]
        cur_x = end_x

    # Add a ramp
    gap_length = np.random.uniform(gap_length_min, gap_length_max)
    cur_x += m_to_idx(gap_length)
    end_x = cur_x + m_to_idx(np.random.uniform(1.0, 1.5))
    add_ramp(cur_x, end_x, mid_y, np.random.uniform(platform_height_min, platform_height_max), np.random.uniform(platform_height_min, platform_height_max + 0.2))
    goals[5] = [(cur_x + end_x) / 2, mid_y]
    cur_x = end_x

    for i in range(6, 7):  # Add final set of stepping stones
        gap_length = np.random.uniform(gap_length_min, gap_length_max)
        cur_x += m_to_idx(gap_length)
        add_stepping_stones(cur_x, mid_y, 3, np.random.uniform(platform_height_min, platform_height_max))
        goals[i] = [cur_x + 1.5 * step_size, mid_y]

    # Add final goal
    cur_x += m_to_idx(gap_length_max)
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_7(length, width, field_resolution, difficulty):
    """Combo of raised platforms, inclined planes, and stepping paths to test agility and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform and obstacle dimensions
    platform_length = 0.8 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.4)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.2 * difficulty, 0.3 + 0.25 * difficulty
    slant_length = 1.0
    slant_length = m_to_idx(slant_length)
    gap_length = 0.1 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_slant(start_x, end_x, mid_y, height_diff):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slant = np.linspace(0, height_diff, num=x2-x1)[:, None]
        height_field[x1:x2, y1:y2] = slant

    # Set the starting section flat
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0  
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length

    # First platform
    platform_height = np.random.uniform(platform_height_min, platform_height_max)
    add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)
    goals[1] = [cur_x + platform_length / 2, mid_y]
    cur_x += platform_length + gap_length

    # Alternating platforms and slopes
    for i in range(1, 6):
        if i % 2 == 0:
            # Add Platform
            platform_height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)
            goal_pos = cur_x + platform_length / 2
        else:
            # Add Slant
            slant_height_diff = np.random.uniform(0.2 * difficulty, 0.4 * difficulty)
            add_slant(cur_x, cur_x + slant_length, mid_y, slant_height_diff)
            goal_pos = cur_x + slant_length / 2
        cur_x += platform_length + gap_length
        goals[i + 1] = [goal_pos, mid_y]
    
    # Last gap and final goal
    final_goal_pos = cur_x + gap_length
    goals[-1] = [final_goal_pos, mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_8(length, width, field_resolution, difficulty):
    """Terrain with intermittent obstacle rows and balance beams that traverses narrow paths for added complexity and challenge."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    mid_y = m_to_idx(width) // 2

    # Platform dimensions
    obstacle_height_min, obstacle_height_max = 0.2 * difficulty, 0.4 * difficulty
    obstacle_length = m_to_idx(0.5)
    beam_width = m_to_idx(0.2 + 0.2 * (1 - difficulty))  # Narrows with increasing difficulty
    path_length = m_to_idx(1.0)
    gap_length_min, gap_length_max = m_to_idx(0.1 + 0.1 * difficulty), m_to_idx(0.3 + 0.4 * difficulty)

    def add_obstacle_row(start_x, end_x, mid_y, height):
        """Add an obstacle row."""
        y1, y2 = mid_y - beam_width // 2, mid_y + beam_width // 2
        x1, x2 = start_x, end_x
        height_field[x1:x2, y1:y2] = height

    def add_balance_beam(start_x, end_x, mid_y):
        """Add a balance beam."""
        y1, y2 = mid_y - beam_width // 2, mid_y + beam_width // 2
        x1, x2 = start_x, end_x
        height_field[x1:x2, y1:y2] = 0.1 + 0.3 * difficulty

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # First goal positioned at spawn point
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    
    # Setup terrain
    for i in range(7):
        obstacle_height = np.random.uniform(obstacle_height_min, obstacle_height_max)
        
        # Add even-indexed obstacle rows
        if i % 2 == 0:
            cur_x += gap_length_max // 2
            add_obstacle_row(cur_x, cur_x + obstacle_length, mid_y, obstacle_height)
            cur_x += obstacle_length + gap_length_max // 2
            goals[i+1] = [cur_x - obstacle_length // 2, mid_y]
        
        # Add odd-indexed balance beams
        else:
            add_balance_beam(cur_x, cur_x + path_length, mid_y)
            cur_x += path_length + gap_length_min
            goals[i+1] = [cur_x - path_length // 2, mid_y]

    # Add final goal behind the last balance beam or obstacle row
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_9(length, width, field_resolution, difficulty):
    """Variable-height platforms and controlled gaps for challenging the quadruped's precision and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define platform and gap parameters
    platform_length = 0.8 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.6, 0.8)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.05 + 0.2 * difficulty, 0.2 + 0.4 * difficulty
    gap_length = 0.3 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    dx_min, dx_max = -0.05, 0.05
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Initial flat ground for spawn area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    for i in range(6):  # Setting up 6 platforms with gaps in between
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
        goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        cur_x += platform_length + dx + gap_length

    # Final flat ground area similar to the initial for stability before end
    final_length = m_to_idx(1)
    add_platform(cur_x, cur_x + final_length, mid_y)
    goals[-1] = [cur_x + final_length / 2, mid_y]

    return height_field, goals

# INSERT TERRAIN FUNCTION DEFINITIONS HERE
