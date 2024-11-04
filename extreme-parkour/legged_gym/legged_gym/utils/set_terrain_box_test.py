import numpy as np

def set_terrain(terrain, variation, difficulty):
    terrain_fns = [
        # Climbing
        set_terrain_jump_on_and_off_box,
    ]
    idx = int(variation * len(terrain_fns))
    # GPT-generated terrains have a different signature
    height_field, goals = terrain_fns[idx](terrain.width * terrain.horizontal_scale, terrain.length * terrain.horizontal_scale, terrain.horizontal_scale, difficulty)
    terrain.height_field_raw = (height_field / terrain.vertical_scale).astype(np.int16)
    terrain.goals = goals.astype(np.float64) * terrain.horizontal_scale
    return idx

def set_terrain_jump_on_and_off_box(length, width, field_resolution, difficulty):
    """Multiple ramp platforms that go from the ground to a height"""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    
    difficulty = 0
    # Set up platform dimensions
    # We make the platform height near 0 at minimum difficulty so the quadruped can learn to climb up
    platform_length = 0.60
    platform_length = m_to_idx(platform_length)
    platform_width = 0.70
    platform_width = m_to_idx(platform_width)
    # platform_height_min, platform_height_max = 0.1 + 0.45 * difficulty, 0.2 + 0.5 * difficulty
    # platform_height_min, platform_height_max = 0.1 + 0.55 * difficulty, 0.15 + 0.55 * difficulty
    platform_height = 0.2
    # platform_height_inc = 0.05
    gap_length = 0.2
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        for delta in range(x2 - x1):
            height_field[x1 + delta, y1:y2] = platform_height

  

    # Set spawn area to flat ground
    spawn_length = m_to_idx(3)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  
    

    cur_x = spawn_length
    add_platform(cur_x, int(cur_x + platform_length), int(mid_y))
    for i in range(6):  # Set up 6 platforms
        # dx = np.random.uniform(dx_min, dx_max)
        # dy = np.random.uniform(dy_min, dy_max)
        # platform_height = np.random.uniform(platform_height_min, platform_height_max) + platform_height_inc * i
        

        # Put goal in the center of the platform
        goals[i+1] = [cur_x + (platform_length) / 2, mid_y]

        # Add gap
        cur_x += int(platform_length + gap_length)
    
    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0
    print(goals)
    return height_field, goals