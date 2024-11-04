import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Combined staggered steps, narrow and wide platforms, and ramps for varied navigation challenges."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Dimensions for diverse and moderately challenging obstacles
    platform_length = 1.5 - 0.4 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width_low, platform_width_high = 1.0, 1.6
    platform_height_min, platform_height_max = 0.3 + 0.2 * difficulty, 0.5 + 0.3 * difficulty
    ramp_height_min, ramp_height_max = 0.2 + 0.3 * difficulty, 0.5 + 0.4 * difficulty
    gap_length = 0.3 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, is_ramp=False):
        half_width = np.random.uniform(platform_width_low, platform_width_high)
        half_width = m_to_idx(half_width) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        if is_ramp:
            direction = np.random.choice([-1, 1])
            ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
            slant = np.linspace(0, ramp_height, num=y2-y1)[::direction]
            slant = slant[None, :]  # Add a dimension for broadcasting to x
            height_field[x1:x2, y1:y2] = slant
        else:
            platform_height = np.random.uniform(platform_height_min, platform_height_max)
            height_field[x1:x2, y1:y2] = platform_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Place the first goal near the spawn area
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]
    
    # Creating a variety of obstacles
    cur_x = spawn_length
    dy_min, dy_max = -0.5, 0.5  # Promoting diverse stepping
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    for i in range(6):  # Set up 6 obstacles with alternating platforms and ramps
        dx = np.random.randint(-1, 2)  # Small random variance in x-direction positioning
        dy = np.random.randint(dy_min, dy_max)  # Small random variance in y-direction positioning
        if i % 2 == 0:  # Even index, place a platform
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        else:  # Odd index, place a ramp
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, is_ramp=True)
            goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        cur_x += platform_length + dx + gap_length

    # Add final goal behind the last obstacle
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0  # Fill the remaining terrain with flat ground

    return height_field, goals