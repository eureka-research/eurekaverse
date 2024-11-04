import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Complex course with stepping stones, staggered platforms, and inclined ramps."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform dimensions and height range
    platform_length = 1.0
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.9, 1.2)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.1 * difficulty, 0.3 + 0.3 * difficulty

    gap_length = m_to_idx(0.3 + 0.6 * difficulty)
    
    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_stepping_stones(start_x, num_stones, mid_y):
        stone_length = m_to_idx(0.4)
        stone_width = m_to_idx(0.4)
        stone_height_range = 0.0 + 0.25 * difficulty, 0.1 + 0.35 * difficulty

        for i in range(num_stones):
            platform_height = np.random.uniform(*stone_height_range)
            step_x = start_x + i * (stone_length + gap_length)
            add_platform(step_x, step_x + stone_length, mid_y + (np.random.randint(-2, 3) * stone_width), platform_height)

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
    
    # Add first platform
    platform_height = np.random.uniform(platform_height_min, platform_height_max)
    add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)
    goals[1] = [cur_x + platform_length / 2, mid_y]
    cur_x += platform_length + gap_length

    # Add stepping stones
    add_stepping_stones(cur_x, 3, mid_y)  # 3 stepping stones
    goals[2] = [cur_x + platform_length, mid_y]

    cur_x += 3 * m_to_idx(0.4) + 3 * gap_length

    # Add staggered platform with narrow bridges
    stagger_x = [cur_x, cur_x + platform_length + gap_length, cur_x + 2 * (platform_length + gap_length)]
    stagger_y = [mid_y - m_to_idx(1), mid_y, mid_y + m_to_idx(1)]
    for x, y in zip(stagger_x, stagger_y):
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        add_platform(x, x + platform_length, y, platform_height)

    goals[3] = [stagger_x[-1] + platform_length / 2, stagger_y[-1]]
    cur_x = stagger_x[-1] + platform_length + gap_length

    # Add inclined ramp
    ramp_height = np.random.uniform(0.3 + 0.3 * difficulty, 0.5 + 0.5 * difficulty)
    add_ramp(cur_x, cur_x + platform_length, mid_y, ramp_height)
    goals[4] = [cur_x + platform_length / 2, mid_y]
    cur_x += platform_length + gap_length

    # Add final set of platforms
    for i in range(3):  # 3 platforms
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        add_platform(cur_x, cur_x + platform_length, mid_y + m_to_idx(i * 0.2), platform_height)
        goals[5 + i] = [cur_x + platform_length / 2, mid_y + m_to_idx(i * 0.2)]
        cur_x += platform_length + gap_length

    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals  # Return the desired terrain and goals