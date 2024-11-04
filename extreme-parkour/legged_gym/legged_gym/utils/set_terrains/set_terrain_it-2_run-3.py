
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
    """Varying-height steps and platforms for the robot to navigate and step over."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Setup platform dimensions
    platform_length_base = 0.8  # Base length of platform
    platform_length_variation = 0.3 * difficulty
    platform_width = np.random.uniform(0.8, 1.2)  # Narrower and slightly varied platform width
    platform_width = m_to_idx(platform_width)
    step_height_min, step_height_max = 0.05 * difficulty, 0.3 * difficulty
    gap_length_base = 0.2
    gap_length_variation = 0.5 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2  # Reduced polarity variation in y direction for a consistent path
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Add platforms and steps
    cur_x = spawn_length
    heights = [0.0]

    for i in range(7):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        platform_length = platform_length_base + (platform_length_variation * np.random.rand())
        platform_length = m_to_idx(platform_length)
        gap_length = gap_length_base + (gap_length_variation * np.random.rand())
        gap_length = m_to_idx(gap_length)

        step_height = np.random.uniform(step_height_min, step_height_max) * (-1 if i % 2 == 0 else 1)
        heights.append(heights[-1] + step_height)

        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, heights[-1])

        # Set goal in the center of the platform
        goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += platform_length + dx + gap_length

    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_1(length, width, field_resolution, difficulty):
    """Combination of narrow beams, platforms, and sloped ramps for advancing navigation skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Parameters for various obstacles
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.5)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.2 * difficulty, 0.10 + 0.25 * difficulty

    beam_length = 1.0
    beam_length = m_to_idx(beam_length)
    beam_width = 0.4
    beam_width = m_to_idx(beam_width)
    beam_height_min, beam_height_max = 0.20, 0.30 + 0.15 * difficulty

    ramp_height_min, ramp_height_max = 0.0 + 0.5 * difficulty, 0.10 + 0.55 * difficulty
    gap_length = 0.2 + 0.8 * difficulty  # Enough gap for jumps
    gap_length = m_to_idx(gap_length)

    def add_obstacle(start_x, end_x, mid_y, width, height, slope=False):
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        if slope:
            slant = np.linspace(0, height, num=x2-x1)[:, None]
            height_field[x1:x2, y1:y2] = slant
        else:
            height_field[x1:x2, y1:y2] = height

    mid_y = m_to_idx(width) // 2

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at spawn

    cur_x = spawn_length
    for i in range(6):  # Combination of 6 different obstacles
        if i % 3 == 0:  # Add platform
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)
            height = np.random.uniform(platform_height_min, platform_height_max)
            add_obstacle(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_width, height)
            goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
            cur_x += platform_length + dx + gap_length

        elif i % 3 == 1:  # Add narrow beam
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)
            height = np.random.uniform(beam_height_min, beam_height_max)
            add_obstacle(cur_x, cur_x + beam_length + dx, mid_y + dy, beam_width, height)
            goals[i + 1] = [cur_x + (beam_length + dx) / 2, mid_y + dy]
            cur_x += beam_length + dx + gap_length

        else:  # Add sloped ramp
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)
            height = np.random.uniform(ramp_height_min, ramp_height_max)
            add_obstacle(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_width, height, slope=True)
            goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
            cur_x += platform_length + dx + gap_length

    # Final goal behind the last obstacle
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_2(length, width, field_resolution, difficulty):
    """Alternating steps and narrow bridges for the robot to navigate carefully and climb across a series of challenging obstacles."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define platform and step dimensions
    platform_length = 1.0 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.5)  
    platform_width = m_to_idx(platform_width)
    step_height_min, step_height_max = 0.1 * difficulty, 0.4 * difficulty
    gap_length = 0.1 + 0.4 * difficulty  
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(step_height_min, step_height_max)
        height_field[x1:x2, y1:y2] = platform_height
    
    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Initialize path with a series of steps and platforms
    cur_x = spawn_length
    step_width = 0.3 - 0.1 * difficulty  # narrower steps if more difficult
    step_width = m_to_idx(step_width)
    for i in range(6):  # Set up 6 alternating steps and platforms
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        if i % 2 == 0:  # Create step
            height = np.random.uniform(step_height_min, step_height_max)
            half_width = platform_width // 2
            x1, x2 = cur_x, cur_x + step_width
            y1, y2 = mid_y - half_width, mid_y + half_width
            height_field[x1:x2, y1:y2] = height
            cur_x += step_width
        else:  # Create platform
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
            cur_x += platform_length + dx

        # Put goal in the center of the step/platform
        goals[i+1] = [cur_x - step_width / 2, mid_y + dy]
        
        # Add gap if necessary
        if i != 5:
            cur_x += gap_length
    
    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_3(length, width, field_resolution, difficulty):
    """Combines stepping stones, narrow beams, and raised platforms for the robot to climb on and jump across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up obstacle dimensions
    step_length = 0.5
    step_length = m_to_idx(step_length)
    step_width = 0.4 + 0.3 * difficulty
    step_width = m_to_idx(step_width)
    step_height_min, step_height_max = 0.1, 0.25 + 0.15 * difficulty
    gap_length = 0.2 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    narrow_beam_length = 1.0 - 0.3 * difficulty
    narrow_beam_length = m_to_idx(narrow_beam_length)
    narrow_beam_width = 0.4
    narrow_beam_width = m_to_idx(narrow_beam_width)
    beam_height = 0.2 + 0.2 * difficulty

    raise_platform_length = 1.0
    raise_platform_length = m_to_idx(raise_platform_length)
    raise_platform_width = np.random.uniform(1.0, 1.6)
    raise_platform_width = m_to_idx(raise_platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.4 * difficulty, 0.05 + 0.6 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_step(start_x, mid_y):
        half_width = step_width // 2
        x1 = start_x
        x2 = start_x + step_length
        y1 = mid_y - half_width
        y2 = mid_y + half_width
        step_height = np.random.uniform(step_height_min, step_height_max)
        height_field[x1:x2, y1:y2] = step_height

    def add_narrow_beam(start_x, end_x, mid_y):
        half_width = narrow_beam_width // 2
        beam_height = 0.2 + 0.2 * difficulty
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = beam_height

    def add_platform(start_x, end_x, mid_y):
        half_width = raise_platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height
  
    dx_min, dx_max = m_to_idx(-0.1), m_to_idx(0.1)
    dy_min, dy_max = m_to_idx(-0.4), m_to_idx(0.4)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    # Step 1: Add stepping stones
    for i in range(3):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_step(cur_x, mid_y + dy)
        goals[i + 1] = [cur_x + step_length / 2, mid_y + dy]
        cur_x += step_length + dx + gap_length

    # Step 2: Add narrow beam
    dx = np.random.randint(dx_min, dx_max)
    dy = np.random.randint(dy_min, dy_max)
    add_narrow_beam(cur_x, cur_x + m_to_idx(narrow_beam_length) + dx, mid_y + dy)
    goals[4] = [cur_x + m_to_idx(narrow_beam_length) / 2, mid_y + dy]
    cur_x += narrow_beam_length + dx + gap_length

    # Step 3: Add raised platforms
    for i in range(3):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + raise_platform_length + dx, mid_y + dy)
        goals[5 + i] = [cur_x + (raise_platform_length + dx) / 2, mid_y + dy]
        cur_x += raise_platform_length + dx + gap_length

    # Add final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_4(length, width, field_resolution, difficulty):
    """A combination of sideways ramps, narrow bridges, and staggered steps to test balance and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Constants sizing and initial variables
    platform_length = m_to_idx(1.0 - 0.2 * difficulty)
    platform_height_min, platform_height_max = 0.05 * difficulty, 0.25 * difficulty
    bridge_width = m_to_idx(0.5 - 0.2 * difficulty)
    gap_length = m_to_idx(0.2 + 0.8 * difficulty)
    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        y1, y2 = mid_y - m_to_idx(1.0) // 2, mid_y + m_to_idx(1.0) // 2
        height_field[start_x:end_x, y1:y2] = height

    def add_ramp(start_x, end_x, mid_y, direction, height):
        y1, y2 = mid_y - m_to_idx(1.0) // 2, mid_y + m_to_idx(1.0) // 2
        ramp_height = np.linspace(0, height, y2 - y1)[::direction]
        ramp_height = ramp_height[None, :]
        height_field[start_x:end_x, y1:y2] = ramp_height

    def add_bridge(start_x, end_x, mid_y, width_idx):
        y1, y2 = mid_y - width_idx // 2, mid_y + width_idx // 2
        height_field[start_x:end_x, y1:y2] = 0.5 * platform_height_max * difficulty

    def add_staggered_steps(start_x, end_x, mid_y):
        y1, y2 = mid_y - m_to_idx(0.7) // 2, mid_y + m_to_idx(0.7) // 2
        step_heights = np.linspace(platform_height_min, platform_height_max, num=end_x-start_x)
        height_field[start_x:end_x, y1:y2] = step_heights[:, None]

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    # Adding first platform
    add_platform(cur_x, cur_x + platform_length, mid_y, platform_height_min)
    goals[1] = [cur_x + platform_length // 2, mid_y]
    cur_x += platform_length + gap_length

    obstacles = [
        {'type': 'ramp', 'direction': -1, 'length': platform_length, 'width': 1.0},
        {'type': 'bridge', 'direction': 1, 'length': gap_length, 'width': 0.5},
        {'type': 'ramp', 'direction': 1, 'length': platform_length, 'width': 1.0},
        {'type': 'steps', 'direction': 0, 'length': platform_length, 'width': 0.7}
    ]

    for i, obs in enumerate(obstacles, 2):
        if obs['type'] == 'ramp':
            add_ramp(cur_x, cur_x + obs['length'], mid_y, obs['direction'], platform_height_max)
        elif obs['type'] == 'bridge':
            add_bridge(cur_x, cur_x + obs['length'], mid_y, bridge_width)
        elif obs['type'] == 'steps':
            add_staggered_steps(cur_x, cur_x + obs['length'], mid_y)

        goals[i] = [cur_x + obs['length'] // 2, mid_y]
        cur_x += obs['length'] + gap_length

    # Add final goal at the end
    goals[-1] = [m_to_idx(11.5), mid_y]
    height_field[m_to_idx(11):, :] = 0

    return height_field, goals

def set_terrain_5(length, width, field_resolution, difficulty):
    """Staggered narrow beams with changing heights to test balance and precise movement."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Beam dimensions
    beam_length = 0.9 + 0.1 * difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = 0.4 + 0.04 * difficulty
    beam_width = m_to_idx(beam_width)
    min_height = 0.1 * difficulty
    max_height = 0.5 * difficulty
    beam_gap = 0.1 * difficulty
    beam_gap = m_to_idx(beam_gap)
    
    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, y, height):
        x1, x2 = start_x, end_x
        y1, y2 = y - beam_width // 2, y + beam_width // 2
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = -0.1, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(6):  # Place 6 beams
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        height = np.random.uniform(min_height, max_height)
        add_beam(cur_x, cur_x + beam_length + dx, mid_y + dy, height)

        # Place goal in the center of the beam
        goals[i+1] = [cur_x + (beam_length + dx) / 2, mid_y + dy]

        # Add gap after beam
        cur_x += beam_length + dx + beam_gap
    
    # Place the final goal at the end
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_6(length, width, field_resolution, difficulty):
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

def set_terrain_7(length, width, field_resolution, difficulty):
    """Obstacle course with platforms, short ramps, and mild gaps for the robot to balance, climb, and jump across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and ramp dimensions
    platform_length = 1.0
    platform_length = m_to_idx(platform_length)
    platform_width = m_to_idx(np.random.uniform(0.9, 1.2))
    platform_height_min, platform_height_max = 0.0 + 0.1 * difficulty, 0.2 + 0.2 * difficulty
    gap_length = m_to_idx(0.1 + 0.1 * difficulty)

    ramp_length = platform_length // 2
    ramp_height_min, ramp_height_max = 0.2, 0.3 + 0.2 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

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

    for i in range(6):  # Creating a mix of platforms and ramps
        if i % 2 == 0:
            add_platform(cur_x, cur_x + platform_length, mid_y)
            goals[i + 1] = [cur_x + platform_length // 2, mid_y]
            cur_x += platform_length + gap_length

        else:
            ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
            add_ramp(cur_x, cur_x + ramp_length, mid_y, ramp_height)
            goals[i + 1] = [cur_x + ramp_length // 2, mid_y]
            cur_x += ramp_length + gap_length

    # Add final goal behind the last element and fill rest with flat terrain
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0.0

    return height_field, goals

def set_terrain_8(length, width, field_resolution, difficulty):
    """Complex course with narrow beams, sideways-facing ramps, and platforms for balance, climbing, and navigation."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Course parameters
    beam_width = m_to_idx(0.4 - 0.2 * difficulty)
    platform_length = m_to_idx(1.0)
    gap_length = m_to_idx(0.5 + 0.3 * difficulty)
    ramp_length = m_to_idx(1.5 - 0.5 * difficulty)

    mid_y = m_to_idx(width / 2)

    def add_beam(start_x, end_x, mid_y):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = np.random.uniform(0.1 * difficulty, 0.4 * difficulty)

    def add_ramp(start_x, end_x, mid_y, direction):
        half_width = m_to_idx(0.5)
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(0.2, 0.6) * difficulty
        slant = np.linspace(0, ramp_height, num=end_x - start_x)[::direction]  # Create gradient
        height_field[x1:x2, y1:y2] = slant[:, None]

    def add_platform(start_x, end_x, mid_y):
        half_width = m_to_idx(0.6)
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
    obstacle_types = [add_beam, add_ramp, add_platform]
    for i in range(7):
        obstacle = obstacle_types[i % 3]
        dx = np.random.randint(dx_min, dx_max)
        dy = (i % 2) * np.random.randint(dy_min, dy_max)  # Alternating y-offset roughly

        if obstacle == add_ramp:
            direction = 1 if i % 4 < 2 else -1  # Alternate ramp directions
            obstacle(cur_x, cur_x + ramp_length + dx, mid_y + dy, direction)
            goals[i+1] = [cur_x + m_to_idx(0.75) + dx // 2, mid_y + dy]
            cur_x += ramp_length + dx + gap_length
        else:
            obstacle(cur_x, cur_x + platform_length, mid_y + dy)
            goals[i+1] = [cur_x + platform_length // 2, mid_y + dy]
            cur_x += platform_length + gap_length

    goals[-1] = [cur_x - m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_9(length, width, field_resolution, difficulty):
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

# INSERT TERRAIN FUNCTION DEFINITIONS HERE
