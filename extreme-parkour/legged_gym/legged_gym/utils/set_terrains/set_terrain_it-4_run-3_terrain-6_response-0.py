import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Staggered platforms and sloped ramps with varying heights and widths for the robot to climb, balance, and jump across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and ramp dimensions
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width_min, platform_width_max = 0.5, 1.0  # Varied widths
    platform_height_min, platform_height_max = 0.1 * difficulty, 0.5 * difficulty
    ramp_height_min, ramp_height_max = 0.2 * difficulty, 0.7 * difficulty
    gap_length_min, gap_length_max = 0.1 + 0.3 * difficulty, 0.4 + 0.6 * difficulty
    gap_length_min, gap_length_max = m_to_idx(gap_length_min), m_to_idx(gap_length_max)

    mid_y = m_to_idx(width) // 2

    def add_platform(x_start, x_end, y_center):
        width = np.random.uniform(platform_width_min, platform_width_max)
        width = m_to_idx(width)
        y1, y2 = y_center - width // 2, y_center + width // 2
        height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x_start:x_end, y1:y2] = height

    def add_ramp(x_start, x_end, y_center, direction):
        width = np.random.uniform(platform_width_min, platform_width_max)
        width = m_to_idx(width)
        y1, y2 = y_center - width // 2, y_center + width // 2
        height = np.random.uniform(ramp_height_min, ramp_height_max)
        ramp_slope = np.linspace(0, height, x_end - x_start)[::direction]
        height_field[x_start:x_end, y1:y2] = ramp_slope[:, None]

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.2, 0.8
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length

    for i in range(7):
        segment_length = np.random.choice([platform_length, platform_length * 1.5])
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        direction = np.random.choice([-1, 1])
        if i % 2 == 0:
            add_platform(cur_x, cur_x + segment_length, mid_y + dy)
        else:
            add_ramp(cur_x, cur_x + segment_length, mid_y + dy, direction)
        
        goals[i+1] = [cur_x + segment_length / 2, mid_y + dy]  # Goal at the center of each segment

        # Next start position
        gap_length = np.random.randint(gap_length_min, gap_length_max)
        cur_x += segment_length + gap_length
    
    # Add final goal behind the last obstacle, fill in the remaining gap
    final_goal_x = min(cur_x + m_to_idx(0.5), height_field.shape[0] - 1)
    goals[-1] = [final_goal_x, mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals