import numpy as np
from isaacgym import terrain_utils

difficulty_scaling = {
    "jump_on_and_off_box": (0.1, 0.8),
    "forward_ramp_lips": (0.6, 1),
    "sphere_bump_lips": (0.2, 1.1),
    "forward_ramp_no_lips": (0.4, 0.8),
    "flush_a_frame": (0.55, 0.9),
    "sphere_bump": (0.3, 1),
    "box_jump_even": (0.1, 0.7),
    "box_jump_uneven": (0, 1),
    "flat_circle_jump": (0, 1),
    "bump_jump": (0, 0.8),

    "sideways_ramp": (0.4, 1.1),
    "stepping_stones_cylinder": (-0.2, 1.1),
    "stepping_stones_randomly_arranged": (0.3, 0.5),
    "staircase_walking_full_width": (0.1, 0.9),
    "staircase_walking": (0, 1.2),
    "staircase_climbing": (0.5, 1),
    "staircase_spiral": (0, 1),
    "squeeze": (0, 1),
    "agility_poles": (0, 1),
    "balance_beam": (0.5, 1),
}

def set_terrain(terrain, variation, difficulty):
    terrain_fns = [
        # Climbing
        set_terrain_jump_on_and_off_box,
        set_terrain_forward_ramp_lips, 
        set_terrain_sphere_bump_lips,
        # Slope
        set_terrain_forward_ramp_no_lips,
        set_terrain_flush_a_frame,
        set_terrain_sphere_bump,
        # Jumping
        set_terrain_box_jump_even,
        set_terrain_box_jump_uneven,
        set_terrain_flat_circle_jump,
        set_terrain_bump_jump,
        set_terrain_sideways_ramp,  # Idx 10
        # Stepping stones
        set_terrain_stepping_stones_cylinder,
        set_terrain_stepping_stones_randomly_arranged,
        # Staircase
        set_terrain_staircase_walking_full_width,
        set_terrain_staircase_walking,
        set_terrain_staircase_climbing,  # Idx 15
        set_terrain_staircase_spiral,
        # Misc
        set_terrain_squeeze, 
        set_terrain_agility_poles,
        set_terrain_balance_beam,
    ]
    idx = int(variation * len(terrain_fns))
    # GPT-generated terrains have a different signature
    height_field, goals = terrain_fns[idx](terrain.width * terrain.horizontal_scale, terrain.length * terrain.horizontal_scale, terrain.horizontal_scale, difficulty)
    terrain.height_field_raw = (height_field / terrain.vertical_scale).astype(np.int16)
    terrain.goals = goals.astype(np.float64) * terrain.horizontal_scale
    return idx

def scale_difficulty(difficulty, min_d, max_d):
    return difficulty * (max_d - min_d) + min_d
    # return difficulty

def set_terrain_forward_ramp_lips(length, width, field_resolution, difficulty):
    """Multiple ramp platforms that go from the ground to a height, with a random nonzero start lip height at higher difficulties"""
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    # difficulty = scale_difficulty(difficulty, 0.5, 0.8)
    # difficulty = scale_difficulty(difficulty, 0.6, 1)
    difficulty = scale_difficulty(difficulty, *difficulty_scaling["forward_ramp_lips"])
    # Set up platform dimensions
    # We make the platform height near 0 at minimum difficulty so the quadruped can learn to climb up
    platform_length = 1.2 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 2.0)
    platform_width = m_to_idx(platform_width)
    start_height_min, start_height_max = 0.1 + 0.2 * difficulty, 0.15 + 0.2 * difficulty
    platform_height_min, platform_height_max = 0.03 + 0.25 * difficulty, 0.05 + 0.3 * difficulty
    
    gap_length = 0.7 + 0.3 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_ramp(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        max_platform_height = np.random.uniform(platform_height_min, platform_height_max)
        start_height = np.random.uniform(start_height_min, start_height_max)
        for delta in range(x2 - x1):
            height_field[x1 + delta, y1:y2] = start_height + max_platform_height * (delta/(x2-x1))

    dx_min, dx_max = -0.3, 0.3
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.1, 0.1
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    for i in range(6):  # Set up 6 platforms
        dx = np.random.uniform(dx_min, dx_max)
        dy = np.random.uniform(dy_min, dy_max)
        add_ramp(cur_x, int(cur_x + platform_length + dx), int(mid_y + dy))

        # Put goal in the center of the platform
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += int(platform_length + dx + gap_length)
    
    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_forward_ramp_no_lips(length, width, field_resolution, difficulty):
    """Multiple ramp platforms that go from the ground to a height"""
    # difficulty = scale_difficulty(difficulty, 0.3, 0.6)

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    # difficulty = scale_difficulty(difficulty, 0.4, 1.2)
    # difficulty = scale_difficulty(difficulty, 0.4, 0.8)
    difficulty = scale_difficulty(difficulty, *difficulty_scaling["forward_ramp_no_lips"])

    # Set up platform dimensions
    # We make the platform height near 0 at minimum difficulty so the quadruped can learn to climb up
    platform_length = 1.2 - 0.5 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 1.5 - 0.5 * difficulty
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.5 * difficulty, 0.2 + 0.6 * difficulty
    gap_length = 0.1 + 0.7 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_ramp(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        max_platform_height = np.random.uniform(platform_height_min, platform_height_max)
        for delta in range(x2 - x1):
            height_field[x1 + delta, y1:y2] = max_platform_height * (delta/(x2-x1))

    dx_min, dx_max = -0.2, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.1, 0.1
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    for i in range(6):  # Set up 6 platforms
        dx = np.random.uniform(dx_min, dx_max)
        dy = np.random.uniform(dy_min, dy_max)
        add_ramp(cur_x, int(cur_x + platform_length + dx), int(mid_y + dy))

        # Put goal in the center of the platform
        goals[i+1] = [cur_x + (platform_length + dx) // 2, mid_y + dy]

        # Add gap
        cur_x += int(platform_length + dx + gap_length)
    
    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_sideways_ramp(length, width, field_resolution, difficulty):
    """Multiple ramp platforms that go sideways"""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    # difficulty = scale_difficulty(difficulty, 0.3, 0.8)
    # difficulty = scale_difficulty(difficulty, 0.4, 1.0)
    # difficulty = scale_difficulty(difficulty, 0.4, 1.1)
    # difficulty = scale_difficulty(difficulty, 0.4, 1.3)
    difficulty = scale_difficulty(difficulty, *difficulty_scaling["sideways_ramp"])
    # Set up platform dimensions
    # We make the platform height near 0 at minimum difficulty so the quadruped can learn to climb up
    platform_length = 1.2 - 0.5 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.0 + 0.1*difficulty)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.05 + 0.25 * difficulty, 0.05 + 0.5 * difficulty
    gap_length = 0.1 + 0.65 * difficulty
    gap_length = m_to_idx(gap_length)
    y_offset = -0.5
    y_offset = m_to_idx(y_offset)

    mid_y = m_to_idx(width) // 2

    def add_ramp(start_x, end_x, mid_y, to_left):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        max_platform_height = np.random.uniform(platform_height_min, platform_height_max)
        diff = y2 - y1
        if to_left:
            for delta in range(diff):
                height_field[x1:x2, y1+delta] = max_platform_height * ((diff - delta)/diff)
        else: 
            for delta in range(diff):
                height_field[x1:x2, y2-delta] = max_platform_height * ((diff - delta)/diff)
    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.1, 0.1
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
    for i in range(6):  # Set up 6 platforms
        dx = np.random.uniform(dx_min, dx_max)
        dy = np.random.uniform(dy_min, dy_max)
        direction = np.random.uniform(0, 1) > 0.5
        add_ramp(cur_x, int(cur_x + platform_length + dx), int(mid_y + direction * y_offset + dy), direction)

        # Put goal in the center of the platform
        goals[i+1] = [cur_x + (platform_length + dx) / 2, int(mid_y + direction * y_offset + dy)]

        # Add gap
        cur_x += int(platform_length + dx + gap_length)
    
    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_flush_a_frame(length, width, field_resolution, difficulty):
    """A frame platforms, comprised of an adjacent forward and backward ramp"""
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    # difficulty = scale_difficulty(difficulty, 0.4, 0.6)   
    # difficulty = scale_difficulty(difficulty, 0.5, 0.7) 
    # difficulty = scale_difficulty(difficulty, 0.5, 1.2) 
    # difficulty = scale_difficulty(difficulty, 0.53, 0.7) 
    difficulty = scale_difficulty(difficulty, *difficulty_scaling["flush_a_frame"])
    # Set up platform dimensions
    # We make the platform height near 0 at minimum difficulty so the quadruped can learn to climb up
    platform_length = 1.0 - 0.4 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 1.5 - 0.5 * difficulty
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.6 * difficulty, 0.15 + 0.6 * difficulty
    start_height_min, start_height_max = 0.01 + 0.05 * difficulty, 0.03 + 0.03 * difficulty
    gap_length = 0.1 + 0.7 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_forward_ramp(start_x, end_x, mid_y, max_platform_height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        
        start_height = np.random.uniform(start_height_min, start_height_max)
        for delta in range(x2 - x1):
            height_field[x1 + delta, y1:y2] = start_height + max_platform_height * (delta/(x2-x1))

    def add_backward_ramp(start_x, end_x, mid_y, max_platform_height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        start_height = np.random.uniform(start_height_min, start_height_max)
        for delta in range(x2 - x1):
            height_field[x1 + delta, y1:y2] = max_platform_height - (max_platform_height - start_height) * (delta/(x2-x1))

    dx_min, dx_max = -0.2, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.1, 0.1
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    for i in range(6):  # Set up 6 platforms
        dx = np.random.uniform(dx_min, dx_max)
        dy = np.random.uniform(dy_min, dy_max)
        max_platform_height = np.random.uniform(platform_height_min, platform_height_max)
        add_forward_ramp(cur_x, int(cur_x + platform_length + dx), int(mid_y + dy), max_platform_height)
        cur_x += int(platform_length + dx)
        add_backward_ramp(cur_x, int(cur_x + platform_length + dx), int(mid_y + dy), max_platform_height)

        # Put goal in the center of the a frame
        goals[i+1] = [cur_x, mid_y + dy]

        # Add gap
        cur_x += int(platform_length + dx + gap_length)
    
    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_jump_on_and_off_box(length, width, field_resolution, difficulty):
    """Multiple ramp platforms that go from the ground to a height"""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    # difficulty = scale_difficulty(difficulty, 0.6, 0.9)
    # difficulty = scale_difficulty(difficulty, 0.8, 0.9)
    difficulty = scale_difficulty(difficulty, *difficulty_scaling["jump_on_and_off_box"])

    # Set up platform dimensions
    # We make the platform height near 0 at minimum difficulty so the quadruped can learn to climb up
    platform_length = 1.2 - 0.25 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 2.0)
    platform_width = m_to_idx(platform_width)
    # platform_height_min, platform_height_max = 0.1 + 0.45 * difficulty, 0.2 + 0.5 * difficulty
    platform_height_min, platform_height_max = 0.1 + 0.55 * difficulty, 0.15 + 0.55 * difficulty
    platform_height_inc = 0.05
    gap_length = 1.5 - 0.3 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, platform_height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        for delta in range(x2 - x1):
            height_field[x1 + delta, y1:y2] = platform_height

    dx_min, dx_max = -0.2, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.1, 0.1
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    for i in range(6):  # Set up 6 platforms
        dx = np.random.uniform(dx_min, dx_max)
        dy = np.random.uniform(dy_min, dy_max)
        platform_height = np.random.uniform(platform_height_min, platform_height_max) + platform_height_inc * i
        add_platform(cur_x, int(cur_x + platform_length + dx), int(mid_y + dy), platform_height)

        # Put goal in the center of the platform
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += int(platform_length + dx + gap_length)
    
    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_box_jump_even(length, width, field_resolution, difficulty):
    """Even box platforms that the robot jumps across"""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    # difficulty = scale_difficulty(difficulty, 0.1, 0.5)
    # difficulty = scale_difficulty(difficulty, 0.1, 0.7)
    difficulty = scale_difficulty(difficulty, *difficulty_scaling["box_jump_even"])
    
    # Set up platform dimensions
    # We make the platform height near 0 at minimum difficulty so the quadruped can learn to climb up
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.0 + 0.1*difficulty)
    platform_width = m_to_idx(platform_width)
    platform_height = 0
    gap_length_min, gap_length_max =  0.4 + 0.5 * difficulty, 0.5 + 0.5 * difficulty
    gap_length_min, gap_length_max = m_to_idx(gap_length_min), m_to_idx(gap_length_max)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = int(start_x), int(end_x)
        y1, y2 = int(mid_y - half_width), int(mid_y + half_width)
        height_field[x1:x2, y1:y2] = platform_height
    
    dx_min, dx_max = -0.2, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.1, 0.1
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
    for i in range(6):  # Set up 6 platforms
        dx = np.random.uniform(dx_min, dx_max)
        dy = np.random.uniform(dy_min, dy_max)
        add_platform(cur_x, int(cur_x + platform_length + dx), int(mid_y + dy))

        # Put goal in the center of the platform
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        gap_length = np.random.uniform(gap_length_min, gap_length_max)
        # Add gap
        cur_x += int(platform_length + dx + gap_length)
    
    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_box_jump_uneven(length, width, field_resolution, difficulty):
    """Uneven box platforms that the robot jumps across"""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    difficulty = scale_difficulty(difficulty, *difficulty_scaling["box_jump_uneven"])

    # Set up platform dimensions
    platform_length = 1.2 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.0 + 0.1*difficulty)
    platform_width = m_to_idx(platform_width)
    min_height_change, max_height_change = 0.01 + 0.2 * difficulty, 0.02 + 0.25 * difficulty
    gap_length_min, gap_length_max =  0.4 + 0.3 * difficulty, 0.5 + 0.4 * difficulty
    gap_length_min, gap_length_max = m_to_idx(gap_length_min), m_to_idx(gap_length_max)

    mid_y = m_to_idx(width) // 2
    last_height = 0

    def add_platform(start_x, end_x, mid_y, platform_height):
        half_width = platform_width // 2
        x1, x2 = int(start_x), int(end_x)
        y1, y2 = int(mid_y - half_width), int(mid_y + half_width)
        height_field[x1:x2, y1:y2] = platform_height
    
    dx_min, dx_max = -0.3, 0.3
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.1, 0.1
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
    for i in range(6):  # Set up 6 platforms
        dx = np.random.uniform(dx_min, dx_max)
        dy = np.random.uniform(dy_min, dy_max)
        height_change = np.random.uniform(min_height_change, max_height_change)
        if last_height - height_change > 0: 
            direction = 1 if np.random.uniform(0, 1) > 0.5 else -1
        else:
            direction = 1
        last_height += direction * height_change
        add_platform(cur_x, int(cur_x + platform_length + dx), int(mid_y + dy), last_height)

        # Put goal in the center of the platform
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        gap_length = np.random.uniform(gap_length_min, gap_length_max)
        # Add gap
        cur_x += int(platform_length + dx + gap_length)
        
    
    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = last_height

    return height_field, goals

def set_terrain_stepping_stones_flat(length, width, field_resolution, difficulty):
    """Flat stepping stone platforms that the robot steps along"""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    difficulty = scale_difficulty(difficulty, *difficulty_scaling["stepping_stones_flat"])


    # Set up platform dimensions
    platform_length = 0.8 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 0.55 - 0.2 * difficulty
    platform_width = m_to_idx(platform_width)
    platform_height = 0
    gap_length_min, gap_length_max =  0.05 + 0.05 * difficulty, 0.1 + 0.07 * difficulty
    gap_length_min, gap_length_max = m_to_idx(gap_length_min), m_to_idx(gap_length_max)

    mid_y = m_to_idx(width) // 2

    def add_stone(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = int(start_x), int(end_x)
        y1, y2 = int(mid_y - half_width), int(mid_y + half_width)
        height_field[x1:x2, y1:y2] = platform_height
    
    # Vary this with difficulty
    dy_min, dy_max = 0.15 + 0.1 * difficulty, 0.2 + 0.1 * difficulty
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
    direction = 1

    goal_indices = []
    for i in range(6):
        if np.random.uniform(0, 1) > 0.5: 
            goal_indices.append(2 * i)
        else:
            goal_indices.append(2 * i + 1)

    for i in range(12):  # Set up 12 platforms
        dy = np.random.randint(dy_min, dy_max)
        # Flip between left and right
        direction *= -1
        add_stone(cur_x, cur_x + platform_length, mid_y + direction * dy)

        # Put goal in the center of the platform
        gap_length = np.random.uniform(gap_length_min, gap_length_max)

        if i in goal_indices:
            goals[i // 2 + 1] = [cur_x + (platform_length) / 2, mid_y + direction * dy]

        if i % 2 == 0:
            cur_x += int(gap_length) 
        else: 
            cur_x += int(platform_length + 0.2 * gap_length)
    
    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_stepping_stones_cylinder(length, width, field_resolution, difficulty):
    """Uneven stepping stone cylinders that the robot steps along"""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]
    
    # difficulty = scale_difficulty(difficulty, 0.1, 1.1)
    # difficulty = scale_difficulty(difficulty, 0.2, 1.3)
    # difficulty = scale_difficulty(difficulty, 0.2, 1.3)
    # difficulty = scale_difficulty(difficulty, -0.1, 0.8)
    difficulty = scale_difficulty(difficulty, *difficulty_scaling["stepping_stones_cylinder"])


    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions
    
    platform_height_min, platform_height_max = 0, 0.07*difficulty
    gap_length_min, gap_length_max =  0.05 + 0.05 * difficulty, 0.1 + 0.07 * difficulty
    gap_length_min, gap_length_max = m_to_idx(gap_length_min), m_to_idx(gap_length_max)

    mid_y = m_to_idx(width) // 2
    radius = 7 - 3.5 * difficulty
   
    def draw_cylinder(mid_x, mid_y):
        x, y = np.ogrid[:m_to_idx(length), :m_to_idx(width)]
        distance = np.sqrt((x - mid_x)**2 + (y - mid_y)**2)
        mask = distance <= radius
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[mask] = platform_height

    # Vary this with difficulty
    # dy_min, dy_max = 0.15 - 0.1 * difficulty, 0.2 - 0.1 * difficulty
    dy_min, dy_max = 0.15 - 0.05 * difficulty, 0.2 - 0.05 * difficulty
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # goal_indices = []
    # for i in range(6):
    #     if np.random.uniform(0, 1) > 0.5: 
    #         goal_indices.append(2 * i)
    #     else:
    #         goal_indices.append(2 * i + 1)

    # Set remaining area to be a pit
    # We do this to force the robot to jump from platform to platform
    # Otherwise, the robot can just jump down and climb back up
    height_field[spawn_length:, :] = -1.0

    cur_x = int(spawn_length + radius / 2)
    direction = 1
    cur_y = mid_y
    for i in range(12):  # Set up 12 platforms
        dy = np.random.randint(dy_min, dy_max)
        # Flip between left and right
        direction *= -1
        draw_cylinder(cur_x + radius / 2, cur_y + direction * dy)

        # Put goal in the center of the platform
        gap_length = np.random.uniform(gap_length_min, gap_length_max)

        # if i in goal_indices:
        #     goals[i // 2 + 1] = [cur_x + (radius) / 2, cur_y + direction * dy]
        if i % 2 == 0:
            cur_x += int(gap_length + radius / 3) 
            goals[i // 2 + 1] = [cur_x, cur_y + radius / 2]
            cur_y += radius
        else: 
            cur_x += int(1.5 * gap_length + radius)
            cur_y = mid_y
    
    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_stepping_stones_randomly_arranged(length, width, field_resolution, difficulty):
    """Randomly distributed stepping stone platforms that the robot steps along"""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    # difficulty = scale_difficulty(difficulty, 0.4, 0.9)
    # difficulty = scale_difficulty(difficulty, 0.4, 1.1)
    # difficulty = scale_difficulty(difficulty, 0.4, 1.3)
    # difficulty = scale_difficulty(difficulty, 0.1, 0.7)
    difficulty = scale_difficulty(difficulty, *difficulty_scaling["stepping_stones_randomly_arranged"])

    # Set up platform dimensions
    platform_length = 0.7 - 0.55 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 0.6 - 0.3 * difficulty
    platform_width = m_to_idx(platform_width)
    platform_height = 0
    gap_length_min, gap_length_max =  0.05 + 0.1 * difficulty, 0.1 + 0.2 * difficulty
    gap_length_min, gap_length_max = m_to_idx(gap_length_min), m_to_idx(gap_length_max)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y,):
        half_width = platform_width // 2
        x1, x2 = int(start_x), int(end_x)
        y1, y2 = int(mid_y - half_width), int(mid_y + half_width)
        height_field[x1:x2, y1:y2] = platform_height
    
    # Vary this with difficulty
    # dy_min, dy_max = 0.05 + 0.05 * difficulty, 0.07 + 0.08 * difficulty
    dy_min, dy_max = 0.03 + 0.04 * difficulty, 0.05 + 0.08 * difficulty
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)
    dy_inc = 0.02

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
    cur_y = mid_y
    direction = 1
    
    max_gap_width = 0.25 + 0.2 * difficulty
    max_gap_width = m_to_idx(max_gap_width) 

    for i in range(12):  # Set up 12 platforms
        dy = min(np.random.uniform(dy_min, dy_max), m_to_idx(width))
        # Flip between left and right
        direction *= -1
        y_change = direction * dy
        if cur_y + y_change < platform_width or cur_y + y_change > m_to_idx(width) - platform_width * 2:
            cur_y -= int(1.5 * y_change)
            y_change *= 0
        add_platform(cur_x, cur_x + platform_length, cur_y + y_change)

        # Put goal in the center of the platform
        gap_length = np.random.uniform(gap_length_min, gap_length_max)



        
            
        if i % 2 == 0: 
            old_x, old_y = cur_x, cur_y
            
            cur_x += int(gap_length) 
            y_change = min(platform_width * (difficulty + 1.5) / 2, max_gap_width)
            cur_y += y_change
            if cur_y < platform_width * 1.5 or cur_y > m_to_idx(width) - platform_width * 1.5:
                # cur_y += -0.7 *  platform_width 
                y_change += -0.7 *  platform_width 
            goals[(i // 2) + 1] = [old_x + int(gap_length) / 2, old_y + y_change / 2]
        else: 
            cur_x += int(platform_length + 0.2 * gap_length)
            y_shift = 1 if np.random.uniform(0, 1) > 0.5 else -1
            y_change = y_shift * np.random.uniform(dy_min, dy_max) + dy_inc * i
            cur_y = mid_y + y_change
            if cur_y < platform_width * 3 or cur_y > m_to_idx(width) - platform_width * 2:
                cur_y += -1.5 * y_change

    
    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_staircase_walking_full_width(length, width, field_resolution, difficulty):
    """Staircase that the robot walks up"""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]
    
    # difficulty = scale_difficulty(difficulty, 0.5, 1.5)
    # difficulty = scale_difficulty(difficulty, 1.0, 2.0)
    difficulty = scale_difficulty(difficulty, *difficulty_scaling["staircase_walking_full_width"])


    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    # Set up platform dimensions
    # platform_length = 0.5 - 0.05 * difficulty
    platform_length = 0.25 - 0.1 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = width
    platform_width = m_to_idx(platform_width)
    dz_min, dz_max = 0.05 + 0.1*difficulty, 0.07 + 0.15*difficulty
    z_inc = 0.05

    mid_y = m_to_idx(width) // 2

    def add_step(start_x, end_x, mid_y, platform_height):
        half_width = platform_width // 2
        x1, x2 = int(start_x), int(end_x)
        y1, y2 = int(mid_y - half_width), int(mid_y + half_width)
        
        height_field[x1:x2, y1:y2] = platform_height
    
    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn 
    

    # Set remaining area to be a pit
    # We do this to force the robot to jump from platform to platform
    # Otherwise, the robot can just jump down and climb back up
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    cur_height = 0
    
    direction = -1
    num_staircases = 5
    num_steps = 6

    counter = 0
    for i in range(num_staircases):
        direction *= -1
        for j in range(num_steps):  # Set up 6 platforms
            dz = np.random.uniform(dz_min, dz_max) + z_inc * (i // 2)
            cur_height += direction * dz
            add_step(cur_x, cur_x + platform_length, mid_y, cur_height)
            cur_x += int(platform_length) 
            counter += 1
        add_step(cur_x, cur_x + platform_length * 5, mid_y, cur_height)
        cur_x += int(platform_length * 5)

    goals[:, 0] = np.linspace(m_to_idx(2), cur_x, 8)
    goals[:, 1] = m_to_idx(width) // 2
    height_field[cur_x:, :] = cur_height

    return height_field, goals

def set_terrain_staircase_walking(length, width, field_resolution, difficulty):
    """Staircase that the robot walks up"""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]
    
    # difficulty = scale_difficulty(difficulty, 0.0, 1.2)
    difficulty = scale_difficulty(difficulty, *difficulty_scaling["staircase_walking"])


    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions
    platform_length = 0.5 - 0.05 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 1.0 - 0.45 * difficulty
    platform_width = m_to_idx(platform_width)
    dz_min, dz_max = 0.05 + 0.1*difficulty, 0.07 + 0.15*difficulty

    mid_y = m_to_idx(width) // 2

    def add_step(start_x, end_x, mid_y, platform_height):
        half_width = platform_width // 2
        x1, x2 = int(start_x), int(end_x)
        y1, y2 = int(mid_y - half_width), int(mid_y + half_width)
        
        height_field[x1:x2, y1:y2] = platform_height
    
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
    cur_height = 0
    for i in range(6):  # Set up 6 platforms
        dz = np.random.uniform(dz_min, dz_max)
        cur_height += dz
        add_step(cur_x, cur_x + platform_length, mid_y, cur_height)

        # Put goal in the center of the platform      
        goals[i + 1] = [cur_x + (platform_length) / 2, mid_y]
        cur_x += int(platform_length) 
    
    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = cur_height

    return height_field, goals
def set_terrain_staircase_climbing(length, width, field_resolution, difficulty):
    """Staircase that the robot climbs up"""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    # difficulty = scale_difficulty(difficulty, 0.5, 0.8)
    # difficulty = scale_difficulty(difficulty, 0.5, 1.0)
    difficulty = scale_difficulty(difficulty, *difficulty_scaling["staircase_climbing"])

    # Set up platform dimensions
    platform_length = 1.5 - 0.1 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 1.5 - 0.4 * difficulty
    platform_width = m_to_idx(platform_width)
    dz_min, dz_max = 0.3 + 0.3*difficulty, 0.4 + 0.3*difficulty

    mid_y = m_to_idx(width) // 2

    def add_step(start_x, end_x, mid_y, platform_height):
        half_width = platform_width // 2
        x1, x2 = int(start_x), int(end_x)
        y1, y2 = int(mid_y - half_width), int(mid_y + half_width)
        
        height_field[x1:x2, y1:y2] = platform_height
    
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
    cur_height = 0
    for i in range(6):  # Set up 6 platforms
        dz = np.random.uniform(dz_min, dz_max)
        cur_height += dz
        add_step(cur_x, cur_x + platform_length, mid_y, cur_height)

        # Put goal in the center of the platform      
        goals[i + 1] = [cur_x + (platform_length) / 2, mid_y]
        cur_x += int(platform_length) 
    
    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = cur_height

    return height_field, goals

def set_terrain_staircase_spiral(length, width, field_resolution, difficulty):
    """Spiral staircase"""
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]



    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions
    # We make the platform height near 0 at minimum difficulty so the quadruped can learn to climb up
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 2.0)
    platform_width = m_to_idx(platform_width)
    gap_length = 0.1 + 0.7 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    
    

    cur_x = spawn_length

    radius = 25
    height_change_min, height_change_max = 0.05 + 0.15 * difficulty, 0.05 + 0.2 * difficulty

    matrix_size = height_field.shape[1]
    mid_x, mid_y = matrix_size // 2, matrix_size // 2
    radius_reduction = 1 - 0.35 * difficulty
    
    # Put first goal right in front of staircase
    goals[0] = [spawn_length * 2 - radius_reduction * 10, mid_y - m_to_idx(0.3)]
    def add_pole(theta_min, theta_max, height, goal_i):

        # Create the meshgrid using np.mgrid with the size of the larger matrix
        x, y = np.mgrid[0:matrix_size, 0:matrix_size]

        # Translate the meshgrid by the center coordinates and normalize to [-radius, radius]
        x = (x - mid_x) / (matrix_size / 2) * radius
        y = (y - mid_y) / (matrix_size / 2) * radius

        # Calculate the distances and angles
        R = np.sqrt(x**2 + y**2)
        Theta = np.arctan2(y, x)


        # Create the matrix for the next 1/6 circle segment
        next_circle_segment = (R <= radius * radius_reduction) & (Theta >= theta_min) & (Theta <= theta_max)

        goal_x, goal_y = np.cos((theta_min + theta_max) / 2) * radius / 2 * 1.5 * radius_reduction, np.sin((theta_min + theta_max) / 2) * radius / 2 * 1.5  * radius_reduction
        goals[goal_i] = [goal_x + mid_x + spawn_length * 2, goal_y + mid_y]
        
        donut = np.concatenate((np.zeros((spawn_length * 2, height_field.shape[1])), next_circle_segment, np.zeros((height_field.shape[0] - spawn_length * 2 - height_field.shape[1], height_field.shape[1])))).astype(np.bool8)
        height_field[donut] = height

    
    height = 0
    for i in range(14):  # Set up 7 platforms
        add_pole(-np.pi + np.pi * i / 7, -np.pi + np.pi * (i + 1) / 7 , height, i // 2 + 1)
        height_change = np.random.uniform(height_change_min, height_change_max)
        height += height_change
    cur_x += m_to_idx(radius) * 4
    
    
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_balance_beam(length, width, field_resolution, difficulty):
    """Balance beam that the robot walks on"""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    # difficulty = scale_difficulty(difficulty, 0.4, 1)
    # difficulty = scale_difficulty(difficulty, 0.6, 1)
    # difficulty = scale_difficulty(difficulty, 0.6, 1.05)
    difficulty = scale_difficulty(difficulty, *difficulty_scaling["balance_beam"])
     
    # Set up platform dimensions
    platform_length = 0.5 + 1.5 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 0.85 - 0.5 * difficulty
    platform_width = m_to_idx(platform_width)
    platform_height = 0

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = int(start_x), int(end_x)
        y1, y2 = int(mid_y - half_width), int(mid_y + half_width)
        
        height_field[x1:x2, y1:y2] = platform_height
    
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
    for i in range(6):  # Set up 6 platforms
        add_platform(cur_x, cur_x + platform_length, mid_y)

        # Put goal in the center of the platform      
        goals[i + 1] = [cur_x + (platform_length) / 2, mid_y]
        cur_x += int(platform_length) 
    
    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_squeeze(length, width, field_resolution, difficulty):
    """Tunnels of decreasing width that the robot squeezes through"""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    # difficulty = scale_difficulty(difficulty, 0.2, 0.6)
    difficulty = scale_difficulty(difficulty, *difficulty_scaling["squeeze"])

    # Set up platform dimensions
    # We make the platform height near 0 at minimum difficulty so the quadruped can learn to climb up
    platform_length = 0.6 + 0.4 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 0.5
    platform_width = m_to_idx(platform_width)
    platform_height = 0.7
    gap_length_min, gap_length_max =  0.4 - 0.1 * difficulty, 0.5 - 0.1 * difficulty
    gap_length_min, gap_length_max = m_to_idx(gap_length_min), m_to_idx(gap_length_max)
    squeeze_width_min, squeeze_width_max = 0.5 - 0.15 * difficulty, 0.6 - 0.15 * difficulty
    squeeze_width_min, squeeze_width_max = m_to_idx(squeeze_width_min), m_to_idx(squeeze_width_max)
    squeeze_change = 0.005 * difficulty  # NEW


    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = int(start_x), int(end_x)
        y1, y2 = int(mid_y - half_width), int(mid_y + half_width)
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
    for i in range(6):  # Set up 6 platforms
        dx = np.random.uniform(dx_min, dx_max)
        dy = np.random.uniform(dy_min, dy_max)
        squeeze_width = np.random.randint(squeeze_width_min, squeeze_width_max) - i * squeeze_change
        add_platform(cur_x, int(cur_x + platform_length + dx), int(mid_y + dy + platform_width // 2 + squeeze_width // 2))
        add_platform(cur_x, int(cur_x + platform_length + dx), int(mid_y + dy - platform_width // 2 - squeeze_width // 2))

        # Put goal in the center of the platform
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        gap_length = np.random.uniform(gap_length_min, gap_length_max)
        # Add gap
        cur_x += int(platform_length + dx + gap_length)
    
    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_agility_poles(length, width, field_resolution, difficulty):
    """
    Creates a set of agility poles that the robot must weave around
    """
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    # difficulty = scale_difficulty(difficulty, -0.5, 1.1)
    difficulty = scale_difficulty(difficulty, *difficulty_scaling["agility_poles"])

    
    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2), dtype=np.int16)
    pole_radius = 3
    pole_height = 1
    distance_between_poles = 2 - 1.15 * difficulty
    distance_between_poles = m_to_idx(distance_between_poles)
    goal_distance = 0.9 - 0.07 * difficulty
    goal_distance = m_to_idx(goal_distance)
   
    
    def add_pole(mid_x, mid_y):
        grid = np.mgrid[:height_field.shape[0], :height_field.shape[1]]
        xx, yy = grid
        circle = (xx - mid_x) ** 2 + (yy - mid_y) ** 2
        donut = circle <= pole_radius ** 2
        height_field[donut] = pole_height
            

    mid_y = m_to_idx(width) // 2
    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  


    cur_x = spawn_length + distance_between_poles

    factor = 1

    for i in range(6):
        add_pole(cur_x, mid_y)
        goals[i + 1] = [cur_x, mid_y + goal_distance * factor]
        factor *= -1
        cur_x += distance_between_poles + 2*pole_radius
    
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    
    return height_field, goals

def set_terrain_sphere_bump(length, width, field_resolution, difficulty):
    """
    Spherical speed bumps that the robot has to climb up
    """
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]
    # difficulty = scale_difficulty(difficulty, 0.4, 0.8)
    # difficulty = scale_difficulty(difficulty, 0.45, 0.75)
    # difficulty = scale_difficulty(difficulty, 0.45, 0.8)
    difficulty = scale_difficulty(difficulty, *difficulty_scaling["sphere_bump"])

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2), dtype=np.int16)
    bump_radius_min, bump_radius_max = 20 - 5.5 * difficulty, 21 - 5.5 * difficulty
    bump_height_min, bump_height_max = 0.2 + 0.4 * difficulty, 0.25 + 0.4 * difficulty
    distance_between_bumps = 0.2 - 0.05 * difficulty
    distance_between_bumps = m_to_idx(distance_between_bumps)
    goal_distance = 0.9 - 0.07 * difficulty
    goal_distance = m_to_idx(goal_distance)
    power = 2 - 0.15 * difficulty
    dx_min, dx_max = -0.4, 0.4
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.9, 0.9
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)
   
    
    def draw_speed_bump(mid_x, mid_y, radius, height):
        x, y = np.ogrid[:m_to_idx(length), :m_to_idx(width)]
        distance = np.sqrt((x - mid_x)**2 + (y - mid_y)**2)
        mask = distance <= radius
        height_field[mask] = height - (distance[mask] / radius) ** power
        height_field[height_field < 0] = 0
            

    mid_y = m_to_idx(width) // 2
    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length + bump_radius_max

    factor = 1

    for i in range(6):
        dx = np.random.uniform(dx_min, dx_max)
        dy = np.random.uniform(dy_min, dy_max)
        bump_radius = np.random.uniform(bump_radius_min, bump_radius_max)
        bump_height = np.random.uniform(bump_height_min, bump_height_max)
        draw_speed_bump(int(cur_x + dx), int(mid_y + dy), bump_radius, bump_height)
        goals[i + 1] = [int(cur_x + dx), int(mid_y + dy)]
        factor *= -1
        cur_x += distance_between_bumps + 2*bump_radius
    
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    
    return height_field, goals

def set_terrain_sphere_bump_lips(length, width, field_resolution, difficulty):
    """
    Spherical speed bumps with lips that the robot has to climb up
    """
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]
    
    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2), dtype=np.int16)

    # difficulty = scale_difficulty(difficulty, 0.5, 1)
    # difficulty = scale_difficulty(difficulty, 0.6, 1)
    difficulty = scale_difficulty(difficulty, *difficulty_scaling["sphere_bump_lips"])
    # bump_radius_min, bump_radius_max = 20 - 0.5 * difficulty, 25 + 1.2 * difficulty
    bump_radius_min, bump_radius_max = 20 - 5 * difficulty, 21 - 5 * difficulty
    # lip_radius_min, lip_radius_max = 10 - 0.5 * difficulty, 12 - 2 * difficulty
    lip_radius_min, lip_radius_max = 10 - 2 * difficulty, 11 - 2 * difficulty
    bump_height_min, bump_height_max = 0.1 + 0.4 * difficulty, 0.15 + 0.45 * difficulty
    bump_height_inc = 0.05
    distance_between_bumps = 0.2 - 0.05 * difficulty
    distance_between_bumps = m_to_idx(distance_between_bumps)
    goal_distance = 0.9 - 0.07 * difficulty
    goal_distance = m_to_idx(goal_distance)

    dx_min, dx_max = -0.4, 0.4
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.9, 0.9
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)
   
    
    def draw_speed_bump(mid_x, mid_y, radius, lip_radius, height):
        x, y = np.ogrid[:m_to_idx(length), :m_to_idx(width)]
        distance = np.sqrt((x - mid_x)**2 + (y - mid_y)**2)
        mask = distance <= radius - lip_radius

        height_field[mask] = height - (distance[mask] / radius) ** 3
        # height_field[height_field < 0] = 0
            

    mid_y = m_to_idx(width) // 2
    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length + bump_radius_max
    factor = 1

    for i in range(6):
        dx = np.random.uniform(dx_min, dx_max)
        dy = np.random.uniform(dy_min, dy_max)
        bump_radius = np.random.uniform(bump_radius_min, bump_radius_max)
        bump_height = np.random.uniform(bump_height_min, bump_height_max) + bump_height_inc * i
        lip_radius = np.random.uniform(lip_radius_min, lip_radius_max)
        draw_speed_bump(int(cur_x + dx), int(mid_y + dy), bump_radius, lip_radius, bump_height)
        goals[i + 1] = [int(cur_x + dx), int(mid_y + dy)]
        factor *= -1
        cur_x += distance_between_bumps + 2*bump_radius
    
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    
    return height_field, goals

