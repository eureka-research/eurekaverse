import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """A series of dynamic elevating platforms for the robot to navigate and jump across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions and properties
    platform_length_base = 1.0
    platform_length_variation = 0.3 * difficulty
    platform_width = np.random.uniform(1.0, 1.2)  # Slightly narrower platforms
    platform_width = m_to_idx(platform_width)
    platform_height_base = 0.2 * difficulty
    platform_height_variation = 0.3  # Increased height variation for difficulty
    gap_length_base = 0.2
    gap_length_variation = 0.5 * difficulty  # Variable gap length with difficulty
    gap_length = m_to_idx(gap_length_base + gap_length_variation)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height_offset):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = platform_height_base + height_offset
        height_field[x1:x2, y1:y2] = platform_height

    dx_min, dx_max = -0.2, 0.2  # Increased dx variation for complexity
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_variation = 0.4  # maintaining the dy variation
    dy_variation = m_to_idx(dy_variation)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Set remaining area to be a pit
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    for i in range(6):  # Set up 6 platforms
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(-dy_variation, dy_variation)

        platform_length = m_to_idx(platform_length_base + platform_length_variation)
        height_offset = np.random.uniform(0, platform_height_variation)
        
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, height_offset)
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        cur_x += platform_length + dx + gap_length

    # Add final goal behind the last platform
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals