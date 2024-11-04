import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Combination of stepping stones, ramps, gaps, and mixed terrain for the quadruped to navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform and obstacle dimensions
    obstacle_width_min = 0.4
    obstacle_width_max = 1.6
    obstacle_length = 1.0 - 0.3 * difficulty
    obstacle_length = m_to_idx(obstacle_length)
    platform_height_min, platform_height_max = 0.05 * difficulty, 0.3 + 0.2 * difficulty
    ramp_height_min, ramp_height_max = 0.1 * difficulty, 0.35 + 0.25 * difficulty
    gap_length = 0.1 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    # Helper functions to add various obstacles
    def add_platform(start_x, end_x, mid_y):
        half_width = np.random.uniform(obstacle_width_min, obstacle_width_max)
        half_width = m_to_idx(half_width) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_ramp(start_x, end_x, mid_y, direction):
        half_width = np.random.uniform(obstacle_width_min, obstacle_width_max)
        half_width = m_to_idx(half_width) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        slant = np.linspace(0, ramp_height, num=y2-y1)[::direction]
        slant = slant[None, :]  # Add a dimension for broadcasting to x
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground and add the first goal
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    for i in range(7):
        if i % 3 == 0:  # Add platforms
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)
            add_platform(cur_x, cur_x + obstacle_length + dx, mid_y + dy)
            goals[i+1] = [cur_x + (obstacle_length + dx) / 2, mid_y + dy]
        elif i % 3 == 1:  # Add ramps
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)
            direction = random.choice([-1, 1])
            add_ramp(cur_x, cur_x + obstacle_length + dx, mid_y + dy, direction)
            goals[i+1] = [cur_x + (obstacle_length + dx) / 2, mid_y + dy]
        else:  # Add gaps
            gap_width = gap_length * (1 + random.uniform(-0.1, 0.1))
            height_field[cur_x:cur_x + gap_length] = 0
            cur_x += gap_length

        cur_x += obstacle_length + dx + gap_length

    # Add the final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals