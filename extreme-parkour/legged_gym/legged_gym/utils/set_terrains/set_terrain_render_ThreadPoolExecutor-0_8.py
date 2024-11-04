
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
    """Series of ramps and turns to test the quadruped's ability to navigate inclined planes and make sharp turns."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    ramp_length = 1.0  # 1 meter ramps
    ramp_height_min, ramp_height_max = 0.05, 0.4  # start from 5 cm to 40 cm

    # Adding some variability to ramp size
    height_variation_factor = difficulty * 0.3
    ramp_length_idxs = m_to_idx(ramp_length)
    ramp_height_min, ramp_height_max = ramp_height_min + height_variation_factor, ramp_height_max + height_variation_factor

    y_center = m_to_idx(width / 2)
    
    def add_ramp(start_x, end_x, start_y, end_y, height_delta):
        x1, x2 = start_x, end_x
        y1, y2 = start_y, end_y
        for x in range(x1, x2):
            height = height_delta * ((x - x1) / max(1, x2 - x1))  # Linear ramp
            height_field[x, y1:y2] = height
    
    # Initialize flat start area
    quad_start_idx = m_to_idx(1)
    height_field[:quad_start_idx, :] = 0

    # Initial goal at the start
    goals[0] = [quad_start_idx - m_to_idx(0.5), y_center]

    cur_x = quad_start_idx

    # Create obstacles ensuring there's enough length for each
    for i in range(7):
        if i % 2 == 0:
            # Ramp upwards
            ramp_height = random.uniform(ramp_height_min, ramp_height_max)
            add_ramp(cur_x, cur_x + ramp_length_idxs, y_center - m_to_idx(0.5), y_center + m_to_idx(0.5), ramp_height)
            goal_x = cur_x + ramp_length_idxs // 2
            goal_y = y_center
        else:
            # Sharp Turn
            turn_offset = m_to_idx(1 if i // 2 % 2 == 0 else -1)
            end_y_center = y_center + turn_offset
            mid_x = cur_x + ramp_length_idxs // 2
            height_field[cur_x:cur_x + ramp_length_idxs // 2, min(y_center, end_y_center):max(y_center, end_y_center)+1] = ramp_height
            goal_x = mid_x
            goal_y = end_y_center

        goals[i+1] = [goal_x, goal_y]
        cur_x += ramp_length_idxs

    # Place the 8th goal
    goals[7] = [cur_x + ramp_length_idxs // 2, y_center]

    return height_field, goals

def set_terrain_1(length, width, field_resolution, difficulty):
    """Series of platforms and ramps with varying heights and gaps to challenge navigation, climbing, jumping, and maneuverability skills."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not isinstance(m, list) and not isinstance(m, tuple) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and ramp dimensions
    platform_length = 1.0 - 0.25 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.2)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 * difficulty, 0.3 * difficulty
    gap_length = 0.4 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    for i in range(6):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        add_platform(cur_x, cur_x + platform_length, mid_y + dy, platform_height)
        goals[i + 1] = [cur_x + platform_length / 2, mid_y + dy]

        cur_x += platform_length + gap_length + dx

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_2(length, width, field_resolution, difficulty):
    """Stepping stone platforms for the robot to precisely navigate across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define stepping stone dimensions and properties
    stone_length = 0.6 - 0.2 * difficulty  # Make stones smaller with increased difficulty
    stone_width = 0.6 - 0.2 * difficulty  # Ensure the robot has to be precise
    stone_length = m_to_idx(stone_length)
    stone_width = m_to_idx(stone_width)
    stone_height_min, stone_height_max = 0.1 + 0.2 * difficulty, 0.2 + 0.3 * difficulty
    gap_distance = 0.4 + 0.5 * difficulty  # Increase gaps with difficulty
    gap_distance = m_to_idx(gap_distance)

    mid_y = m_to_idx(width) // 2

    def add_stepping_stone(x, y):
        x1, x2 = x, x + stone_length
        y1, y2 = y - stone_width // 2, y + stone_width // 2
        stone_height = np.random.uniform(stone_height_min, stone_height_max)
        height_field[x1:x2, y1:y2] = stone_height

    # Initialize the spawning area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    
    # First goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(7):  # Create 7 stepping stones
        add_stepping_stone(cur_x, mid_y)
        
        # Set intermediate goals on each stepping stone
        goals[i+1] = [cur_x + stone_length // 2, mid_y]
        
        # Move to the next stone position, factoring in the gap
        cur_x += stone_length + gap_distance
    
    # Final goal position
    goals[7] = [cur_x - gap_distance + m_to_idx(0.3), mid_y]

    return height_field, goals

def set_terrain_3(length, width, field_resolution, difficulty):
    """Raised platforms and stepping stones with jumping gaps to challenge the quadruped's agility and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform and step dimensions
    platform_length_min, platform_length_max = 0.5, 1.0
    platform_width_min, platform_width_max = 0.8, 1.2
    platform_height_min, platform_height_max = 0.15, 0.3
    gap_length_min, gap_length_max = 0.3, 0.7

    platform_length = [np.random.uniform(platform_length_min, platform_length_max) for _ in range(6)]
    platform_width = [np.random.uniform(platform_width_min, platform_width_max) for _ in range(6)]
    platform_height = [np.random.uniform(platform_height_min, platform_height_max) for _ in range(6)]
    gap_length = [np.random.uniform(gap_length_min, gap_length_max) * difficulty for _ in range(5)]
    
    platform_length = m_to_idx(platform_length)
    platform_width = m_to_idx(platform_width)
    platform_height = np.array(platform_height) * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, width, height):
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    # Clear spawn area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal near spawn

    cur_x = spawn_length

    for i in range(6):
        # Adding raised platform
        add_platform(cur_x, cur_x + platform_length[i], mid_y, platform_width[i], platform_height[i])
        goals[i+1] = [cur_x + platform_length[i] // 2, mid_y]  # Central goal on the platform

        cur_x += platform_length[i] + (gap_length[i-1] if i > 0 else 0)

        if i < 5:
            # Gap preparation
            height_field[cur_x:cur_x + gap_length[i], :] = -0.1 * difficulty  # Small gaps relative to difficulty factor

    # Add final goal near the end of the terrain
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_4(length, width, field_resolution, difficulty):
    """Inclined ramps and varied platforms designed for advanced maneuvering and climbing skills of the quadruped."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions
    platform_length = 0.7 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.2)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.2 + 0.3 * difficulty
    gap_length = 0.3 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    # Set up ramp dimensions
    ramp_length = 0.8 + 0.3 * difficulty
    ramp_length = m_to_idx(ramp_length)
    ramp_height_min, ramp_height_max = 0.2 + 0.3 * difficulty, 0.3 + 0.4 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_ramp(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        for i in range(x1, x2):
            height_field[i, y1:y2] = np.linspace(0, height, y2-y1)
        
    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # Initial goal

    # Initialize the sequence of platforms and ramps
    cur_x = spawn_length
    alternating_ramps = [i % 2 == 0 for i in range(1, 7)]

    for i in range(1, 7): 
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        if alternating_ramps[i - 1]:
            add_ramp(cur_x, cur_x + ramp_length + dx, mid_y + dy, np.random.uniform(ramp_height_min, ramp_height_max))
            goals[i] = [cur_x + ramp_length // 2, mid_y + dy]
            cur_x += ramp_length + dx + gap_length
        else:
            platform_height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height)
            goals[i] = [cur_x + platform_length // 2, mid_y + dy]
            cur_x += platform_length + dx + gap_length
    
    # Add final goal behind the last obstacle
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_5(length, width, field_resolution, difficulty):
    """Narrow bridges and balancing beams for the robot to walk and balance across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up bridge and beam dimensions
    min_beam_width = 0.4
    max_beam_width = 1.0 - difficulty * 0.6
    min_gap_length = 0.2
    max_gap_length = 0.5
    beam_height = 0.2 + difficulty * 0.3

    mid_y = m_to_idx(width) // 2

    def add_balancing_beam(start_x, end_x, mid_y, beam_width):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
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
    for i in range(6):  # Set up 6 balancing beams
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        beam_width = np.random.uniform(min_beam_width, max_beam_width)
        beam_length = 1.0
        beam_length = m_to_idx(beam_length)
        gap_length = np.random.uniform(min_gap_length, max_gap_length)
        gap_length = m_to_idx(gap_length)

        add_balancing_beam(cur_x, cur_x + beam_length + dx, mid_y + dy, m_to_idx(beam_width))

        # Put goal in the center of the beam
        goals[i+1] = [cur_x + (beam_length + dx) // 2, mid_y + dy]

        # Add gap
        cur_x += beam_length + dx + gap_length
    
    # Add final goal behind the last balancing beam, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_6(length, width, field_resolution, difficulty):
    """Narrow balance beams requiring careful navigation."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up balance beam dimensions
    # Beam height slightly increases with difficulty
    beam_length = 1.8 - 0.5 * difficulty
    beam_length = m_to_idx(beam_length)
    beam_width_min, beam_width_max = 0.1, 0.3  # Width of 10cm to 30cm
    beam_height_min, beam_height_max = 0.1 + 0.1 * difficulty, 0.3 + 0.2 * difficulty
    
    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, mid_y):
        beam_width = np.random.uniform(beam_width_min, beam_width_max)
        half_width = m_to_idx(beam_width / 2)
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        beam_height = np.random.uniform(beam_height_min, beam_height_max)
        height_field[x1:x2, y1:y2] = beam_height

    dx_min, dx_max = 0.1, 0.3
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at spawn

    cur_x = spawn_length
    for i in range(6):  # Set up 6 balance beams
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        add_beam(cur_x, cur_x + beam_length + dx, mid_y + dy)

        # Put goal at the end of each beam
        goals[i+1] = [cur_x + (beam_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += beam_length + dx

    # Add final goal after the last beam
    goals[-1] = [cur_x + dx_min, mid_y]
    height_field[cur_x:, :] = 0  # Fill final section with flat ground

    return height_field, goals

def set_terrain_7(length, width, field_resolution, difficulty):
    """Obstacle course featuring balance beams and narrow pathways for the robot to traverse."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Balance beam dimensions
    beam_length = 2.0
    beam_width = 0.4 - difficulty * 0.2
    beam_height = 0.05 + difficulty * 0.2
    
    beam_length_idx = m_to_idx(beam_length)
    beam_width_idx = m_to_idx(beam_width)
    beam_height_value = 0.2 + difficulty * 0.3

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, beam_width_idx):
        mid_y_offset = np.random.randint(-m_to_idx(0.5), m_to_idx(0.5))
        beam_mid_y = mid_y + mid_y_offset
        half_width = beam_width_idx // 2
        height_field[start_x:start_x + beam_length_idx, beam_mid_y - half_width:beam_mid_y + half_width] = beam_height_value
        return beam_mid_y

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [1, mid_y]  # First goal at the spawn

    cur_x = spawn_length

    # Place balance beams and goals
    for i in range(6):
        beam_y = add_beam(cur_x, beam_width_idx)
        goals[i+1] = [cur_x + beam_length_idx // 2, beam_y]
        # Update x position for the next beam, including gaps proportional to the difficulty
        cur_x += beam_length_idx + m_to_idx(0.5 + 0.5 * difficulty)

    # Final goal past the last beam
    goals[-1] = [cur_x + m_to_idx(1), mid_y]  # 1 meter past the last beam
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_8(length, width, field_resolution, difficulty):
    """Step platforms, narrow beams, and ramps traversing a pit for the robot to climb and navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define obstacle sizes relative to the difficulty
    step_length = 0.5 - 0.1 * difficulty
    step_length = m_to_idx(step_length)
    step_width = 0.5 - 0.1 * difficulty
    step_width = m_to_idx(step_width)
    step_height_min, step_height_max = 0.05 + 0.15 * difficulty, 0.1 + 0.2 * difficulty
    
    beam_length = 1.0 - 0.2 * difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = 0.3 - 0.1 * difficulty
    beam_width = m_to_idx(beam_width)
    beam_height_min, beam_height_max = 0.1 + 0.2 * difficulty, 0.2 + 0.25 * difficulty

    ramp_length = 1.2 - 0.2 * difficulty
    ramp_length = m_to_idx(ramp_length)
    ramp_width = 1.0 - 0.3 * difficulty
    ramp_width = m_to_idx(ramp_width)
    ramp_height_min, ramp_height_max = 0.1 + 0.3 * difficulty, 0.15 + 0.4 * difficulty

    gap_length = 0.1 + 0.3 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_step(start_x, end_x, mid_y):
        half_width = step_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        step_height = np.random.uniform(step_height_min, step_height_max)
        height_field[x1:x2, y1:y2] = step_height

    def add_beam(start_x, end_x, mid_y):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        beam_height = np.random.uniform(beam_height_min, beam_height_max)
        height_field[x1:x2, y1:y2] = beam_height

    def add_ramp(start_x, end_x, mid_y):
        half_width = ramp_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        slope = np.linspace(0, ramp_height, x2 - x1)
        height_field[x1:x2, y1:y2] = slope[:, None]

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length

    # Create steps
    num_steps = 3
    for _ in range(num_steps):
        add_step(cur_x, cur_x + step_length, mid_y)
        goals[_ + 1] = [cur_x + step_length // 2, mid_y]
        cur_x += step_length + gap_length
    
    # Create narrow beams
    num_beams = 2
    for i in range(num_beams):
        add_beam(cur_x, cur_x + beam_length, mid_y)
        goals[num_steps + i + 1] = [cur_x + beam_length // 2, mid_y]
        cur_x += beam_length + gap_length

    # Create ramps
    num_ramps = 2
    for i in range(num_ramps):
        add_ramp(cur_x, cur_x + ramp_length, mid_y)
        goals[num_steps + num_beams + i + 1] = [cur_x + ramp_length // 2, mid_y]
        cur_x += ramp_length + gap_length

    # Fill in remaining gap for final goal
    goals[-1] = [cur_x - gap_length // 2, mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_9(length, width, field_resolution, difficulty):
    """Tilted platforms and raised pathways with variable width gaps to challenge balance and navigation skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Dimensions and heights for platforms and pathways
    platform_length = 0.8 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.2)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.1 * difficulty, 0.2 + 0.2 * difficulty

    path_width = m_to_idx(1.0 - 0.3 * difficulty)
    gap_length_min, gap_length_max = 0.2 + 0.4 * difficulty, 0.4 + 0.5 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, tilt=False):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        if tilt:
            platform_heights = np.linspace(platform_height, platform_height / 2, y2 - y1)
            height_field[x1:x2, y1:y2] = platform_heights
        else:
            height_field[x1:x2, y1:y2] = platform_height
    
    def add_pathway(start_x, end_x, mid_y, guard_rails=True):
        half_width = path_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = 0.1 + 0.2 * difficulty
        if guard_rails:
            guard_height = 0.05 + 0.1 * difficulty
            height_field[x1:x2, y1:y1+1] = guard_height
            height_field[x1:x2, y2-1:y2] = guard_height

    dx_min, dx_max = -0.2, 0.3
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
        gap_length = np.random.uniform(gap_length_min, gap_length_max)
        gap_length_idx = m_to_idx(gap_length)
        
        if i % 2 == 0:
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, tilt=True)
            goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        else:
            add_pathway(cur_x, cur_x + platform_length, mid_y)
            goals[i+1] = [cur_x + platform_length / 2, mid_y]

        cur_x += platform_length + gap_length_idx + dx if i % 2 == 0 else platform_length + gap_length_idx
    
    # Add final goal behind the last obstacle, filling remaining gap as flat
    final_gap_length = m_to_idx(1)  # A small gap length
    goals[-1] = [cur_x + final_gap_length, mid_y]
    height_field[cur_x + final_gap_length:, :] = 0.2 + 0.3 * difficulty

    return height_field, goals

# INSERT TERRAIN FUNCTION DEFINITIONS HERE
