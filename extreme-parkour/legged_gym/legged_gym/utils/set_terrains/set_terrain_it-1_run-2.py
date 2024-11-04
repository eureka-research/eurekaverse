
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
    """Mixed challenges with higher platforms, narrow beams, and varied gap jumps."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define properties of platforms and beams
    platform_length = 0.7 + 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 0.5 + 0.2 * difficulty
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.2 * difficulty, 0.5 + 0.3 * difficulty
    beam_length = 0.6 + 0.2 * difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = 0.2 + 0.1 * difficulty
    beam_width = m_to_idx(beam_width)
    gap_length_min, gap_length_max = 0.2 + 0.3 * difficulty, 0.5 + 0.5 * difficulty
    gap_length_min, gap_length_max = m_to_idx(gap_length_min), m_to_idx(gap_length_max)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, start_y, end_x, end_y):
        """Adds a platform to the terrain."""
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[start_x:end_x, start_y:end_y] = platform_height

    def add_beam(start_x, start_y, end_x, end_y, height):
        """Adds a narrow beam to the terrain."""
        height_field[start_x:end_x, start_y:end_y] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x, cur_y = spawn_length, mid_y - platform_width // 2

    # Create series of platforms and beams with varied gaps
    for i in range(1, 8):
        if i % 2 == 1:  # Add platform
            dx = np.random.randint(0, m_to_idx(0.2))
            dy = np.random.randint(-m_to_idx(0.4), m_to_idx(0.4))
            add_platform(cur_x + dx, cur_y + dy, cur_x + platform_length + dx, cur_y + platform_width + dy)
            goals[i] = [cur_x + platform_length // 2 + dx, cur_y + platform_width // 2 + dy]
            cur_x += platform_length + dx + np.random.randint(gap_length_min, gap_length_max)
        else:  # Add narrow beam
            height = np.random.uniform(0.1, 0.2)
            dx = np.random.randint(0, m_to_idx(0.2))
            dy = np.random.randint(-m_to_idx(0.2), m_to_idx(0.2))
            add_beam(cur_x + dx, cur_y + dy, cur_x + beam_length + dx, cur_y + beam_width + dy, height)
            goals[i] = [cur_x + beam_length // 2 + dx, cur_y + beam_width // 2 + dy]
            cur_x += beam_length + dx + np.random.randint(gap_length_min, gap_length_max)
            
    # Final goal after the last obstacle
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_1(length, width, field_resolution, difficulty):
    """Narrow bridges and elevated platforms to test balance and navigation at varying heights."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform and bridge sizes
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.2)
    platform_width = m_to_idx(platform_width)
    bridge_length_min, bridge_length_max = 2.0 - 0.8 * difficulty, 2.5 - 0.8 * difficulty
    bridge_length_min = m_to_idx(bridge_length_min)
    bridge_length_max = m_to_idx(bridge_length_max)
    bridge_width_min, bridge_width_max = 0.5, 0.6
    bridge_width_min = m_to_idx(bridge_width_min)
    bridge_width_max = m_to_idx(bridge_width_max)
    gap_length = 0.1 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)

    platform_height_min, platform_height_max = 0.2, 0.5 + 0.3 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_platform(center_x, center_y):
        half_length = platform_length // 2
        half_width = platform_width // 2
        x1, x2 = center_x - half_length, center_x + half_length
        y1, y2 = center_y - half_width, center_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height
    
    def add_bridge(start_x, end_x, center_y):
        half_width = random.randint(bridge_width_min, bridge_width_max) // 2
        x1, x2 = start_x, end_x
        y1, y2 = center_y - half_width, center_y + half_width
        bridge_height = random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = bridge_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    for i in range(6):  # Create 6 platforms and bridges
        # Add platform
        add_platform(cur_x + platform_length // 2, mid_y)
        goals[i] = [cur_x + platform_length // 2, mid_y]

        # Move x-coordinate ahead to place bridge
        cur_x += platform_length

        # Add a gap
        cur_x += gap_length

        # Add bridge
        bridge_length = random.randint(bridge_length_min, bridge_length_max)
        add_bridge(cur_x, cur_x + bridge_length, mid_y)
        
        # Move x-coordinate ahead to place next platform
        cur_x += bridge_length

        # Add another gap
        cur_x += gap_length
    
    # Add final platform
    add_platform(cur_x + platform_length // 2, mid_y)
    goals[6] = [cur_x + platform_length // 2, mid_y]

    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + platform_length + m_to_idx(0.5), mid_y]
    height_field[cur_x + platform_length:, :] = 0

    return height_field, goals

def set_terrain_2(length, width, field_resolution, difficulty):
    """Obstacle course featuring staggered stepping stones and varying elevation platforms to test agility and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    stepping_stone_length = 0.6 - 0.2 * difficulty
    stepping_stone_length = m_to_idx(stepping_stone_length)
    stepping_stone_width = np.random.uniform(0.4, 0.6)
    stepping_stone_width = m_to_idx(stepping_stone_width)
    stepping_stone_height_min, stepping_stone_height_max = 0.15 * difficulty, 0.35 * difficulty
    small_gap_length = 0.05 + 0.25 * difficulty
    small_gap_length = m_to_idx(small_gap_length)

    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.1)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.4 * difficulty, 0.1 + 0.5 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_stepping_stone(start_x, end_x, y_start, y_end, height):
        """Add a stepping stone to the height_field."""
        height_field[start_x:end_x, y_start:y_end] = height
        
    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.1, 0.1
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length

    for i in range(3):  # Set up 3 stepping stones
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        stone_height = np.random.uniform(stepping_stone_height_min, stepping_stone_height_max)
        
        # Ensure that stones remain within bounds
        y_center = mid_y + dy
        y_start = max(1, y_center - stepping_stone_width // 2, m_to_idx(1))
        y_end = min(m_to_idx(width) - 1, y_center + stepping_stone_width // 2, m_to_idx(width - 1))
        
        add_stepping_stone(cur_x, cur_x + stepping_stone_length + dx, y_start, y_end, stone_height)

        # Put goal in the center of the current stone
        goals[i+1] = [cur_x + (stepping_stone_length + dx) / 2, y_center]

        # Creating gaps
        cur_x += stepping_stone_length + dx + small_gap_length

    for i in range(4, 8):  # Adding 4 platforms
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)

        # Put goal in the center of the platform
        goals[i] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += platform_length + dx + small_gap_length
    
    # Add final goal near the end of the course
    goals[-1] = [cur_x + m_to_idx(1), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_3(length, width, field_resolution, difficulty):
    """Series of staggered narrow beams with height variations for the quadruped to balance and navigate through."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    # Initialize height field and goals
    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Beam dimensions and setup
    beam_width = 0.2 + 0.1 * difficulty
    beam_width = m_to_idx(beam_width)
    beam_length = 1.0 + 0.2 * difficulty
    beam_length = m_to_idx(beam_length)
    beam_height_min, beam_height_max = 0.1 + 0.1 * difficulty, 0.2 + 0.4 * difficulty
    gap_length = 0.4 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, center_y, height):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = center_y - half_width, center_y + half_width
        height_field[x1:x2, y1:y2] = height

    # Flatten the spawn area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(6):  # Create a sequence of beams with gaps
        dx = np.random.randint(-m_to_idx(0.1), m_to_idx(0.1))
        dy = np.random.randint(-m_to_idx(0.3), m_to_idx(0.3))
        beam_height = np.random.uniform(beam_height_min, beam_height_max)
        add_beam(cur_x, cur_x + beam_length + dx, mid_y + dy, beam_height)

        # Place goal in the middle of each beam
        goals[i + 1] = [cur_x + (beam_length + dx) / 2, mid_y + dy]

        # Increment current x by the length of the beam and the gap
        cur_x += beam_length + dx + gap_length

    # Place the final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_4(length, width, field_resolution, difficulty):
    """Obstacle course with varied platforms and thin beams for balance and navigation challenges."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if isinstance(m, (int, float)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Dimensions and height ranges of platforms and beams
    basic_height_min, basic_height_max = 0.1 + 0.2 * difficulty, 0.3 + 0.4 * difficulty
    beam_width = np.random.uniform(0.4, 0.5)  # Narrower beams for greater difficulty
    beam_width = m_to_idx(beam_width)
    platform_length = 0.8 + 0.4 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width_range = [1.0, 1.4]
    gap_length_range = [0.2, 0.7]
    
    mid_y = m_to_idx(width) // 2

    def add_platform(x_start, length, height, mid_y):
        """Creates a rectangular platform at provided location."""
        width = np.random.uniform(*platform_width_range)
        width = m_to_idx(width)
        x_end = x_start + length
        half_width = width // 2
        height_field[x_start:x_end, mid_y - half_width:mid_y + half_width] = height

    def add_beam(x_start, length, height, mid_y, shift=0):
        """Creates a thin beam for balance challenge."""
        x_end = x_start + length
        y_start = mid_y - beam_width // 2 + shift
        y_end = mid_y + beam_width // 2 + shift
        height_field[x_start:x_end, y_start:y_end] = height

    # Set flat ground for spawning area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(1), mid_y]

    cur_x = spawn_length
    cur_y_shift = 0

    for i in range(7):
        platform_height = np.random.uniform(basic_height_min, basic_height_max)
        gap_length = np.random.uniform(*gap_length_range)
        gap_length = m_to_idx(gap_length)

        if i % 2 == 0:  # Even indices -> platform
            add_platform(cur_x, platform_length, platform_height, mid_y + cur_y_shift)
            goals[i+1] = [cur_x + platform_length / 2, mid_y + cur_y_shift]
            cur_x += platform_length + gap_length
        else:  # Odd indices -> beam
            add_beam(cur_x, platform_length, platform_height, mid_y, shift=cur_y_shift)
            goals[i+1] = [cur_x + platform_length / 2, mid_y + cur_y_shift]
            cur_x += platform_length + gap_length
        
        # Alternate y-shift to promote diverse navigation
        cur_y_shift = (-1) ** i * np.random.randint(0, m_to_idx(0.4))
    
    goals[-1] = [cur_x + m_to_idx(1), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_5(length, width, field_resolution, difficulty):
    """Elevated platforms with narrow beams and gaps to test dexterity and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up obstacle dimensions
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)

    platform_width = np.random.uniform(0.8, 1.0)  # Narrower platforms
    platform_width = m_to_idx(platform_width)

    platform_height_min, platform_height_max = 0.2 + 0.3 * difficulty, 0.5 + 0.3 * difficulty
    gap_length = 0.5 + 0.7 * difficulty
    gap_length = m_to_idx(gap_length)

    beam_width = 0.2 + 0.2 * difficulty  # Narrow beams with increasing difficulty
    beam_width = m_to_idx(beam_width)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, start_y, end_y, height):
        height_field[start_x:end_x, start_y:end_y] = height

    cur_x = m_to_idx(2)
    height_field[0:cur_x, :] = 0  # Set spawn area to flat ground
    n_obstacles = 6

    # Initial goal at spawn area
    goals[0] = [cur_x - m_to_idx(0.5), mid_y]

    for i in range(n_obstacles):
        height = np.random.uniform(platform_height_min, platform_height_max)

        if i % 2 == 0:  # Add platforms
            end_x = cur_x + platform_length
            add_platform(cur_x, end_x, mid_y - platform_width // 2, mid_y + platform_width // 2, height)
            goals[i + 1] = [cur_x + platform_length // 2, mid_y]
            cur_x = end_x + gap_length

        else:  # Add narrow beams
            end_x = cur_x + platform_length
            add_platform(cur_x, end_x, mid_y - beam_width // 2, mid_y + beam_width // 2, height)
            goals[i + 1] = [cur_x + platform_length // 2, mid_y]
            cur_x = end_x + gap_length

    # Final goal position
    goals[-1] = [cur_x + m_to_idx(1), mid_y]

    return height_field, goals


def set_terrain_6(length, width, field_resolution, difficulty):
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

def set_terrain_7(length, width, field_resolution, difficulty):
    """Irregular stepping stones and varied-height platforms with small gaps for balance and jumping."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and stepping stone dimensions
    stone_length = 0.75 - 0.15 * difficulty
    stone_length = m_to_idx(stone_length)
    stone_width = 0.35  # Narrower for balance, maintaining as feasible
    stone_width = m_to_idx(stone_width)
    stone_height_min, stone_height_max = 0.05 + 0.30 * difficulty, 0.10 + 0.4 * difficulty
    gap_length = 0.1 + 0.4 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_stepping_stone(start_x, mid_y, stone_height):
        half_width = stone_width // 2
        end_x = start_x + stone_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[start_x:end_x, y1:y2] = stone_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0    
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at spawn

    # Begin sequence of uneven stepping stones
    cur_x = spawn_length    
    for i in range(6):  # Set up 6 stepping stones
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        stone_height = np.random.uniform(stone_height_min, stone_height_max)
        add_stepping_stone(cur_x, mid_y + dy, stone_height)
        
        # Add goal at center of the stone
        goals[i+1] = [cur_x + stone_length / 2 + dx, mid_y + dy]
        
        # Add gap between stones
        cur_x += stone_length + gap_length + dx

    # Add final goal and ensure flat ground at the end
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_8(length, width, field_resolution, difficulty):
    """Series of steps and gentle slopes for the robot to climb and traverse."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define dimensions and heights for steps and slopes
    step_length = 0.6 + 0.2 * difficulty
    step_length = m_to_idx(step_length)
    step_width = 0.6 + 0.1 * difficulty
    step_width = m_to_idx(step_width)
    step_height_min, step_height_max = 0.1, 0.2 + 0.2 * difficulty
    slope_height_min = 0.05
    slope_height_max = 0.15 + 0.1 * difficulty
    
    gap_length = 0.2 + 0.3 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_step(start_x, end_x, mid_y, height):
        half_width = step_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height
    
    def add_slope(start_x, end_x, mid_y, height_change):
        half_width = step_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slope = np.linspace(0, height_change, num=x2-x1)
        slope = slope[:, None]  # Add a dimension for broadcasting to y
        height_field[x1:x2, y1:y2] += slope

    dx_min, dx_max = -0.1, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length + gap_length
    next_goal_idx = 1

    for i in range(4):  # Set up 4 steps
        step_height = np.random.uniform(step_height_min, step_height_max)
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        add_step(cur_x, cur_x + step_length + dx, mid_y + dy, step_height)

        # Put goal in the center of the step
        goals[next_goal_idx] = [cur_x + (step_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += step_length + dx + gap_length
        next_goal_idx += 1

    for i in range(3):  # Set up 3 slopes
        slope_height_change = np.random.uniform(slope_height_min, slope_height_max)
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        add_slope(cur_x, cur_x + step_length + dx, mid_y + dy, slope_height_change)

        # Put goal in the center of the slope
        goals[next_goal_idx] = [cur_x + (step_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += step_length + dx + gap_length
        next_goal_idx += 1

    # Add final goal on flat ground
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_9(length, width, field_resolution, difficulty):
    """Challenging terrain with alternating narrow beams, platforms, and tilted ramps to enhance balance and jumping skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        if isinstance(m, (list, tuple)):
            return [round(i / field_resolution) for i in m]
        return np.round(m / field_resolution).astype(np.int16)

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Adjust parameters based on difficulty
    platform_length = 1.6 - 0.5 * difficulty
    platform_length_idx = m_to_idx(platform_length)
    platform_width_min, platform_width_max = 0.9, 1.2
    platform_width_idx = m_to_idx(np.random.uniform(platform_width_min, platform_width_max))
    
    beam_width = 0.4  # Fixed narrow beam width
    beam_length = 1.0 + 1.0 * difficulty
    beam_length_idx = m_to_idx(beam_length)
    beam_width_idx = m_to_idx(beam_width)
    
    ramp_height_min, ramp_height_max = 0.3 * difficulty, 0.6 * difficulty
    gap_length = 0.4 + 0.6 * difficulty
    gap_length_idx = m_to_idx(gap_length)

    mid_y = m_to_idx(width / 2)

    def add_narrow_beam(start_x, mid_y):
        """Adds a narrow beam obstacle."""
        half_width_idx = beam_width_idx // 2
        x1, x2 = start_x, start_x + beam_length_idx
        y1, y2 = mid_y - half_width_idx, mid_y + half_width_idx
        beam_height = np.random.uniform(ramp_height_min, ramp_height_max)
        height_field[x1:x2, y1:y2] = beam_height
        return (x1 + x2) // 2, mid_y

    def add_platform(start_x, mid_y):
        """Adds a platform obstacle."""
        half_width_idx = platform_width_idx // 2
        x1, x2 = start_x, start_x + platform_length_idx
        y1, y2 = mid_y - half_width_idx, mid_y + half_width_idx
        platform_height = np.random.uniform(ramp_height_min, ramp_height_max)
        height_field[x1:x2, y1:y2] = platform_height
        return (x1 + x2) // 2, mid_y

    def add_ramp(start_x, mid_y, direction):
        """Adds a tilted ramp obstacle."""
        half_width_idx = platform_width_idx // 2
        x1, x2 = start_x, start_x + platform_length_idx
        y1, y2 = mid_y - half_width_idx, mid_y + half_width_idx
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        slant = np.linspace(0, ramp_height, num=y2-y1)[::direction]
        slant = slant[None, :]  # Add a dimension for broadcasting to x
        height_field[x1:x2, y1:y2] = slant
        return (x1 + x2) // 2, mid_y

    # Set spawn area to flat ground
    spawn_length_idx = m_to_idx(2)
    height_field[:spawn_length_idx, :] = 0
    goals[0] = [spawn_length_idx - m_to_idx(0.5), mid_y]

    # Initiate current x and step length
    cur_x = spawn_length_idx
  
    for i in range(6):  # Set up 6 challenging obstacles
        dx = np.random.randint(-m_to_idx(0.1), m_to_idx(0.1))
        if i % 3 == 0:
            # Add narrow beams
            cx, cy = add_narrow_beam(cur_x, mid_y)
        elif i % 3 == 1:
            # Add platforms
            cx, cy = add_platform(cur_x, mid_y)
        else:
            # Add tilted ramps
            dy = np.random.randint(-m_to_idx(0.2), m_to_idx(0.2))
            direction = (-1) ** i  # Alternate left and right ramps
            cx, cy = add_ramp(cur_x, mid_y + dy, direction)
            
        goals[i + 1] = [cx, cy]
        
        # Move to the next position accounting for obstacle length and gap
        if i % 3 == 2:
            cur_x = cx + gap_length_idx  # Increase gap after ramp
      
    # Add final goal after last obstacle
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

# INSERT TERRAIN FUNCTION DEFINITIONS HERE