def set_terrain_flat_circle_jump(length, width, field_resolution, difficulty):
    """
    Flat bump pillars with lips that the robot has jump between
    """
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]
    # difficulty = scale_difficulty(difficulty, 0.2, 1)
    difficulty = scale_difficulty(difficulty, *difficulty_scaling["flat_circle_jump"])

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2), dtype=np.int16)
    bump_radius_min, bump_radius_max = 20 - 0.5 * difficulty, 21 + 1.2 * difficulty
    lip_radius_min, lip_radius_max = 10 + 0.4 * difficulty, 10.1 + 0.6 * difficulty
    bump_height_min, bump_height_max = 0.1 + 0.08 * difficulty, 0.2 + 0.1 * difficulty
    distance_between_bumps_min, distance_between_bumps_max =  0.4 + 0.7 * difficulty, 0.5 + 0.8 * difficulty
    distance_between_bumps_min, distance_between_bumps_max  = m_to_idx(distance_between_bumps_min), m_to_idx(distance_between_bumps_max)
    goal_distance = 0.9 - 0.07 * difficulty
    goal_distance = m_to_idx(goal_distance)

    dx_min, dx_max = -0.2 + 0.15 * difficulty, 0.2 + 0.15 * difficulty
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2 + 0.15 * difficulty, 0.2 + 0.15 * difficulty
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)
   
    
    def draw_speed_bump(mid_x, mid_y, radius, lip_radius, height):
        x, y = np.ogrid[:m_to_idx(length), :m_to_idx(width)]
        distance = np.sqrt((x - mid_x)**2 + (y - mid_y)**2)
        mask = distance <= radius - lip_radius
        height_field[mask] = height
            

    mid_y = m_to_idx(width) // 2
    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length + distance_between_bumps_max

    factor = 1

    # Set remaining area to be a pit
    # We do this to force the robot to jump from platform to platform
    # Otherwise, the robot can just jump down and climb back up
    height_field[spawn_length:, :] = -1.0

    for i in range(6):
        dx = np.random.uniform(dx_min, dx_max)
        dy = np.random.uniform(dy_min, dy_max)
        bump_radius = np.random.uniform(bump_radius_min, bump_radius_max)
        bump_height = np.random.uniform(bump_height_min, bump_height_max)
        lip_radius = np.random.uniform(lip_radius_min, lip_radius_max)
        draw_speed_bump(int(cur_x + dx), int(mid_y + dy), bump_radius, lip_radius, bump_height)
        goals[i + 1] = [int(cur_x + dx), int(mid_y + dy)]
        factor *= -1
        distance_between_bumps = np.random.uniform(distance_between_bumps_min, distance_between_bumps_max)
        cur_x += int(distance_between_bumps + bump_radius - lip_radius)
    
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[int(cur_x):, :] = 0
    
    return height_field, goals
def set_terrain_bump_jump(length, width, field_resolution, difficulty):
    """
    Spherical bump pillars with lips that the robot has jump between
    """
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]
    
    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2), dtype=np.int16)
    # difficulty = scale_difficulty(difficulty, -1, 0)
    difficulty = scale_difficulty(difficulty, *difficulty_scaling["bump_jump"])

    bump_radius_min, bump_radius_max = 20 - 2.5 * difficulty, 21 - 2.5 * difficulty
    lip_radius_min, lip_radius_max = 3 + 1.5 * difficulty, 3.5 + 2.0 * difficulty
    bump_height_min, bump_height_max = 0.1 + 0.05 * difficulty, 0.15 + 0.07 * difficulty
    distance_between_bumps_min, distance_between_bumps_max =  0.4 + 0.4 * difficulty, 0.5 + 0.5 * difficulty
    distance_between_bumps_min, distance_between_bumps_max  = m_to_idx(distance_between_bumps_min), m_to_idx(distance_between_bumps_max)
    goal_distance = 0.9 - 0.07 * difficulty
    goal_distance = m_to_idx(goal_distance)
    power = 2 
    dx_min, dx_max = -0.2 + 0.15 * difficulty, 0.2 + 0.15 * difficulty
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2 + 0.15 * difficulty, 0.2 + 0.15 * difficulty
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)
   
    
    def draw_speed_bump(mid_x, mid_y, radius, lip_radius, height):
        x, y = np.ogrid[:m_to_idx(length), :m_to_idx(width)]
        distance = np.sqrt((x - mid_x)**2 + (y - mid_y)**2)
        mask = distance <= radius - lip_radius

        height_field[mask] = height - (distance[mask] / radius) ** power
        
        height_field[height_field < -0.35 / (difficulty + 2) ** 2 ] = -1.0
            

    mid_y = m_to_idx(width) // 2
    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length + distance_between_bumps_min
    factor = 1

    # Set remaining area to be a pit
    # We do this to force the robot to jump from platform to platform
    # Otherwise, the robot can just jump down and climb back up
    height_field[spawn_length:, :] = -1.0

    for i in range(6):
        # dx = np.random.randint(dx_min, dx_max)
        dx = 0
        dy = np.random.randint(dy_min, dy_max)
        bump_radius = np.random.uniform(bump_radius_min, bump_radius_max)
        bump_height = np.random.uniform(bump_height_min, bump_height_max)
        lip_radius = np.random.uniform(lip_radius_min, lip_radius_max)
        draw_speed_bump(cur_x + dx, mid_y + dy, bump_radius, lip_radius, bump_height)
        goals[i + 1] = [cur_x + dx, mid_y + dy]
        factor *= -1
        distance_between_bumps = np.random.uniform(distance_between_bumps_min, distance_between_bumps_max)
        cur_x += int(distance_between_bumps + bump_radius - lip_radius)
    
    height_field[0:spawn_length, :] = 0
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[int(cur_x):, :] = 0
    
    return height_field, goals

# def set_terrain_a_frame_gap(length, width, field_resolution, difficulty):
#     """A frame platforms, comprised of an adjacent forward and backward ramp"""
#     def m_to_idx(m):
#         """Converts meters to quantized indices."""
#         return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

#     height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
#     goals = np.zeros((8, 2))

#     # Set up platform dimensions
#     # We make the platform height near 0 at minimum difficulty so the quadruped can learn to climb up
#     platform_length = 0.6 - 0.2 * difficulty
#     platform_length = m_to_idx(platform_length)
#     platform_width = np.random.uniform(1.0, 2.0)
#     platform_width = m_to_idx(platform_width)
#     platform_height_min, platform_height_max = 0.1 + 0.18 * difficulty, 0.2 + 0.25 * difficulty
#     start_height_min, start_height_max = 0.01 + 0.005 * difficulty, 0.03 + 0.01 * difficulty
#     gap_length = 0.1 + 0.4 * difficulty
#     gap_length = m_to_idx(gap_length)

#     mid_y = m_to_idx(width) // 2

#     def add_forward_ramp(start_x, end_x, mid_y, max_platform_height):
#         half_width = platform_width // 2
#         x1, x2 = start_x, end_x
#         y1, y2 = mid_y - half_width, mid_y + half_width
#         start_height = np.random.uniform(start_height_min, start_height_max)
#         for delta in range(x2 - x1):
#             height_field[x1 + delta, y1:y2] = start_height + max_platform_height * (delta/(x2-x1))
    
#     def add_platform(start_x, end_x, mid_y, platform_height):
#         half_width = platform_width // 2
#         x1, x2 = int(start_x), int(end_x)
#         y1, y2 = int(mid_y - half_width), int(mid_y + half_width)
#         height_field[x1:x2, y1:y2] = platform_height
    
#     def add_backward_ramp(start_x, end_x, mid_y, max_platform_height):
#         half_width = platform_width // 2
#         x1, x2 = start_x, end_x
#         y1, y2 = mid_y - half_width, mid_y + half_width
#         start_height = np.random.uniform(start_height_min, start_height_max)
#         for delta in range(x2 - x1):
#             height_field[x1 + delta, y1:y2] = max_platform_height - (max_platform_height - start_height) * (delta/(x2-x1))

#     dx_min, dx_max = -0.1, 0.1
#     dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
#     dy_min, dy_max = -0.1, 0.1
#     dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)
#     gap_min, gap_max = 0 + 0.07 * difficulty, 0.05 + 0.1 * difficulty
#     gap_min, gap_max = m_to_idx(gap_min), m_to_idx(gap_max)

#     # Set spawn area to flat ground
#     spawn_length = m_to_idx(2)
#     height_field[0:spawn_length, :] = 0
#     # Put first goal at spawn
#     goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  
#     flat_length_min, flat_length_max = 0.6 - 0.4 * difficulty, 0.8 - 0.5 * difficulty
#     flat_length_min, flat_length_max = m_to_idx(flat_length_min), m_to_idx(flat_length_max)
#     cur_x = spawn_length
#     for i in range(6):  # Set up 6 platforms
#         dx = np.random.randint(dx_min, dx_max)
#         dy = np.random.randint(dy_min, dy_max)
#         flat_length = np.random.uniform(flat_length_min, flat_length_max)
#         max_platform_height = np.random.uniform(platform_height_min, platform_height_max)
#         add_forward_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, max_platform_height)
#         ramp_gap_length = np.random.uniform(gap_min, gap_max)
#         cur_x += int(platform_length + dx)
#         add_platform(cur_x, cur_x + flat_length, mid_y + dy, max_platform_height)
#         cur_x += int(flat_length + ramp_gap_length)
#         add_platform(cur_x, cur_x + flat_length, mid_y + dy, max_platform_height)
#         cur_x += int(flat_length)
#         add_backward_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, max_platform_height)

#         # Put goal in the center of the platform
#         goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]


#         # Add gap
#         cur_x += int(platform_length + dx + gap_length)
    
#     # Add final goal behind the last platform, fill in the remaining gap
#     goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
#     height_field[cur_x:, :] = 0

#     return height_field, goals
# def set_terrain_stepping_stones_spherical(length, width, field_resolution, difficulty):
#     """Randomly distributed stepping stone platforms that the robot steps along"""

#     def m_to_idx(m):
#         """Converts meters to quantized indices."""
#         return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

#     height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
#     goals = np.zeros((8, 2))

#     # Set up platform dimensions
#     platform_length = 0.8 - 0.3 * difficulty
#     platform_length = m_to_idx(platform_length)
#     radius = platform_length * 2
#     platform_width = 0.55 - 0.2 * difficulty
#     platform_width = m_to_idx(platform_width)
#     platform_height = 0.03
#     gap_length_min, gap_length_max =  0.05 + 0.05 * difficulty, 0.1 + 0.07 * difficulty
#     gap_length_min, gap_length_max = m_to_idx(gap_length_min), m_to_idx(gap_length_max)

#     mid_y = m_to_idx(width) // 2

#     def add_platform(start_x, end_x, mid_y):
#         half_width = platform_width // 2
#         x1, x2 = int(start_x), int(end_x)
#         y1, y2 = int(mid_y - half_width), int(mid_y + half_width)
#         x, y = np.ogrid[:m_to_idx(length), :m_to_idx(width)]
#         mid_x = (start_x + end_x)/ 2
#         distance = np.sqrt((x - mid_x)**2 + (y - mid_y)**2)
        
#         height_field[x1:x2, y1:y2] = platform_height - (distance[x1:x2, y1:y2] / radius) ** 2
    
#     # Vary this with difficulty
#     dy_min, dy_max = 0.15 + 0.035 * difficulty, 0.2 + 0.04 * difficulty
#     dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

#     # Set spawn area to flat ground
#     spawn_length = m_to_idx(2)
#     height_field[0:spawn_length, :] = 0
#     # Put first goal at spawn
#     goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

#     # Set remaining area to be a pit
#     # We do this to force the robot to jump from platform to platform
#     # Otherwise, the robot can just jump down and climb back up
#     height_field[spawn_length:, :] = -1.0

#     cur_x = spawn_length
#     cur_y = mid_y
#     direction = 1
#     for i in range(12):  # Set up 12 platforms
#         dy = np.random.uniform(dy_min, dy_max)
#         # Flip between left and right
#         direction *= -1
#         # draw_speed_bump(cur_x, cur_y + direction * dy, 15, 0, 0.5)
#         add_platform(cur_x, cur_x + platform_length, cur_y + direction * dy)

#         # Put goal in the center of the platform
#         gap_length = np.random.uniform(gap_length_min, gap_length_max)
#         if i % 2 == 0:
#             goals[(i // 2) + 1] = [cur_x + (platform_length) / 2, cur_y + (direction * dy)]
#             cur_x += int(gap_length) 
            
#         else: 
#             cur_x += int(platform_length + 0.2 * gap_length)
#             y_shift = 1 if np.random.uniform(0, 1) > 0.5 else -1
#             cur_y += y_shift * np.random.uniform(dy_min, dy_max)
    
#     # Add final goal behind the last platform, fill in the remaining gap
#     goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
#     height_field[cur_x:, :] = 0

#     return height_field, goals