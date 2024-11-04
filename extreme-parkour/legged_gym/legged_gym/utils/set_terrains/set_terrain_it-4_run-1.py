
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
    """Dynamic terrain with moving platforms and varying heights for the robot to balance, climb, and jump across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length = 0.4
    platform_length = m_to_idx(platform_length)
    platform_width = 1.0
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.2 * difficulty, 0.1 + 0.3 * difficulty
    gap_length_min, gap_length_max = 0.2, 0.6 + 0.5 * difficulty
    gap_length_min, gap_length_max = m_to_idx(gap_length_min), m_to_idx(gap_length_max)

    ramp_length = 0.8
    ramp_length = m_to_idx(ramp_length)
    ramp_height_min, ramp_height_max = 0.2, 0.4 + 0.3 * difficulty
    
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

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at spawn

    cur_x = spawn_length

    for i in range(4):
        dx = np.random.randint(gap_length_min, gap_length_max)
        dy = np.random.randint(m_to_idx(0.0), m_to_idx(0.6))

        if i % 2 == 0:
            add_platform(cur_x, cur_x + platform_length, mid_y + dy)
            goals[i + 1] = [cur_x + platform_length // 2, mid_y + dy]
        else:
            add_ramp(cur_x, cur_x + ramp_length, mid_y + dy, direction=(-1) ** i)
            goals[i + 1] = [cur_x + ramp_length // 2, mid_y + dy]

        cur_x += platform_length + dx if i % 2 == 0 else ramp_length + dx

    # Adding final straight-run obstacle and a final goal
    final_run_length = m_to_idx(2.5)
    final_run_ramp = m_to_idx(2.0)
    final_run_height = np.random.uniform(0.2, 0.3 + 0.1 * difficulty)
    half_width = platform_width // 2
    y1, y2 = mid_y - half_width, mid_y + half_width
    ramp_height = np.linspace(0, final_run_height, num=final_run_ramp)
    height_field[cur_x:cur_x + final_run_ramp, y1:y2] = ramp_height[:, np.newaxis]
    cur_x += final_run_ramp

    y_current = height_field[cur_x:cur_x + final_run_length, y1:y2][-1, 0]
    height_field[cur_x:cur_x + final_run_length, y1:y2] = y_current  # Ending straight path

    goals[-1] = [cur_x + final_run_length // 2, mid_y]

    return height_field, goals

def set_terrain_1(length, width, field_resolution, difficulty):
    """Combines narrow beams, ramps, and staggered platforms to increase the difficulty for the robot."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    def add_beam(start_x, end_x, center_y, width, height):
        """Adds a narrow beam at specified x and y coordinates."""
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = center_y - half_width, center_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_ramp(start_x, end_x, center_y, width, height_diff, direction):
        """Adds a ramp at specified x and y coordinates."""
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = center_y - half_width, center_y + half_width
        slant = np.linspace(0, height_diff, num=y2-y1 if direction else x2-x1)
        if direction:
            slant = slant[None, :]  # Ramp along y-axis
        else:
            slant = slant[:, None]  # Ramp along x-axis
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), m_to_idx(width) // 2]  

    platform_length = 1.0 - 0.2 * difficulty
    platform_width = 0.4 + 0.2 * difficulty
    platform_height_min, platform_height_max = 0.1 + 0.3 * difficulty, 0.3 + 0.4 * difficulty
    platform_length, platform_width = m_to_idx(platform_length), m_to_idx(platform_width)
    gap_length = 0.2 + 0.8 * difficulty
    gap_length = m_to_idx(gap_length)
    mid_y = m_to_idx(width) // 2

    cur_x = spawn_length
    for i in range(6):  # Set up platforms, ramps, and narrow beams
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        if i % 3 == 0:  # Build beam
            beam_width = m_to_idx(0.3)
            beam_height = np.random.uniform(platform_height_min, platform_height_max)
            add_beam(cur_x, cur_x + platform_length + dx, mid_y + dy, beam_width, beam_height)
        elif i % 3 == 1:  # Build ramp
            ramp_height_diff = np.random.uniform(platform_height_min, platform_height_max)
            add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_width, ramp_height_diff, direction=(i % 2 == 0))
        else:  # Build platform
            add_beam(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_width, np.random.uniform(platform_height_min, platform_height_max))
            
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        cur_x += platform_length + dx + gap_length

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_2(length, width, field_resolution, difficulty):
    """Stepped platforms and narrow beams at varying heights and widths for the quadruped to navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform and beam configurations
    platform_length = 0.5  # Shorter platforms
    platform_length = m_to_idx(platform_length)
    platform_width = 0.5  # Shorter width for complexity
    platform_width = m_to_idx(platform_width)
    beam_length = 1.0 - 0.3 * difficulty  # Slightly longer beams
    beam_length = m_to_idx(beam_length)
    beam_width_factor = 1.0 - 0.7 * difficulty  # Adjustable width
    beam_width_min = max(m_to_idx(0.1), m_to_idx(beam_width_factor * 0.28))
    beam_width_max = m_to_idx(0.4)
    gap_length = 0.2 + 0.2 * difficulty  # Adjustable gaps
    gap_length = m_to_idx(gap_length)
    platform_height_min = 0.1
    platform_height_max = 0.3 + 0.3 * difficulty  # Adjustable height ranges

    mid_y = m_to_idx(width) // 2

    def add_platform_beam(start_x, end_x, mid_y, height, use_beam=False):
        half_width = beam_width_max // 2 if use_beam else platform_width // 2
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[start_x:end_x, y1:y2] = height

    dx_min, dx_max = -0.2, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.15, 0.15
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Flat start area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Create obstacles with alternating platforms and beams
    cur_x = spawn_length
    for i in range(6):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        if i % 2 == 0:
            # Platforms
            platform_height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform_beam(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height)
            
            # Place goal in the center of the platform
            goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
            cur_x += platform_length + dx + gap_length
        else:
            # Beams
            beam_width = np.random.randint(beam_width_min, beam_width_max)
            beam_height = np.random.uniform(platform_height_min, platform_height_max)
            
            half_width = beam_width // 2
            add_platform_beam(cur_x, cur_x + beam_length + dx, mid_y + dy, beam_height, use_beam=True)

            # Place goal in the center of the beam
            goals[i+1] = [cur_x + (beam_length + dx) / 2, mid_y + dy]
            cur_x += beam_length + dx + gap_length

    # Final goal placement
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_3(length, width, field_resolution, difficulty):
    """Narrow paths, higher platforms, and wider gaps for comprehensive balance, navigation, and jumping challenges."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform and gap dimension variables
    platform_length = 0.8 - 0.3 * difficulty  # Increasing difficulty decreases platform size
    platform_length = m_to_idx(platform_length)
    platform_width = 0.6 + 0.3 * difficulty  # Making the platform width narrower with increased difficulty
    platform_width = m_to_idx(platform_width)
    platform_height_min = 0.2 + 0.3 * difficulty  # Taller platforms
    platform_height_max = 0.4 + 0.4 * difficulty
    gap_length = 0.2 + 0.8 * difficulty  # Wider gaps
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, center_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = center_y - half_width, center_y + half_width
        height_field[x1:x2, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[:spawn_length, :] = 0  # Ensuring flat spawn area
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at spawn

    last_x = spawn_length
    for i in range(1, 8):
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        start_x = last_x + gap_length
        end_x = start_x + platform_length

        center_y_offset = (-1) ** i * np.random.randint(0, m_to_idx(0.3))  # alternating offsets

        add_platform(start_x, end_x, mid_y + center_y_offset, platform_height)

        goals[i] = [start_x + platform_length / 2, mid_y + center_y_offset]

        last_x = end_x

    return height_field, goals

def set_terrain_4(length, width, field_resolution, difficulty):
    """Combination of staggered elevated platforms, directional ramps, and narrow balance beams to challenge navigation, balance, and agility."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    mid_y = m_to_idx(width) // 2

    platform_min_len, platform_max_len = 0.8, 1.2  # meters
    platform_min_width, platform_max_width = 0.4, 0.8  # meters
    platform_height_min, platform_height_max = 0.1, 0.3 + 0.2 * difficulty  # meters
    gap_min_len, gap_max_len = 0.4, 0.8 + 0.4 * difficulty  # meters
    
    def add_platform(start_x, platform_length, platform_width, height):
        half_width = platform_width // 2
        height_field[start_x:(start_x + platform_length), (mid_y - half_width):(mid_y + half_width)] = height

    def add_ramp(start_x, ramp_length, platform_width, height_start, height_end):
        half_width = platform_width // 2
        height_field[start_x:(start_x + ramp_length), (mid_y - half_width):(mid_y + half_width)] = np.linspace(height_start, height_end, ramp_length).reshape(-1, 1)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # First goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]
    
    # Initialize current x
    cur_x = spawn_length
    for i in range(1, 8):
        # Randomize the next platform/beam parameters
        platform_length = np.random.uniform(platform_min_len, platform_max_len)
        platform_length = m_to_idx(platform_length)
        platform_width = np.random.uniform(platform_min_width, platform_max_width)
        platform_width = m_to_idx(platform_width)
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        
        if i % 3 == 0:
            # Every 3rd obstacle is a ramp
            ramp_length = platform_length
            height_start = platform_height
            height_end = np.random.uniform(platform_height_min, platform_height_max)
            add_ramp(cur_x, ramp_length, platform_width, height_start, height_end)
            platform_height = height_end
        else:
            # Add a normal platform
            add_platform(cur_x, platform_length, platform_width, platform_height)

        # Set the goal on this platform
        goals[i] = [cur_x + platform_length // 2, mid_y]

        # Advance cur_x accounting for the length of the current obstacle and a random gap
        gap_length = np.random.uniform(gap_min_len, gap_max_len)
        gap_length = m_to_idx(gap_length)
        cur_x += platform_length + gap_length

    # Add final goal after the last platform
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    
    return height_field, goals

def set_terrain_5(length, width, field_resolution, difficulty):
    """Staggered elevated steps and bridges for the robot to climb, navigate and balance across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up staggered step and elevated bridge dimensions
    # We make the step height near 0 at minimum difficulty so the quadruped can learn to climb up
    step_length = 0.8 - 0.2 * difficulty
    step_length = m_to_idx(step_length)
    step_width = np.random.uniform(0.4, 0.6)
    step_width = m_to_idx(step_width)
    step_height_min, step_height_max = 0.1 * difficulty, 0.3 * difficulty
    
    bridge_length = 1.0 - 0.3 * difficulty
    bridge_length = m_to_idx(bridge_length)
    bridge_width = np.random.uniform(0.5, 0.8)
    bridge_width = m_to_idx(bridge_width)
    bridge_height_min, bridge_height_max = 0.2 * difficulty, 0.5 * difficulty

    gap_length = 0.2 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_step(start_x, end_x, mid_y, height):
        half_width = step_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_bridge(start_x, end_x, mid_y, height):
        half_width = bridge_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height
    
    dx_min, dx_max = -0.05, 0.05
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.1, 0.1
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn area
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]
    
    cur_x = spawn_length
    for i in range(3):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        step_height = np.random.uniform(step_height_min, step_height_max)
        add_step(cur_x, cur_x + step_length + dx, mid_y + dy, step_height)

        # Put goal in the center of the step
        goals[i+1] = [cur_x + (step_length + dx) / 2, mid_y + dy]

        cur_x += step_length + dx + gap_length

    for i in range(3, 7):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        bridge_height = np.random.uniform(bridge_height_min, bridge_height_max)
        add_bridge(cur_x, cur_x + bridge_length + dx, mid_y + dy, bridge_height)

        # Put goal in the center of the bridge
        goals[i+1] = [cur_x + (bridge_length + dx) / 2, mid_y + dy]

        cur_x += bridge_length + dx + gap_length
    
    # Add final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_6(length, width, field_resolution, difficulty):
    """Combination of narrow beams, varied height platforms, and sloped ramps to test balance, precision, and incline traversal."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_width_min = 0.4 + 0.1 * difficulty
    platform_width_max = 1.5 - 0.2 * difficulty
    platform_length = 1.0 + 0.4 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.6 * difficulty
    gap_length = 0.2 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_obstacle(start_x, end_x, mid_y, obs_width, height):
        half_width = obs_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.5, 0.5
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    for i in range(6):  # Set up 6 obstacles of varying types
        obs_type = random.choice(["beam", "platform", "ramp"])
        obs_width = np.random.uniform(platform_width_min, platform_width_max)
        obs_width = m_to_idx(obs_width)
        obs_height = np.random.uniform(platform_height_min, platform_height_max)
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        if obs_type == "beam":
            add_obstacle(cur_x, cur_x + platform_length + dx, mid_y + dy, obs_width, obs_height)
        elif obs_type == "platform":
            add_obstacle(cur_x, cur_x + platform_length + dx, mid_y + dy, obs_width, obs_height)
        elif obs_type == "ramp":
            half_width = obs_width // 2
            x1, x2 = cur_x, cur_x + platform_length + dx
            y1, y2 = mid_y + dy - half_width, mid_y + dy + half_width
            ramp_height = np.linspace(0, obs_height, y2-y1)[None, :]
            height_field[x1:x2, y1:y2] = ramp_height

        # Place a goal at the center of the obstacle
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Create a gap after the obstacle
        cur_x += platform_length + dx + gap_length

    # Add final goal behind the last obstacle, filling in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_7(length, width, field_resolution, difficulty):
    """Combination of narrow beams, balanced ramps, and varied-height platforms for increased difficulty and feasibility."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up obstacle dimensions
    platform_length = m_to_idx(1.0 - 0.2 * difficulty)
    platform_width = m_to_idx(np.random.uniform(0.9, 1.3))
    platform_height_min, platform_height_max = 0.0 + 0.3 * difficulty, 0.05 + 0.35 * difficulty
    ramp_length = m_to_idx(1.5 - 0.3 * difficulty)
    ramp_width = m_to_idx(0.4 - 0.05 * difficulty)
    ramp_height_min, ramp_height_max = 0.0 + 0.4 * difficulty, 0.05 + 0.45 * difficulty
    beam_width = m_to_idx(0.35 - 0.05 * difficulty)
    gap_length = m_to_idx(0.5 + 0.4 * difficulty)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_ramp(start_x, end_x, mid_y, direction):
        half_width = ramp_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        slant = np.linspace(0, ramp_height, num=end_x - start_x)[::direction]  # Create gradient
        height_field[x1:x2, y1:y2] = slant[:, None]

    def add_beam(start_x, end_x, mid_y):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = np.random.uniform(0.2 * difficulty, 0.5 * difficulty)

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    obstacle_types = [add_platform, add_ramp, add_beam]
    for i in range(7):
        obstacle = obstacle_types[i % 3]
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        if obstacle == add_ramp:
            direction = 1 if i % 4 < 2 else -1  # Alternate ramp directions
            obstacle(cur_x, cur_x + ramp_length + dx, mid_y + dy, direction)
            goals[i + 1] = [cur_x + m_to_idx(0.75) + dx // 2, mid_y + dy]
            cur_x += ramp_length + dx + gap_length
        elif obstacle == add_beam:
            obstacle(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i + 1] = [cur_x + platform_length // 2, mid_y + dy]
            cur_x += platform_length + gap_length
        else:
            obstacle(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i + 1] = [cur_x + platform_length // 2, mid_y + dy]
            cur_x += platform_length + gap_length

    goals[-1] = [cur_x - m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_8(length, width, field_resolution, difficulty):
    """Staggered platforms, narrow bridges, and mild sloped pathways for the quadruped to climb, balance, and navigate"""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions
    platform_length = m_to_idx(1.0 - 0.3 * difficulty)
    platform_height_min, platform_height_max = 0.05 * difficulty, 0.25 * difficulty
    bridge_width = m_to_idx(0.5 - 0.2 * difficulty)
    gap_length = m_to_idx(0.2 + 0.8 * difficulty)
    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, length, mid_y, height):
        half_width = m_to_idx(1.0) // 2
        height_field[start_x:start_x + length, mid_y - half_width:mid_y + half_width] = height

    def add_bridge(start_x, length, mid_y):
        half_width = bridge_width // 2
        height_field[start_x:start_x + length, mid_y - half_width:mid_y + half_width] = 0.5 * platform_height_max * difficulty

    def add_slope(start_x, length, mid_y, height):
        half_width = m_to_idx(1.0) // 2
        slope = np.linspace(0, height, length)
        slope = slope[:, None]  # Add a dimension for broadcasting to y
        height_field[start_x:start_x + length, mid_y - half_width:mid_y + half_width] = slope

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    # Let's mix platforms, slopes, and bridges
    for i in range(1, 7):  # We have 6 more goals to place
        if i % 2 == 1:
            # Add platform every other goal
            height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, platform_length, mid_y, height)
            goals[i] = [cur_x + platform_length // 2, mid_y]
            cur_x += platform_length + gap_length
        else:
            # Add alternating between bridge and slope
            if np.random.rand() > 0.5:
                add_bridge(cur_x, platform_length, mid_y)
            else:
                height = np.random.uniform(platform_height_min, platform_height_max)
                add_slope(cur_x, platform_length, mid_y, height)
            goals[i] = [cur_x + platform_length // 2, mid_y]
            cur_x += platform_length + gap_length

    # Add final goal behind the last obstacle, fill in remaining gap
    goals[-1] = [m_to_idx(11.5), mid_y]
    height_field[m_to_idx(11):, :] = 0

    return height_field, goals

def set_terrain_9(length, width, field_resolution, difficulty):
    """Course with alternating stepping platforms and varying-beam widths for the quadruped to balance on, step up, and navigate across gaps."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up obstacle dimensions
    platform_length = 0.8 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    beam_width_min = 0.4 - 0.1 * difficulty
    beam_width_max = 0.8 - 0.1 * difficulty
    beam_width_min = m_to_idx(beam_width_min)
    beam_width_max = m_to_idx(beam_width_max)
    platform_height_min, platform_height_max = 0.1 + 0.05 * difficulty, 0.25 + 0.15 * difficulty
    gap_length = 0.1 + 0.3 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2
    num_platforms = 4  # Alternating platforms

    def add_platform(start_x, end_x, cur_y):
        half_width = (end_x - start_x) // 2
        x1, x2 = start_x, end_x
        y1, y2 = cur_y - half_width, cur_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    # Alternating platforms for stepping
    for i in range(num_platforms):
        dx = np.random.randint(dx_min, dx_max)
        width = np.random.randint(beam_width_min, beam_width_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y)

        # Set goal in the center of the platform
        goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y]

        # Add gap
        cur_x += platform_length + dx + gap_length

    # Add beams of varied widths between platforms
    for i in range(num_platforms, 7):
        dx = np.random.randint(dx_min, dx_max)
        width = np.random.randint(beam_width_min, beam_width_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y)

        # Set goal in the center of the beam
        goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y]

        # Add gap
        cur_x += platform_length + dx + gap_length

    # Add final goal behind the last obstacle
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

# INSERT TERRAIN FUNCTION DEFINITIONS HERE
