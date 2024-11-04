import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Mixed terrains with varying heights, slopes, and narrow passages for complex navigation"""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set platform dimensions
    platform_length = 1.5 - 0.4 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.4)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.2 * difficulty, 0.4 * difficulty
    pit_depth = -1.0  # Depth of the pits between platforms
    gap_length = 0.2 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_slope(start_x, end_x, mid_y, height_start, height_end):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slope = np.linspace(height_start, height_end, x2-x1)
        slope = slope[:, None]  # Add an axis to broadcast to the y-dimension
        height_field[x1:x2, y1:y2] = slope

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length

    # Add steps and platforms
    for i in range(3):
        # Random platform height and gap between obstacles
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        dx = np.random.randint(-m_to_idx(0.1), m_to_idx(0.1))
        dy = np.random.randint(-m_to_idx(0.3), m_to_idx(0.3))
        
        # Add platform
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height)
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += platform_length + dx + gap_length

        # After every 2 platforms, add a slope
        if i % 2 == 1:
            slope_end_height = np.random.uniform(platform_height_max, platform_height_max + 0.15 * difficulty)
            add_slope(cur_x - gap_length, cur_x, mid_y + dy, 0.0, slope_end_height)

    # Transition to alternating steps
    for i in range(3):
        platform_height = np.random.uniform(platform_height_min + 0.1, platform_height_max + 0.2)
        dx = np.random.randint(-m_to_idx(0.1), m_to_idx(0.1))
        dy = np.random.randint(-m_to_idx(0.3), m_to_idx(0.3))

        # Add step up
        add_platform(cur_x, cur_x + m_to_idx(0.5) + dx, mid_y - dy, platform_height)
        goals[i+4] = [cur_x + (m_to_idx(0.25) + dx) / 2, mid_y - dy]

        cur_x += m_to_idx(0.5) + dx + gap_length

        # Add step down
        add_platform(cur_x, cur_x + m_to_idx(0.5) + dx, mid_y + dy, -platform_height)
        cur_x += m_to_idx(0.5) + dx + gap_length

    # Add final goal at the end of the course
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0  # Ensure the final surface is flat

    return height_field, goals