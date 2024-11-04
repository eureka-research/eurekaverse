
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
        set_terrain_10,
        set_terrain_11,
        set_terrain_12,
        set_terrain_13,
        set_terrain_14,
        set_terrain_15,
        set_terrain_16,
        set_terrain_17,
        set_terrain_18,
        set_terrain_19,
        set_terrain_20,
        set_terrain_21,
        set_terrain_22,
        set_terrain_23,
        set_terrain_24,
        set_terrain_25,
        set_terrain_26,
        set_terrain_27,
        set_terrain_28,
        set_terrain_29,
        set_terrain_30,
        set_terrain_31,
        set_terrain_32,
        set_terrain_33,
        set_terrain_34,
        set_terrain_35,
        set_terrain_36,
        set_terrain_37,
        set_terrain_38,
        set_terrain_39,
        # INSERT TERRAIN FUNCTIONS HERE
    ]
    idx = int(variation * len(terrain_fns))
    height_field, goals = terrain_fns[idx](terrain.width * terrain.horizontal_scale, terrain.length * terrain.horizontal_scale, terrain.horizontal_scale, difficulty)
    terrain.height_field_raw = (height_field / terrain.vertical_scale).astype(np.int16)
    terrain.goals = goals
    return idx

def set_terrain_0(length, width, field_resolution, difficulty):
    """Staggered steps of varying heights for the robot to climb and traverse."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set the dimensions of the staggered steps
    step_length_base = 1.0  # Base length of each step in meters
    step_width_base = 1.2   # Base width of each step in meters
    
    step_length_variation = 0.3 * difficulty  # The more difficult, the more variation in length
    step_height_min, step_height_max = 0.15 * difficulty, 0.3 * difficulty

    step_length = m_to_idx(step_length_base - step_length_variation)
    step_width = m_to_idx(step_width_base)
    mid_y = m_to_idx(width) // 2

    def add_step(start_x, end_x, height, mid_y):
        half_width = step_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = -0.5, 0.5
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    for i in range(6):  # Set up 6 steps
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        step_height = np.random.uniform(step_height_min, step_height_max)
        add_step(cur_x, cur_x + step_length + dx, step_height, mid_y + dy)

        # Put goal in the center of the step
        goals[i+1] = [cur_x + (step_length + dx) / 2, mid_y + dy]

        # Prepare for the next step
        cur_x += step_length + dx
    
    # Add final goal behind the last step, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_1(length, width, field_resolution, difficulty):
    """Multiple elevated platforms and sideways ramps for the robot to climb, descend and jump across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and ramp dimensions
    platform_length_min = 0.8
    platform_length_max = 1.5
    platform_height_min = 0.1 + 0.2 * difficulty
    platform_height_max = 0.3 + 0.4 * difficulty
    ramp_length = 1.0
    ramp_height = 0.15 + 0.35 * difficulty

    platform_length_min = m_to_idx(platform_length_min)
    platform_length_max = m_to_idx(platform_length_max)
    ramp_length = m_to_idx(ramp_length)
    
    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = m_to_idx(1.2) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_ramp(start_x, end_x, mid_y):
        half_width = m_to_idx(1.0) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_slope = np.linspace(0, ramp_height, num=x2-x1)
        height_field[x1:x2, y1:y2] = ramp_slope[:, None]

    dx_min, dx_max = m_to_idx([-0.1, 0.2])
    dy_min, dy_max = m_to_idx([-0.4, 0.4])
    gap_min, gap_max = m_to_idx([0.2, 0.7])
    
    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    for i in range(3):
        dx, dy = np.random.randint(dx_min, dx_max), np.random.randint(dy_min, dy_max)
        gap = np.random.randint(gap_min, gap_max)

        # Add an elevated platform
        platform_length = np.random.randint(platform_length_min, platform_length_max)
        add_platform(cur_x, cur_x + platform_length, mid_y + dy)
        goals[i + 1] = [(cur_x + platform_length) / 2, mid_y + dy]  # Center of the platform
        cur_x += platform_length + gap

        # Add a sideways ramp
        dx, dy = np.random.randint(dx_min, dx_max), np.random.randint(dy_min, dy_max)
        add_ramp(cur_x, cur_x + ramp_length, mid_y + dy)
        goals[i + 4] = [cur_x + (ramp_length // 2), mid_y + dy]  # Center of the ramp
        cur_x += ramp_length + gap

    # Add a final goal behind the last ramp, filling in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_2(length, width, field_resolution, difficulty):
    """Ramps, narrow passages, and elevated platforms to simulate urban challenges."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    mid_y = m_to_idx(width) // 2

    # Set first goal at the spawn point
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Define ramp and passage parameters
    ramp_length = max(1.0, 1.5 - 0.5 * difficulty)  # Decrease ramp length with difficulty
    ramp_length = m_to_idx(ramp_length)
    ramp_height = np.linspace(0, 0.25 + 0.35 * difficulty, ramp_length)  # Incline increases with difficulty
    
    narrow_passage_width = np.random.uniform(0.4, 0.5) + difficulty * 0.3  # Make narrower with higher difficulty
    narrow_passage_width = m_to_idx(narrow_passage_width)

    # Platform parameters
    platform_height = 0.2 + 0.2 * difficulty
    platform_length = m_to_idx(1.0)
    platform_width = m_to_idx(1.0)

    def add_ramp(start_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, start_x + ramp_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = ramp_height[:, np.newaxis]

    def add_passage(start_x, mid_y):
        half_width = narrow_passage_width // 2
        x1, x2 = start_x, start_x + platform_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height_field[x1 - 1, y1]  # Continue from the previous height

    def add_platform(start_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, start_x + platform_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = platform_height

    # Initialize current x position just after spawn area
    cur_x = spawn_length

    # Add ramp
    add_ramp(cur_x, mid_y)
    goals[1] = [cur_x + ramp_length // 2, mid_y]  # Middle of the first ramp
    cur_x += ramp_length
    
    # Add passage
    add_passage(cur_x, mid_y)
    goals[2] = [cur_x + platform_length // 2, mid_y]  # Middle of the narrow passage
    cur_x += platform_length

    # Add platform
    add_platform(cur_x, mid_y)
    goals[3] = [cur_x + platform_length // 2, mid_y]  # Middle of the platform
    cur_x += platform_length

    for i in range(4, 8):
        if i % 2 == 0:
            # Alternate between ramp and platform
            add_ramp(cur_x, mid_y)
            goals[i] = [cur_x + ramp_length // 2, mid_y]
            cur_x += ramp_length
        else:
            add_platform(cur_x, mid_y)
            goals[i] = [cur_x + platform_length // 2, mid_y]
            cur_x += platform_length

    return height_field, goals

def set_terrain_3(length, width, field_resolution, difficulty):
    """Alternating high and low platforms with variable gaps to challenge climbing and jumping skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    
    platform_length = 0.8 - 0.2 * difficulty  # Shorter to increase frequency of platforms
    platform_length = m_to_idx(platform_length)
    platform_width_min, platform_width_max = 0.8, 1.2
    gap_length_min, gap_length_max = 0.5 + 0.3 * difficulty, 1.0 + 0.6 * difficulty
    gap_length_min, gap_length_max = m_to_idx(gap_length_min), m_to_idx(gap_length_max)
    platform_height_min, platform_height_max = 0.2, 0.3 + 0.2 * difficulty  # Higher platforms

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        width = np.random.uniform(platform_width_min, platform_width_max)
        width = m_to_idx(width)
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length // 2, mid_y]
    
    cur_x = spawn_length
    platform_heights = [np.random.uniform(platform_height_min, platform_height_max) if i % 2 == 0 else 0 for i in range(8)]

    for i in range(7):  # Set up different types of platforms
        gap_length = np.random.randint(gap_length_min, gap_length_max)
        platform_end = cur_x + platform_length
        add_platform(cur_x, platform_end, mid_y, platform_heights[i])
        goals[i + 1] = [cur_x + platform_length // 2, mid_y]
        cur_x = platform_end + gap_length

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_4(length, width, field_resolution, difficulty):
    """Series of staggered stairs for the quadruped to climb up and down."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Convert terrain dimensions to grid indices
    terrain_length = m_to_idx(length)
    terrain_width = m_to_idx(width)

    # Quadruped's center starting point
    start_x = m_to_idx(2)
    start_y = terrain_width // 2
    
    # Initial goal at start position
    goals[0] = [start_x - m_to_idx(0.5), start_y]

    # Define stair dimensions based on difficulty
    stair_width = 1.0 - 0.3 * difficulty  # decrease with difficulty
    stair_width = m_to_idx(stair_width)

    stair_height_min = 0.1 * difficulty  # increase with difficulty
    stair_height_max = 0.3 * difficulty  # increase with difficulty
    stair_length = 1.2  # fixed length of 1.2 meters
    stair_length = m_to_idx(stair_length)
    
    cur_x = start_x

    def add_stair(x, y, width, length, height):
        """Add a stair with given dimensions to the height_field."""
        half_width = width // 2
        x1, x2 = x, x + length
        y1, y2 = y - half_width, y + half_width
        height_field[x1:x2, y1:y2] += height

    for i in range(7):  # 7 sets of stairs
        stair_height = np.random.uniform(stair_height_min, stair_height_max)
        add_stair(cur_x, start_y, stair_width, stair_length, stair_height)

        # Place the goal in the center of the stair
        goals[i + 1] = [cur_x + stair_length // 2, start_y]

        # Move to the next stair position
        cur_x += stair_length

        # Adding a small gap with random width between stairs for added difficulty
        gap = np.random.uniform(0.1, 0.4) * difficulty
        gap = m_to_idx(gap)
        cur_x += gap

    # Final goal at the end of the terrain
    goals[-1] = [cur_x + m_to_idx(0.5), start_y]

    return height_field, goals

def set_terrain_5(length, width, field_resolution, difficulty):
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

def set_terrain_6(length, width, field_resolution, difficulty):
    """A complex course of platforms, ramps, and narrow beams for the quadruped to navigate and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]
    
    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    def add_platform(x_start, x_end, y_mid, height_min, height_max):
        y_half_width = m_to_idx(0.5)  # 1 meter wide platform
        platform_height = np.random.uniform(height_min, height_max)
        height_field[x_start:x_end, y_mid-y_half_width:y_mid+y_half_width] = platform_height

    def add_ramp(x_start, x_end, y_mid, height_min, height_max, slope_up):
        y_half_width = m_to_idx(0.5)  # 1 meter wide ramp
        ramp_height = np.random.uniform(height_min, height_max)
        slope = np.linspace(0, ramp_height, x_end-x_start) * (1 if slope_up else -1)
        slope = slope[:, None]
        height_field[x_start:x_end, y_mid-y_half_width:y_mid+y_half_width] = slope

    def add_beam(x_start, x_end, y_mid, beam_height):
        y_half_width = m_to_idx(0.2)  # 0.4 meter wide beam
        height_field[x_start:x_end, y_mid-y_half_width:y_mid+y_half_width] = beam_height

    def define_goal(x, y, index):
        goals[index] = [x, y]

    spawn_length = m_to_idx(2)
    mid_y = m_to_idx(width) // 2

    height_field[0:spawn_length, :] = 0  # Flat spawn area
    define_goal(spawn_length - m_to_idx(0.5), mid_y, 0)

    x_cursor = spawn_length
    height_min, height_max = 0.2 * difficulty, 0.5 * difficulty
    gap_min, gap_max = m_to_idx(0.2), m_to_idx(difficulty + 0.5)

    # First Platform
    platform_length = m_to_idx(1.5 + 0.3 * difficulty)
    add_platform(x_cursor, x_cursor + platform_length, mid_y, height_min, height_max)
    define_goal(x_cursor + platform_length // 2, mid_y, 1)
    x_cursor += platform_length + np.random.randint(gap_min, gap_max)
    
    # Second Beam
    beam_length = m_to_idx(1 + 0.5 * difficulty)
    add_beam(x_cursor, x_cursor + beam_length, mid_y, np.random.uniform(height_min, height_max))
    define_goal(x_cursor + beam_length // 2, mid_y, 2)
    x_cursor += beam_length + np.random.randint(gap_min, gap_max)
    
    # Third Ramp (up)
    ramp_length = m_to_idx(1.5 + 0.4 * difficulty)
    add_ramp(x_cursor, x_cursor + ramp_length, mid_y, height_min, height_max, slope_up=True)
    define_goal(x_cursor + ramp_length // 2, mid_y, 3)
    x_cursor += ramp_length + np.random.randint(gap_min, gap_max)

    # Fourth Platform
    add_platform(x_cursor, x_cursor + platform_length, mid_y, height_min, height_max)
    define_goal(x_cursor + platform_length // 2, mid_y, 4)
    x_cursor += platform_length + np.random.randint(gap_min, gap_max)
    
    # Fifth Ramp (down)
    add_ramp(x_cursor, x_cursor + ramp_length, mid_y, height_min, height_max, slope_up=False)
    define_goal(x_cursor + ramp_length // 2, mid_y, 5)
    x_cursor += ramp_length + np.random.randint(gap_min, gap_max)
    
    # Sixth Beam
    add_beam(x_cursor, x_cursor + beam_length, mid_y, np.random.uniform(height_min, height_max))
    define_goal(x_cursor + beam_length // 2, mid_y, 6)
    x_cursor += beam_length + np.random.randint(gap_min, gap_max)
    
    # Final Platform
    final_platform_length = m_to_idx(2)
    add_platform(x_cursor, x_cursor + final_platform_length, mid_y, height_min, height_max)
    define_goal(x_cursor + final_platform_length // 2, mid_y, 7)

    return height_field, goals

def set_terrain_7(length, width, field_resolution, difficulty):
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


def set_terrain_8(length, width, field_resolution, difficulty):
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

def set_terrain_9(length, width, field_resolution, difficulty):
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

def set_terrain_10(length, width, field_resolution, difficulty):
    """Series of narrow beams for the robot to carefully navigate across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up beam dimensions
    beam_length = 2.0 - difficulty  # Beams get shorter with higher difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = 0.4 + 0.2 * difficulty  # The width of the beams, keeping it between 0.4m and 0.6m
    beam_width = m_to_idx(beam_width)
    beam_height = 0.2 + 0.3 * difficulty  # The height of the beams, increasing with difficulty
    gap_length = 0.4 + 0.6 * difficulty  # Gaps between beams

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, mid_y):
        y_half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - y_half_width, mid_y + y_half_width
        height_field[x1:x2, y1:y2] = beam_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(6):  # Set up 6 beams
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_beam(cur_x, cur_x + beam_length + dx, mid_y + dy)

        # Put goal in the center of the beam
        goals[i+1] = [cur_x + (beam_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += beam_length + dx + m_to_idx(gap_length)

    # Add final goal behind the last beam, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_11(length, width, field_resolution, difficulty):
    """Mixed terrains with varying heights, slopes, and narrow passages for complex navigation"""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set platform dimensions
    platform_length = 1.5 - 0.4 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.4)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.2 * difficulty, 0.4 * difficulty
    pit_depth = -1.0  # Depth of the pits between platforms
    gap_length = 0.2 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_slope(start_x, end_x, mid_y, height_start, height_end):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slope = np.linspace(height_start, height_end, x2-x1)
        slope = slope[:, None]  # Add an axis to broadcast to the y-dimension
        height_field[x1:x2, y1:y2] = slope

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length

    # Add steps and platforms
    for i in range(3):
        # Random platform height and gap between obstacles
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        dx = np.random.randint(-m_to_idx(0.1), m_to_idx(0.1))
        dy = np.random.randint(-m_to_idx(0.3), m_to_idx(0.3))
        
        # Add platform
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height)
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += platform_length + dx + gap_length

        # After every 2 platforms, add a slope
        if i % 2 == 1:
            slope_end_height = np.random.uniform(platform_height_max, platform_height_max + 0.15 * difficulty)
            add_slope(cur_x - gap_length, cur_x, mid_y + dy, 0.0, slope_end_height)

    # Transition to alternating steps
    for i in range(3):
        platform_height = np.random.uniform(platform_height_min + 0.1, platform_height_max + 0.2)
        dx = np.random.randint(-m_to_idx(0.1), m_to_idx(0.1))
        dy = np.random.randint(-m_to_idx(0.3), m_to_idx(0.3))

        # Add step up
        add_platform(cur_x, cur_x + m_to_idx(0.5) + dx, mid_y - dy, platform_height)
        goals[i+4] = [cur_x + (m_to_idx(0.25) + dx) / 2, mid_y - dy]

        cur_x += m_to_idx(0.5) + dx + gap_length

        # Add step down
        add_platform(cur_x, cur_x + m_to_idx(0.5) + dx, mid_y + dy, -platform_height)
        cur_x += m_to_idx(0.5) + dx + gap_length

    # Add final goal at the end of the course
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0  # Ensure the final surface is flat

    return height_field, goals

def set_terrain_12(length, width, field_resolution, difficulty):
    """Series of narrow beams aligned with gaps in between for the robot to balance and traverse."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up beam and gap sizes based on difficulty
    beam_width_min, beam_width_max = 0.4 - 0.2 * difficulty, 0.8 - 0.3 * difficulty
    beam_width = np.random.uniform(beam_width_min, beam_width_max)
    beam_width = m_to_idx(beam_width)
    beam_height = 0.3 + 0.5 * difficulty
    gap_width = 0.2 + 0.6 * difficulty
    gap_width = m_to_idx(gap_width)

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, beam_width, mid_y):
        half_width = beam_width // 2
        x1 = start_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x1 + beam_width, y1:y2] = beam_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    for i in range(6):  # Set up 6 beams
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_beam(cur_x, beam_width + dx, mid_y + dy)

        # Put goal at the endpoint of each beam
        goals[i+1] = [cur_x + (beam_width + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += beam_width + dx + gap_width
    
    # Add final goal behind the last beam, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_13(length, width, field_resolution, difficulty):
    """Narrow bridges and sharp turns for the robot to navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Basic obstacle sizes and properties
    bridge_width = max(0.4, 0.8 * (1 - difficulty))  # Bridge width decreases with difficulty
    bridge_width = m_to_idx(bridge_width)
    bridge_length_min = 2.0
    bridge_length_max = 3.0
    bridge_length_min = m_to_idx(bridge_length_min)
    bridge_length_max = m_to_idx(bridge_length_max)
    bridge_height = 0.05 + 0.25 * difficulty  # Increase height with difficulty
    pit_depth = -1.0  # Depth of the pit around bridges
  
    spawn_x_idx = m_to_idx(2)
    height_field[0:spawn_x_idx, :] = 0  # Spawn area flat ground
    mid_y_idx = m_to_idx(width / 2)

    # Set the initial goal at spawn area
    goals[0] = [spawn_x_idx - m_to_idx(0.5), mid_y_idx]

    def add_bridge(start_x_idx, start_y_idx, length):
        half_width = bridge_width // 2
        x1, x2 = start_x_idx, start_x_idx + length
        y1, y2 = start_y_idx - half_width, start_y_idx + half_width
        height_field[x1:x2, y1:y2] = bridge_height

    cur_x = spawn_x_idx

    for i in range(7):  # Set up 7 bridges
        bridge_length = np.random.randint(bridge_length_min, bridge_length_max)
        offset_y = np.random.uniform(-1.0, 1.0)
        offset_y = m_to_idx(offset_y)
        
        add_bridge(cur_x, mid_y_idx + offset_y, bridge_length)
        goals[i+1] = [cur_x + bridge_length // 2, mid_y_idx + offset_y]  # Goal in the center of the bridge

        # Add space (pit) before the next bridge
        pit_length = np.random.uniform(0.4, 0.6)
        pit_length = m_to_idx(pit_length)
        cur_x += bridge_length + pit_length

    # Fill in the remaining area after the last bridge with flat ground
    height_field[cur_x:, :] = 0
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y_idx]  # Final goal just after last bridge

    return height_field, goals

def set_terrain_14(length, width, field_resolution, difficulty):
    """Combination of narrow beams and raised platforms for an increased challenge."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Parameters for raised platforms and beams
    platform_length = 1.0 - 0.4 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width_min = 0.6  # Narrower platforms
    platform_width_max = 1.0
    platform_width_min = m_to_idx(platform_width_min)
    platform_width_max = m_to_idx(platform_width_max)

    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.15 + 0.25 * difficulty
    beam_width = 0.4  # Fixed narrow beam width
    beam_width = m_to_idx(beam_width)
    beam_length_min = 0.4  # Minimum beam length
    beam_length_max = 1.0  # Maximum beam length
    beam_length_min = m_to_idx(beam_length_min)
    beam_length_max = m_to_idx(beam_length_max)

    gap_length_min = 0.2
    gap_length_min = m_to_idx(gap_length_min)
    gap_length_max = 0.8 + 0.6 * difficulty
    gap_length_max = m_to_idx(gap_length_max)

    mid_y = m_to_idx(width) // 2

    def add_platform(center_x, center_y, size, height):
        half_size_length = size[0] // 2
        half_size_width = size[1] // 2
        x1, x2 = center_x - half_size_length, center_x + half_size_length
        y1, y2 = center_y - half_size_width, center_y + half_size_width
        height_field[x1:x2, y1:y2] = height

    def add_beam(start_x, mid_y, length, direction):
        if direction == 'horizontal':
            x1, x2 = start_x, start_x + length
            y1, y2 = mid_y - beam_width // 2, mid_y + beam_width // 2
        else:
            x1, x2 = start_x - beam_width // 2, start_x + beam_width // 2
            y1, y2 = mid_y, mid_y + length
        
        beam_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = beam_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(3):  # Set up 3 beams
        length = np.random.randint(beam_length_min, beam_length_max)
        direction = 'horizontal' if i % 2 == 0 else 'vertical'
        add_beam(cur_x, mid_y, length, direction)

        # Position goal in the middle of the beam
        if direction == 'horizontal':
            goals[i + 1] = [cur_x + length // 2, mid_y]
            cur_x += length + gap_length_min
        else:
            goals[i + 1] = [cur_x, mid_y + length // 2]

    for j in range(3):  # Set up 3 platforms
        size = [np.random.randint(platform_length // 2, platform_length),
                np.random.randint(platform_width_min, platform_width_max)]
        height = np.random.uniform(platform_height_min, platform_height_max)
        add_platform(cur_x, mid_y, size, height)

        goals[j + 4] = [cur_x, mid_y]
        cur_x += size[0] + gap_length_max

    # Add final goal behind the last platform
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_15(length, width, field_resolution, difficulty):
    """Narrow ledges with alternating heights for the robot to balance and navigate across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define parameters for platforms and gaps
    platform_length_min = 0.8 - 0.25 * difficulty
    platform_length_max = 1.2 - 0.1 * difficulty
    platform_width = 0.4 + 0.05 * difficulty
    platform_height_min = 0.0 + 0.2 * difficulty
    platform_height_max = 0.1 + 0.3 * difficulty
    gap_length_min = 0.1 + 0.05 * difficulty
    gap_length_max = 0.3 + 0.2 * difficulty

    platform_length_min, platform_length_max = m_to_idx([platform_length_min, platform_length_max])
    platform_width = m_to_idx(platform_width)
    gap_length_min, gap_length_max = m_to_idx([gap_length_min, gap_length_max])

    mid_y = m_to_idx(width) // 2
    half_width = platform_width // 2

    def add_platform(start_x, end_x, mid_y, height):
        """Adds a platform with a specified height."""
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[start_x:end_x, y1:y2] = height

    dx_offset = m_to_idx(0.1)
    dy_offset_min, dy_offset_max = m_to_idx([-0.2, 0.2])

    # Set spawn area to flat ground and the first goal
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(6):
        platform_length = np.random.randint(platform_length_min, platform_length_max)
        height = np.random.uniform(platform_height_min, platform_height_max)

        dy_offset = np.random.randint(dy_offset_min, dy_offset_max)
        add_platform(cur_x, cur_x + platform_length, mid_y + dy_offset, height)

        # Place goal at the middle of the platform
        goals[i+1] = [cur_x + platform_length // 2, mid_y + dy_offset]

        # Add a gap before the next platform
        gap_length = np.random.randint(gap_length_min, gap_length_max)
        cur_x += platform_length + gap_length

    # Ensure the final section is reachable
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_16(length, width, field_resolution, difficulty):
    """Narrow passageways and raised walkways to test precision and careful navigation."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]
    
    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Configure parameters based on difficulty
    path_width = 0.4 + (0.6 * (1 - difficulty))  # Path width between 0.4m and 1m
    passage_height = 0.05 + (0.3 * difficulty)  # Passage height between 0.05m and 0.35m
    walkway_height = 0.1 + (0.3 * difficulty)  # Walkway height between 0.1m and 0.4m
    section_length = 1.0 + (1.0 * difficulty)  # Varying section lengths, longer with higher difficulty

    path_width = m_to_idx(path_width)
    passage_height = np.random.uniform(passage_height, passage_height + 0.1 * difficulty)
    walkway_height = np.random.uniform(walkway_height, walkway_height + 0.1 * difficulty)
    section_length = m_to_idx(section_length)

    # Initial flat ground area for spawn point
    spawn_area = m_to_idx(2)
    height_field[:spawn_area, :] = 0
    mid_y = m_to_idx(width) // 2
    goals[0] = [spawn_area - m_to_idx(0.5), mid_y]

    cur_x = spawn_area

    def add_narrow_passage(start_x, length, height, center_y):
        half_width = path_width // 2
        x_start, x_end = start_x, start_x + length
        y_start, y_end = center_y - half_width, center_y + half_width
        height_field[x_start:x_end, y_start:y_end] = height

    # Create a sequence of narrow passages and raised walkways
    for i in range(7):
        if i % 2 == 0:
            # Add narrow passage
            add_narrow_passage(cur_x, section_length, passage_height, mid_y)
            goals[i+1] = [cur_x + section_length / 2, mid_y]
        else:
            # Add raised walkway
            height_field[cur_x:cur_x + section_length, :] = walkway_height
            goals[i+1] = [cur_x + section_length / 2, mid_y]

        cur_x += section_length

    # Final goal at the end of the course
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    return height_field, goals

def set_terrain_17(length, width, field_resolution, difficulty):
    """Combination of staircases, ramps, and small gaps to test climbing and jumping skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform, staircase, and ramp dimensions
    platform_length = 1.0 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.2, 1.6)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.2 + 0.4 * difficulty
    
    ramp_length = 1.2 - 0.3 * difficulty
    ramp_length = m_to_idx(ramp_length)
    ramp_width = platform_width
    ramp_height = 0.2 + 0.4 * difficulty

    gap_length = 0.4 + 0.3 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_ramp(start_x, end_x, mid_y, direction):
        half_width = ramp_width // 2
        height = np.linspace(0, ramp_height, end_x - start_x)
        if direction == 'down':
            height = height[::-1]
        for i in range(mid_y - half_width, mid_y + half_width):
            height_field[start_x:end_x, i] = height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length

    # Create mixed obstacles
    for i in range(6):
        # Randomly decide the obstacle type
        obstacle_type = np.random.choice(['platform', 'ramp_up', 'ramp_down'])

        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        if obstacle_type == 'platform':
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
            cur_x += platform_length + dx + gap_length
        elif obstacle_type == 'ramp_up':
            add_ramp(cur_x, cur_x + ramp_length + dx, mid_y + dy, 'up')
            goals[i + 1] = [cur_x + (ramp_length + dx) / 2, mid_y + dy]
            cur_x += ramp_length + dx + gap_length
        elif obstacle_type == 'ramp_down':
            add_ramp(cur_x, cur_x + ramp_length + dx, mid_y + dy, 'down')
            goals[i + 1] = [cur_x + (ramp_length + dx) / 2, mid_y + dy]
            cur_x += ramp_length + dx + gap_length

    # Add final goal behind the last obstacle
    goals[7] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_18(length, width, field_resolution, difficulty):
    """Multi-skill course featuring small ramps, jumps, and a final narrow bridge."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    mid_y = m_to_idx(width / 2)

    def add_ramp(start_x, end_x, mid_y, start_height, end_height):
        """Add a ramp to the height field."""
        for x in range(start_x, end_x):
            height_value = start_height + ((end_height - start_height) * (x - start_x) / (end_x - start_x))
            height_field[x, mid_y- m_to_idx(0.5): mid_y + m_to_idx(0.5)] = height_value

    def add_jump(start_x, mid_y, height, length, width):
        """Add a platform to jump onto."""
        x1, x2 = start_x, start_x + length
        y1, y2 = mid_y - width//2, mid_y + width//2
        height_field[x1:x2, y1:y2] = height

    def add_narrow_bridge(start_x, end_x, mid_y, width):
        """Add a narrow bridge towards the end of the course."""
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - width//2, mid_y + width//2
        height_field[x1:x2, y1:y2] = 0.5

    # Set up levels and parameters
    ramp_height = 0.2 + 0.3 * difficulty
    platform_height = 0.4 + 0.3 * difficulty
    gap_length = m_to_idx(0.4)
    narrow_bridge_width = m_to_idx(0.4)

    # Clear spawn area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    # Add series of ramps and platforms
    for i in range(3):
        ramp_length = m_to_idx(1.0 + 0.5 * difficulty)
        add_ramp(cur_x, cur_x + ramp_length, mid_y, 0, ramp_height)
        goals[i+1] = [cur_x + ramp_length//2, mid_y]
        
        cur_x += ramp_length + gap_length
        
        platform_length = m_to_idx(1.0)
        add_jump(cur_x, mid_y, platform_height, platform_length, m_to_idx(1.0))
        goals[i+2] = [cur_x + platform_length//2, mid_y]
        
        cur_x += platform_length + gap_length

    # Add a final narrow bridge
    bridge_length = m_to_idx(2.0)
    add_narrow_bridge(cur_x, cur_x + bridge_length, mid_y, narrow_bridge_width)
    goals[6] = [cur_x + bridge_length//2, mid_y]

    cur_x += bridge_length
    
    # Set final goal
    goals[7] = [cur_x + m_to_idx(0.5), mid_y]

    #Ensure remaining area is flat
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_19(length, width, field_resolution, difficulty):
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

def set_terrain_20(length, width, field_resolution, difficulty):
    """Stepping stones obstacle course testing the quadruped's precision and agility."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up step dimensions
    step_size = 0.3  # Each stone has a diameter of approximately 0.3 meters
    step_size_idx = m_to_idx(step_size)
    gap_min = 0.4  # Minimum gap between steps
    gap_max = 0.8  # Maximum gap between steps
    gap_min_idx = m_to_idx(gap_min)
    gap_max_idx = m_to_idx(gap_max)
    step_height_min, step_height_max = 0.1, 0.4  # Height range for steps
    step_height_min += 0.1 * difficulty
    step_height_max += 0.3 * difficulty

    mid_y = m_to_idx(width // 2)

    def add_step(x, y):
        """Adds a stepping stone at the specified (x, y) location."""
        radius = step_size_idx // 2
        step_height = np.random.uniform(step_height_min, step_height_max)
        height_field[x - radius:x + radius, y - radius:y + radius] = step_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # Place the first goal right at the spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    cur_y = mid_y

    for i in range(7):  # Set up 7 stepping stones
        add_step(cur_x, cur_y)

        # Update the goal to the center of the current step
        goals[i+1] = [cur_x, cur_y]

        # Move to the next position for the next step
        gap_x = np.random.randint(gap_min_idx, gap_max_idx)
        cur_x += gap_x

        # Slightly randomize the y position for the next step
        dy = np.random.uniform(-gap_max / 2, gap_max / 2)
        cur_y = np.clip(cur_y + m_to_idx(dy), step_size_idx, m_to_idx(width) - step_size_idx)
    
    # Ensure the last goal is reachable and set on flat ground
    goals[-1] = [cur_x + gap_min_idx, mid_y]
    height_field[cur_x + gap_min_idx:, :] = 0

    return height_field, goals

def set_terrain_21(length, width, field_resolution, difficulty):
    """Obstacle course focuses on a zigzag path with narrow steps to test lateral agility and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform dimensions - steps are much narrower but long, height increases with difficulty
    step_length = 0.8 - 0.3 * difficulty
    step_length = m_to_idx(step_length)
    step_width = np.random.uniform(0.4, 0.7)
    step_width = m_to_idx(step_width)
    step_height_min, step_height_max = 0.1 + 0.2 * difficulty, 0.1 + 0.3 * difficulty

    mid_y = m_to_idx(width) // 2

    # Helper function to add a step
    def add_step(start_x, end_x, start_y, end_y, height):
        height_field[start_x:end_x, start_y:end_y] = height
        
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
    step_direction = 1  # 1 means moving towards positive y, -1 means negative y

    for i in range(6):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        start_y = mid_y + step_direction * (step_width // 2 + dy)
        end_y = start_y + step_direction * step_width
        
        step_height = np.random.uniform(step_height_min, step_height_max)
        add_step(cur_x, cur_x + step_length, start_y, end_y, step_height)
        
        # Place the goal at the center of the step
        goal_x = cur_x + step_length // 2
        goal_y = (start_y + end_y) // 2
        goals[i + 1] = [goal_x, goal_y]
        
        cur_x += step_length + m_to_idx(0.2)  # Space between consecutive steps
        step_direction *= -1  # Switch direction for zigzag pattern
        
    # Add final goal behind the last step, filling in remaining space
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_22(length, width, field_resolution, difficulty):
    """Narrow paths and gaps for precise balancing and navigation."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define narrow path dimensions and gap lengths
    path_width = 0.4
    path_width = m_to_idx(path_width)
    path_length = 2.0  # Fixed length for simplicity
    path_length = m_to_idx(path_length)
    path_height_min, path_height_max = 0.1 + 0.3 * difficulty, 0.2 + 0.4 * difficulty
    gap_length = 0.2 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_path(start_x, end_x, mid_y):
        half_width = path_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        path_height = np.random.uniform(path_height_min, path_height_max)
        height_field[x1:x2, y1:y2] = path_height

    dx_min, dx_max = -0.05, 0.05
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.15, 0.15
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Starting base line for paths and gaps
    cur_x = spawn_length
    for i in range(6):  # Set up 6 paths with gaps
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_path(cur_x, cur_x + path_length + dx, mid_y + dy)

        # Put goal in the center of the path
        goals[i+1] = [cur_x + (path_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += path_length + dx + gap_length
    
    # Final goal behind the last path, bridging the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_23(length, width, field_resolution, difficulty):
    """Higher platforms, wider gaps, and lateral transitions to test robot's balance and navigation abilities."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set dimensions and positions for platforms and gaps
    platform_size = 1.0 - 0.3 * difficulty  # Platforms become smaller with difficulty
    platform_size_idx = m_to_idx(platform_size)
    platform_width = np.random.uniform(0.9, 1.2)
    platform_width_idx = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.15 * difficulty, 0.3 * difficulty  # Higher platforms
    gap_length = 0.3 + 0.5 * difficulty  # Wider gaps with difficulty
    gap_length_idx = m_to_idx(gap_length)

    mid_y = m_to_idx(width / 2)

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width_idx // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_beam(start_x, end_x, mid_y):
        beam_width = 0.4  # Narrow beam width
        beam_width_idx = m_to_idx(beam_width)
        half_width = beam_width_idx // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        beam_height = platform_height_max  # Consistent height for review
        height_field[x1:x2, y1:y2] = beam_height
        
    def add_ramp(start_x, end_x, mid_y, direction):
        """Adds a sloped ramp for the robot to ascend or descend."""
        half_width = platform_width_idx // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(platform_height_min, platform_height_max)
        slant = np.linspace(0, ramp_height, num=y2-y1)[::direction]
        slant = slant[None, :]
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = m_to_idx(2)
    
    # First platform to get started
    add_platform(cur_x, cur_x + platform_size_idx, mid_y)
    goals[1] = [cur_x + platform_size_idx // 2, mid_y]
    
    cur_x += platform_size_idx + gap_length_idx

    for i in range(2, 8, 2):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        # Add a beam obstacle
        add_beam(cur_x, cur_x + platform_size_idx + dx, mid_y + dy)
        goals[i] = [cur_x + (platform_size_idx + dx) // 2, mid_y + dy]
        cur_x += platform_size_idx + dx + gap_length_idx
        
        # Add a sideways-facing ramp
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        direction = (-1) ** i
        dy = dy * direction

        add_ramp(cur_x, cur_x + platform_size_idx + dx, mid_y + dy, direction)
        goals[i + 1] = [cur_x + (platform_size_idx + dx) // 2, mid_y + dy]
        cur_x += platform_size_idx + dx + gap_length_idx

    # Final flat area to end the course
    goals[7] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_24(length, width, field_resolution, difficulty):
    """Series of hills and mounds for the robot to climb up and down, testing balance and stability."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set the overall length and width of the hill segments
    hill_length = 1.5 + 1.0 * difficulty  # Length of a hill, increases with difficulty
    hill_length = m_to_idx(hill_length)

    space_between_hills = 0.1 * difficulty
    space_between_hills = m_to_idx(space_between_hills)

    hill_height_min = 0.1 + 0.1 * difficulty  # Minimum height of the hills
    hill_height_max = 0.25 + 0.5 * difficulty  # Maximum height of the hills

    mid_y = m_to_idx(width) // 2

    def add_hill(start_x, end_x, mid_y, height, slope):
        half_width = m_to_idx(1.5)  # ensuring around 1.5 meters width for hills
        y1, y2 = mid_y - half_width // 2, mid_y + half_width // 2

        # Create slope: linear increase from ground to peak height
        for x in range(start_x, end_x):
            current_height = height * ((x - start_x) / (end_x - start_x)) ** slope
            height_field[x, y1:y2] = current_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    
    # Place first goal near the spawn point
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(6):  # Plan a sequence consisting of 6 hills
        hill_height = np.random.uniform(hill_height_min, hill_height_max)
        slope = np.random.uniform(1, 2)  # Randomized slope between 1 (linear) and 2 (quadratic)
        add_hill(cur_x, cur_x + hill_length, mid_y, hill_height, slope)
        
        # Place goal near the peak of each hill
        goals[i+1] = [cur_x + hill_length // 2, mid_y]

        cur_x += hill_length + space_between_hills  # Move to the position for the next hill

    # Add final goal behind the last hill, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_25(length, width, field_resolution, difficulty):
    """A series of balance beams of varying heights and widths."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up beam dimensions and gaps
    # Beam height and width vary with difficulty
    beam_height_min, beam_height_max = 0.05 * difficulty, 0.3 * difficulty
    beam_width_min, beam_width_max = 0.4, 1.0  # Ensure beams are traversable
    gap_length = 0.1 + 0.7 * difficulty

    beam_length = length / 8  # Divide the length of the course into 8 segments
    beam_length = m_to_idx(beam_length)
    gap_length = m_to_idx(gap_length)

    def add_beam(start_x, end_x, y_center, beam_width, beam_height):
        half_width = beam_width // 2
        y1, y2 = y_center - half_width, y_center + half_width
        height_field[start_x:end_x, y1:y2] = beam_height

    mid_y = m_to_idx(width) // 2

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -m_to_idx(0.4), m_to_idx(0.4)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    for i in range(6):  # Set up 6 balance beams
        beam_height = np.random.uniform(beam_height_min, beam_height_max)
        beam_width = np.random.uniform(beam_width_min, beam_width_max)
        beam_width = m_to_idx(beam_width)
        
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        add_beam(cur_x, cur_x + beam_length + dx, mid_y + dy, beam_width, beam_height)

        # Put goal in the center of the beam
        goals[i+1] = [cur_x + (beam_length + dx) // 2, mid_y + dy]

        # Add gap
        cur_x += beam_length + dx + gap_length

    # Add final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_26(length, width, field_resolution, difficulty):
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

def set_terrain_27(length, width, field_resolution, difficulty):
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

def set_terrain_28(length, width, field_resolution, difficulty):
    """Combination of platforms and ramps to traverse a pit for the robot to climb on and jump across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define dimensions and properties of platforms and ramps
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.2)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.2 * difficulty, 0.1 + 0.3 * difficulty
    gap_length = 0.2 + 0.5 * difficulty
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
        ramp_height = np.random.uniform(platform_height_min, platform_height_max)
        slant = np.linspace(0, ramp_height, num=x2-x1)
        slant = slant[::direction]
        slant = slant[:, None]  # Add a dimension for broadcasting to y
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy = m_to_idx(0.4)  # Consistent y offset

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Set remaining area to be a pit
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    for i in range(4):  # Set up 4 platforms
        dx = np.random.randint(dx_min, dx_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y)

        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y]

        cur_x += platform_length + dx + gap_length

    for i in range(4, 7):  # Set up 3 ramps
        dx = np.random.randint(dx_min, dx_max)
        direction = (-1) ** i  # Alternate left and right ramps
        add_ramp(cur_x, cur_x + platform_length + dx, mid_y, direction)

        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y]

        cur_x += platform_length + dx + gap_length
    
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_29(length, width, field_resolution, difficulty):
    """A series of hurdles each with varying heights for the robot to jump over."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # Starting position for the quadruped
    starting_x = spawn_length
    mid_y = m_to_idx(width/2)

    # Set first goal
    goals[0] = [starting_x, mid_y]

    # Dimensions for hurdles
    hurdle_height_min = 0.1 * difficulty  # Minimum height of hurdles
    hurdle_height_max = 0.4 * difficulty  # Maximum height of hurdles
    hurdle_width = m_to_idx(1)  # 1 meter width
    hurdle_gap_min = m_to_idx(0.5 + 0.5 * difficulty) # Minimum gap between hurdles
    hurdle_gap_max = m_to_idx(1 + 1 * difficulty) # Maximum gap between hurdles

    num_hurdles = 6  # Number of hurdles to place

    for i in range(1, num_hurdles+1):
        # Randomly determine the height of the hurdle
        height = np.random.uniform(hurdle_height_min, hurdle_height_max)

        # Place the hurdle at the current position
        height_field[starting_x:starting_x + hurdle_width, :] = height

        # Set the goal location just before the start of the next hurdle
        goals[i] = [starting_x + hurdle_width + hurdle_gap_min//2, mid_y]

        # Move starting_x to the position after the gap
        starting_x += hurdle_width + np.random.randint(hurdle_gap_min, hurdle_gap_max)

    # Final goal, positioned at the end of the terrain.
    goals[-1] = [m_to_idx(length - 1), mid_y]

    return height_field, goals

def set_terrain_30(length, width, field_resolution, difficulty):
    """Narrow passages with varying heights for the robot to maneuver on."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define beam characteristics
    beam_length = m_to_idx(0.4 + 0.2 * difficulty)  # Varies from 0.4m to 0.6m depending on difficulty
    beam_width = m_to_idx(0.4)  # Constant width

    # Heights will have more variation with increased difficulty
    min_height = 0.05 * difficulty
    max_height = 0.2 + 0.3 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_beam(x, y_center):
        y1 = y_center - beam_width // 2
        y2 = y_center + beam_width // 2
        beam_height = np.random.uniform(min_height, max_height)
        height_field[x:x + beam_length, y1:y2] = beam_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [m_to_idx(1), mid_y]  # First goal at the spawn area

    cur_x = spawn_length
    dx_range = m_to_idx([-0.1, 0.1])  # Small variation in x direction
    dy_range = m_to_idx([-0.5 + 0.3 * difficulty, 0.5 - 0.3 * difficulty])  # Larger variation in y direction for difficulty

    for i in range(7):  # Set up 7 beams
        dx = np.random.randint(dx_range[0], dx_range[1])
        dy = np.random.randint(dy_range[0], dy_range[1])
        add_beam(cur_x + dx, mid_y + dy)

        # Place goal within each beam
        goals[i+1] = [cur_x + dx + beam_length // 2, mid_y + dy]

        # Pass to the next beam
        cur_x += beam_length + dx

    return height_field, goals

def set_terrain_31(length, width, field_resolution, difficulty):
    """Series of stepping stone platforms of varying heights for the robot to jump across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    def add_platform(start_x, start_y, platform_width, platform_length, platform_height):
        end_x = start_x + m_to_idx(platform_length)
        end_y = start_y + m_to_idx(platform_width)
        height_field[start_x:end_x, start_y:end_y] = platform_height

    # Convert sizes to indices
    course_length = m_to_idx(length)
    course_width = m_to_idx(width)
    quadruped_length = m_to_idx(0.645)
    quadruped_width = m_to_idx(0.28)

    # Initial spawn area
    height_field[0:m_to_idx(2), :] = 0
    goals[0] = [m_to_idx(1), course_width // 2]

    # Initial platform properties
    platform_length = 0.8 - 0.2 * difficulty
    platform_width = 0.5
    platform_height_min = 0.2 * difficulty
    platform_height_max = platform_height_min + 0.1
    num_platforms = 7

    cur_x = m_to_idx(2)
    platform_gap = 0.2
    platform_gap_idx = m_to_idx(platform_gap)

    for i in range(num_platforms):
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        platform_y = np.random.randint(quadruped_width, course_width - quadruped_width)
        
        add_platform(cur_x, platform_y, platform_width, platform_length, platform_height)
        
        # Set goal position on platform
        goals[i+1] = [cur_x + m_to_idx(platform_length) // 2, platform_y + m_to_idx(platform_width) // 2]

        # Prepare for next platform
        cur_x += m_to_idx(platform_length) + platform_gap_idx
        platform_height_min += 0.05
        platform_height_max += 0.05
        
        # Adjust heights for increasing difficulty
        if i < num_platforms - 1:
            height_field[cur_x:cur_x + platform_gap_idx, :] = 0

    # Final goal
    goals[-1] = [min(cur_x + m_to_idx(platform_length) // 2, course_length - 1), course_width // 2]

    return height_field, goals

def set_terrain_32(length, width, field_resolution, difficulty):
    """Narrow beams and larger platforms for balance and transition skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Terrain dimensions and parameters
    mid_y = m_to_idx(width) // 2
    beam_height_min, beam_height_max = 0.05, 0.4 * difficulty
    beam_width = m_to_idx(0.2)  # Narrow beam, 0.2 meters
    platform_width = m_to_idx(1.2)  # Broad platform, 1.2 meters
    platform_length = m_to_idx(1.0 - 0.3 * difficulty)
    gap_length = m_to_idx(0.5 + 0.5 * difficulty)

    def add_beam(start_x, end_x, mid_y):
        """Add a narrow beam to the terrain."""
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        beam_height = np.random.uniform(beam_height_min, beam_height_max)
        height_field[x1:x2, y1:y2] = beam_height

    def add_platform(start_x, end_x, mid_y):
        """Add a broad platform to the terrain."""
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(beam_height_min, beam_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    cur_x = m_to_idx(2)
    height_field[:cur_x, :] = 0
    goals[0] = [cur_x / 2, mid_y]

    def add_goal(i, cur_x, length, mid_y):
        """Add a goal at the center of the current surface."""
        goals[i] = [cur_x + length // 2, mid_y]

    # Place obstacles and goals
    for i in range(7):
        if i % 2 == 0:  # Add a narrow beam
            beam_length = platform_length if i == 0 else platform_length - m_to_idx(0.2)
            add_beam(cur_x, cur_x + beam_length, mid_y)
            add_goal(i + 1, cur_x, beam_length, mid_y)
            cur_x += beam_length + gap_length
        else:  # Add a broad platform
            add_platform(cur_x, cur_x + platform_length, mid_y)
            add_goal(i + 1, cur_x, platform_length, mid_y)
            cur_x += platform_length + gap_length

    goals[-1] = [cur_x - gap_length / 2, mid_y]
    
    # Final area should be flat
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_33(length, width, field_resolution, difficulty):
    """A series of varying steps to test the robot's climbing and descending capabilities."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Step characteristics
    step_heights = [0.05, 0.1, 0.15, 0.2]  # Heights in meters 
    step_width_range = (1.0, 1.6)  # Range of step widths in meters
    step_length = 0.4  # Length of each step in meters

    step_length = m_to_idx(step_length)
    step_width_min, step_width_max = m_to_idx(step_width_range[0]), m_to_idx(step_width_range[1])
    mid_y = m_to_idx(width) // 2

    def add_step(start_x, start_y, step_height, step_width):
        x2 = start_x + step_length
        y1 = start_y - step_width // 2
        y2 = start_y + step_width // 2
        height_field[start_x:x2, y1:y2] = step_height

    # Setting initial flat area for spawn
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(7):  # Create 7 steps
        step_height = random.choice(step_heights) * difficulty
        step_width = random.randint(step_width_min, step_width_max)
        
        add_step(cur_x, mid_y, step_height, step_width)
        
        # Place goal at the top of each step
        goals[i + 1] = [cur_x + step_length // 2, mid_y]

        cur_x += step_length

    # Set the height at the end to zero (flat ground)
    height_field[cur_x:, :] = 0
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    return height_field, goals

def set_terrain_34(length, width, field_resolution, difficulty):
    """Multiple platforms connected by ramps and small gaps for balancing and climbing."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and ramp dimensions
    platform_length = 1.0 - 0.15 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.4) 
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.1 * difficulty, 0.2 + 0.25 * difficulty
    ramp_height_min, ramp_height_max = 0.0 + 0.3 * difficulty, 0.2 + 0.35 * difficulty
    gap_length = 0.1 + 0.3 * difficulty  
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_ramp(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        slant = np.linspace(0, ramp_height, num=y2-y1)
        slant = slant[None, :]  # Add a dimension for broadcasting to x
        height_field[x1:x2, y1:y2] = slant

    def add_safe_zone(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = 0

    dx_min, dx_max = -0.1, 0.1 
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.0, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    dx = np.random.randint(dx_min, dx_max)
    dy = np.random.randint(dy_min, dy_max)
    
    add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
    goals[1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
    cur_x += platform_length + dx + gap_length

    for i in range(1, 6):  # Set up 5 ramps
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        if i % 2 == 1:
            add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy)
        else:
            add_safe_zone(cur_x, cur_x + platform_length + dx, mid_y + dy)

        goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

    # Add final goal to the flat area beyond last obstacle
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0.0

    return height_field, goals

def set_terrain_35(length, width, field_resolution, difficulty):
    """Mixed obstacles including wide platforms, uneven stepping stones, and gentle slopes for agility and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform parameters
    platform_width = np.random.uniform(1.2, 1.8)
    platform_width = m_to_idx(platform_width)
    platform_length = 1.5 - 0.5 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_height_min, platform_height_max = 0.1 * difficulty, 0.3 * difficulty

    # Stepping stone parameters
    stepping_stone_size = 0.5
    stepping_stone_size = m_to_idx(stepping_stone_size)
    stepping_stone_height_min, stepping_stone_height_max = 0.05 * difficulty, 0.2 * difficulty

    # Slope parameters
    slope_width = platform_width
    slope_length = 1.5 - 0.5 * difficulty
    slope_length = m_to_idx(slope_length)
    slope_height_min, slope_height_max = 0.1 * difficulty, 0.25 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_stepping_stone(mid_x, mid_y, height):
        half_size = stepping_stone_size // 2
        x1, x2 = mid_x - half_size, mid_x + half_size
        y1, y2 = mid_y - half_size, mid_y + half_size
        height_field[x1:x2, y1:y2] = height

    def add_slope(start_x, end_x, mid_y, height):
        half_width = slope_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slope = np.linspace(0, height, num=x2-x1)[:, None]  # Creating gradual slope
        height_field[x1:x2, y1:y2] = slope

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # First goal at the end of the flat area
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    dx_min, dx_max = m_to_idx(-0.1), m_to_idx(0.1)
    dy_min, dy_max = m_to_idx(-0.4), m_to_idx(0.4)

    # Add first wide platform
    add_platform(cur_x, cur_x + platform_length, mid_y, np.random.uniform(platform_height_min, platform_height_max))
    goals[1] = [cur_x + platform_length // 2, mid_y]
    cur_x += platform_length + m_to_idx(0.5)

    # Add series of stepping stones
    for i in range(2, 6):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_stepping_stone(cur_x + dx, mid_y + dy, np.random.uniform(stepping_stone_height_min, stepping_stone_height_max))
        goals[i] = [cur_x + dx, mid_y + dy]
        cur_x += stepping_stone_size + m_to_idx(0.5)

    # Add final slope
    slope_height = np.random.uniform(slope_height_min, slope_height_max)
    add_slope(cur_x, cur_x + slope_length, mid_y, slope_height)
    goals[-2] = [cur_x + slope_length // 2, mid_y]
    cur_x += slope_length + m_to_idx(0.5)

    # Last goal at the end
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0  # Ensure no further obstacles

    return height_field, goals

def set_terrain_36(length, width, field_resolution, difficulty):
    """Stepping stones across a stream for the robot to jump and balance on."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up stepping stone dimensions
    stone_diameter_min = 0.4  # minimum diameter of stepping stones
    stone_diameter_max = 0.8  # maximum diameter of stepping stones
    stone_height_min, stone_height_max = 0.1 + 0.1 * difficulty, 0.15 + 0.25 * difficulty
    gap_length_min = 0.3  # minimum gap between stepping stones
    gap_length_max = 0.7 + 0.3 * difficulty  # maximum gap increases with difficulty

    def add_stepping_stone(center_x, center_y):
        radius = np.random.uniform(stone_diameter_min / 2, stone_diameter_max / 2)
        radius_idx = m_to_idx(radius)
        stone_height = np.random.uniform(stone_height_min, stone_height_max)

        x, y = m_to_idx(center_x), m_to_idx(center_y)
        for i in range(-radius_idx, radius_idx + 1):
            for j in range(-radius_idx, radius_idx + 1):
                if i**2 + j**2 <= radius_idx**2:
                    height_field[x + i, y + j] = stone_height

    spawn_length = m_to_idx(2)
    mid_y = m_to_idx(width / 2)

    # Set spawn area to flat ground
    height_field[0:spawn_length, :] = 0
    # Put the first goal at spawn area
    goals[0] = [m_to_idx(1), mid_y]

    cur_x = 2.0
    for i in range(1, 8):  # Set up 7 stepping stones
        stone_center_y = width / 2 + np.random.uniform(-width / 4, width / 4)
        stone_center_x = cur_x + np.random.uniform(gap_length_min, gap_length_max)
        add_stepping_stone(stone_center_x, stone_center_y)

        # Place goal on the current stepping stone
        goals[i] = [m_to_idx(stone_center_x), m_to_idx(stone_center_y)]
        
        # Update current x position for the next stone
        cur_x = stone_center_x

    return height_field, goals

def set_terrain_37(length, width, field_resolution, difficulty):
    """Series of different height platforms for the robot to jump onto and adapt its approach."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions for varying heights and gaps
    platform_length = 0.8 - 0.2 * difficulty  # Decreased length to make it jumpier
    platform_length = m_to_idx(platform_length)
    platform_width = 0.4 + 0.4 * (1 - difficulty)  # Narrow platforms
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1, 0.8 * difficulty  # Varied heights
    gap_length = 0.3 + 0.5 * difficulty  # Larger gaps
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Start creating platforms and gaps after spawn area
    cur_x = spawn_length

    for i in range(7):  # 7 platforms
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)

        # Put goal at the center of the platform
        goals[i+1] = [cur_x + platform_length // 2, mid_y]

        # Add gap
        cur_x += platform_length + gap_length
    
    # Add final goal beyond the last platform
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_38(length, width, field_resolution, difficulty):
    """Hurdles and beams obstacle course for the robot to step over and balance on."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Height of the hurdles
    hurdle_height_min, hurdle_height_max = 0.1 + 0.1 * difficulty, 0.3 + 0.2 * difficulty
    hurdle_length = m_to_idx(0.4)
    hurdle_width = m_to_idx(1.0)

    # Width of the beams
    beam_length = m_to_idx(1.0)
    beam_width = m_to_idx(0.4)
    beam_height_min, beam_height_max = 0.05 + 0.1 * difficulty, 0.2 + 0.2 * difficulty

    def add_hurdle(start_x, y):
        """Add a hurdle at the specified location."""
        x1, x2 = start_x, start_x + hurdle_length
        y1, y2 = y - hurdle_width // 2, y + hurdle_width // 2
        hurdle_height = np.random.uniform(hurdle_height_min, hurdle_height_max)
        height_field[x1:x2, y1:y2] = hurdle_height

    def add_beam(start_x, y):
        """Add a narrow beam at the specified location."""
        x1, x2 = start_x, start_x + beam_length
        y1, y2 = y - beam_width // 2, y + beam_width // 2
        beam_height = np.random.uniform(beam_height_min, beam_height_max)
        height_field[x1:x2, y1:y2] = beam_height

    mid_y = m_to_idx(width) // 2

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Place first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length + m_to_idx(0.5)
    turn_offset_y = m_to_idx(0.4)
    y_positions = [
        mid_y - turn_offset_y,
        mid_y + turn_offset_y,
        mid_y - turn_offset_y,
        mid_y + turn_offset_y,
        mid_y - turn_offset_y,
        mid_y + turn_offset_y,
    ]

    # Add alternating hurdles and beams along the course
    for i, y in enumerate(y_positions[:6]):
        if i % 2 == 0:
            add_hurdle(cur_x, y)
            goals[i+1] = [cur_x + hurdle_length // 2, y]
        else:
            add_beam(cur_x, y)
            goals[i+1] = [cur_x + beam_length // 2, y]
        cur_x += m_to_idx(2)
    
    # Final goal
    goals[7] = [cur_x + m_to_idx(1), mid_y - turn_offset_y]

    return height_field, goals

def set_terrain_39(length, width, field_resolution, difficulty):
    """Stepping stones across a river with varying heights and distances."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Stepping stone parameters
    stone_diameter_min = 0.4  # meters
    stone_diameter_max = 0.8  # meters
    stone_height_min = 0.1  # meters
    stone_height_max = 0.4  # meters

    # Distance between stones varies with difficulty
    min_stone_distance = 0.5  # meters
    max_stone_distance = 1.5 + 3.5 * difficulty  # meters

    mid_y = m_to_idx(width) // 2

    def add_stone(center_x, center_y):
        x_rad = m_to_idx(random.uniform(stone_diameter_min, stone_diameter_max) / 2)
        y_rad = x_rad  # Making stones circular
        stone_height = random.uniform(stone_height_min, stone_height_max) * difficulty
        
        x1 = center_x - x_rad
        x2 = center_x + x_rad
        y1 = center_y - y_rad
        y2 = center_y + y_rad
        
        x1, x2 = max(x1, 0), min(x2, height_field.shape[0])
        y1, y2 = max(y1, 0), min(y2, height_field.shape[1])
        
        height_field[x1:x2, y1:y2] = stone_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # First goal, near the spawn area
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]
    
    # Keep track of the current position where new stones are added
    cur_x = spawn_length
    for i in range(7):  # Place 7 stepping stones
        stone_distance = random.uniform(min_stone_distance, max_stone_distance)
        center_x = cur_x + m_to_idx(stone_distance)
        center_y = mid_y + random.randint(m_to_idx(-0.5), m_to_idx(0.5))  # Allow small y deviations

        add_stone(center_x, center_y)

        # Place a goal at the middle of each stone
        goals[i + 1] = [center_x, center_y]

        cur_x = center_x  # Update the current x for the next stone
    
    # Ensure last part of terrain is flat, setting final goal
    final_running_length = m_to_idx(2)
    height_field[cur_x + m_to_idx(0.5):cur_x + final_running_length, :] = 0
    goals[-1] = [cur_x + m_to_idx(1), mid_y]

    return height_field, goals

# INSERT TERRAIN FUNCTION DEFINITIONS HERE
