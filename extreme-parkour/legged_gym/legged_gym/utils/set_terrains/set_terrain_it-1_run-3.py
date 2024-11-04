
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
    """Stepping stones over varying heights and distances to test stability and jumping abilities."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Stepping stone dimensions
    stone_length = 0.6 - 0.1 * difficulty
    stone_length = m_to_idx(stone_length)
    stone_width = 0.4 + 0.2 * difficulty
    stone_width = m_to_idx(stone_width)
    stone_height_min, stone_height_max = 0.0 + 0.1 * difficulty, 0.1 + 0.2 * difficulty
    gap_length = 0.3 + 0.4 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_stone(center_x, center_y, height):
        half_length = stone_length // 2
        half_width = stone_width // 2
        x_range = slice(center_x - half_length, center_x + half_length)
        y_range = slice(center_y - half_width, center_y + half_width)
        height_field[x_range, y_range] = height

    dx_min, dx_max = -gap_length // 2, gap_length // 2
    dy_min, dy_max = -stone_width // 2, stone_width // 2

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length // 2, mid_y]  # Put first goal at spawn

    cur_x = spawn_length + gap_length
    for i in range(7):  # Set up 7 stepping stones
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        stone_height = np.random.uniform(stone_height_min, stone_height_max)
        add_stone(cur_x + dx, mid_y + dy, stone_height)

        # Put goal in the center of the stone
        goals[i + 1] = [cur_x + dx, mid_y + dy]

        # Add gap
        cur_x += stone_length + gap_length

    return height_field, goals

def set_terrain_1(length, width, field_resolution, difficulty):
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

def set_terrain_2(length, width, field_resolution, difficulty):
    """Series of staggered, raised platforms with varying heights and gaps for the robot to jump across and navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions
    platform_length = 1.0 + 0.4 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 0.8 + 0.2 * difficulty  # Slightly increase platform width
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.2 * difficulty, 0.1 + 0.3 * difficulty
    gap_length = 0.3 + 0.2 * difficulty
    gap_length = m_to_idx(gap_length)
    
    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_gap(start_x, end_x):
        height_field[start_x:end_x, :] = -1.0  # Set a pit for the gap

    dx_min, dx_max = -m_to_idx(0.2), m_to_idx(0.2)
    dy_min, dy_max = -m_to_idx(0.2), m_to_idx(0.2)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Set remaining area to be a pit
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    for i in range(6):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height)
        
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        cur_x += platform_length + dx
        add_gap(cur_x, cur_x + gap_length)
        cur_x += gap_length
    
    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_3(length, width, field_resolution, difficulty):
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

def set_terrain_4(length, width, field_resolution, difficulty):
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

def set_terrain_5(length, width, field_resolution, difficulty):
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

def set_terrain_6(length, width, field_resolution, difficulty):
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

def set_terrain_7(length, width, field_resolution, difficulty):
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

def set_terrain_8(length, width, field_resolution, difficulty):
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

def set_terrain_9(length, width, field_resolution, difficulty):
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

# INSERT TERRAIN FUNCTION DEFINITIONS HERE
