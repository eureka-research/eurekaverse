import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Mixed terrain with inclined ramps, platforms, gaps, and low barriers for a balanced test of agility and navigation."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up dimensions based on difficulty
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width_min, platform_width_max = 0.8, 1.5
    platform_width_min, platform_width_max = m_to_idx(platform_width_min), m_to_idx(platform_width_max)
    platform_height_min, platform_height_max = 0.1 * difficulty, 0.25 * difficulty
    gap_length_min, gap_length_max = 0.2, 0.5
    gap_length_min, gap_length_max = m_to_idx(gap_length_min), m_to_idx(gap_length_max)
    barrier_height = 0.2 + 0.4 * difficulty
    barrier_height = m_to_idx(barrier_height)
    
    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, y_center):
        platform_width = np.random.randint(platform_width_min, platform_width_max)
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        y1 = y_center - platform_width // 2
        y2 = y_center + platform_width // 2
        height_field[start_x:end_x, y1:y2] = platform_height

    def add_ramp(start_x, end_x, y_center, slant):
        platform_width = np.random.randint(platform_width_min, platform_width_max)
        ramp_height = np.random.uniform(platform_height_min, platform_height_max)
        y1 = y_center - platform_width // 2
        y2 = y_center + platform_width // 2
        height_field[start_x:end_x, y1:y2] = np.linspace(0, ramp_height, end_x - start_x)[None, :] * slant

    def add_barrier(x_center, y_center):
        height_field[x_center - 1:x_center + 1, y_center] = barrier_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Initialize terrain creation
    cur_x = spawn_length
    for i in range(7):
        obstacle_type = np.random.choice(['platform', 'ramp', 'barrier'], p=[0.4, 0.4, 0.2])

        if obstacle_type == 'platform':
            dx = np.random.randint(-m_to_idx(0.1), m_to_idx(0.1))
            add_platform(cur_x, cur_x + platform_length + dx, mid_y)
            goals[i + 1] = [cur_x + (platform_length + dx) // 2, mid_y]
            cur_x += platform_length + dx + np.random.randint(gap_length_min, gap_length_max)

        elif obstacle_type == 'ramp':
            ramp_length = platform_length // 2
            dx = np.random.randint(-m_to_idx(0.1), m_to_idx(0.1))
            add_ramp(cur_x, cur_x + ramp_length + dx, mid_y, slant=np.random.choice([-1, 1]))  # Random up/down slope
            goals[i + 1] = [cur_x + (ramp_length + dx) // 2, mid_y]
            cur_x += ramp_length + dx + np.random.randint(gap_length_min, gap_length_max)

        elif obstacle_type == 'barrier':
            add_barrier(cur_x, mid_y)
            goals[i + 1] = [cur_x, mid_y]
            cur_x += np.random.randint(gap_length_min, gap_length_max)

    # Final goal behind last obstacle
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals