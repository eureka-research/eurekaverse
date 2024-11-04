import numpy as np
from isaacgym import terrain_utils



def set_terrain(terrain, variation, difficulty):
    terrain_fns = [
        set_terrain_random
    ]
    idx = int(variation * len(terrain_fns))
    # GPT-generated terrains have a different signature
    height_field, goals = terrain_fns[idx](terrain.width * terrain.horizontal_scale, terrain.length * terrain.horizontal_scale, terrain.horizontal_scale, difficulty)
    terrain.height_field_raw = (height_field / terrain.vertical_scale).astype(np.int16)
    terrain.goals = goals.astype(np.float64) * terrain.horizontal_scale
    return idx

def set_terrain_random(length, width, field_resolution, difficulty):
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]
    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Ranges from 1 to 4 times the size of the Go 1
    platform_width_min, platform_width_max = 0.6, 2.0
    platform_width_min, platform_width_max = m_to_idx(platform_width_min), m_to_idx(platform_width_max)
    platform_length_min, platform_length_max =  0.6, 1.6
    platform_length_min, platform_length_max = m_to_idx(platform_length_min), m_to_idx(platform_length_max)
    platform_height_min, platform_height_max = 0.1, 0.65
    start_height_min, start_height_max = 0.05, 0.2
    mid_y = m_to_idx(width) // 2

    dy_min, dy_max = -1.0, 1.0
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    def add_ramp(start_x, end_x, mid_y):
        platform_width = np.random.randint(platform_width_min, platform_width_max)
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        max_platform_height = np.random.uniform(platform_height_min, platform_height_max)
        start_height = np.random.uniform(start_height_min, start_height_max)
        for delta in range(x2 - x1):
            height_field[x1 + delta, y1:y2] = start_height + max_platform_height * (delta/(x2-x1))

    def add_platform(start_x, end_x, mid_y):
        platform_width = np.random.randint(platform_width_min, platform_width_max)
        half_width = platform_width // 2
        x1, x2 = int(start_x), int(end_x)
        y1, y2 = int(mid_y - half_width), int(mid_y + half_width)
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height
    
    
    
    gap_length_min, gap_length_max = 0.5, 0.8

    gap_length_min, gap_length_max = m_to_idx(gap_length_min), m_to_idx(gap_length_max)
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  
    cur_x = spawn_length

    for i in range(6):  # Set up 6 platforms
        dy = np.random.randint(dy_min, dy_max)
        platform_length = np.random.randint(platform_length_min, platform_length_max)
        if i % 2 == 0:
            add_ramp(cur_x, int(cur_x + platform_length), int(mid_y + dy))
        else: 
            add_platform(cur_x, int(cur_x + platform_length), int(mid_y + dy))
        # Put goal in the center of the platform
        goals[i+1] = [cur_x + (platform_length) / 2, mid_y + dy]

        # Add gap
        gap_length = np.random.randint(gap_length_min, gap_length_max)
        cur_x += int(platform_length + gap_length)
    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0
    return height_field, goals
