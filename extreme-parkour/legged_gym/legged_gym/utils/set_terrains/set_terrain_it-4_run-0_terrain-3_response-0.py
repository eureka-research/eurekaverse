import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Inclined terrain with varied step-based obstacles requiring complex navigation."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and ramp dimensions
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.3)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.3 * difficulty, 0.15 + 0.4 * difficulty
    ramp_length = 1.2 - 0.2 * difficulty
    ramp_length = m_to_idx(ramp_length)
    ramp_height = 0.1 + 0.3 * difficulty
    ramp_height = m_to_idx(ramp_height)
    gap_length = 0.1 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_ramp(start_x, end_x, mid_y, direction):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.linspace(0, ramp_height_max, num=y2-y1)[::direction]
        ramp_height = ramp_height[None, :]  # Add a dimension for broadcasting to x
        height_field[x1:x2, y1:y2] = ramp_height

    dx_min, dx_max = -0.1, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Set remaining area to be a pit
    height_field[spawn_length:, :] = -0.6  # Increase the depth of the pit

    cur_x = spawn_length
    alternate_directions = [1, -1]

    for i in range(6):  # Set up 6 platforms and ramps in sequence
        if i % 2 == 0:
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        else:
            direction = np.random.choice(alternate_directions)
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max) * direction
            add_ramp(cur_x, cur_x + ramp_length + dx, mid_y + dy, direction)
            goals[i+1] = [cur_x + (ramp_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += platform_length + dx + gap_length if i % 2 == 0 else ramp_length + dx + gap_length
    
    # Add final goal behind the last obstacle, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals