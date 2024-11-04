import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Staggered platforms with side ramps requiring the robot to climb and navigate precisely."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Variables for platform and gap dimensions
    platform_length = 1.2 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 0.8 + 0.5 * (1 - difficulty)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 * difficulty, 0.4 * difficulty
    gap_length = 0.5 + 1.0 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width / 2)

    def add_platform(start_x, end_x, middle_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = middle_y - half_width, middle_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_ramp(start_x, end_x, middle_y, ramp_height, direction):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = middle_y - half_width, middle_y + half_width
        ramp_slope = np.linspace(0, ramp_height, num=y2-y1)[::direction]
        ramp_slope = ramp_slope[None, :]
        height_field[x1:x2, y1:y2] = ramp_slope

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at spawn

    # Set remaining area to a pit
    height_field[spawn_length:, :] = -1.0  # Keeping height -1 for gap/pit area

    cur_x = spawn_length
    for i in range(6):  # Alternate between platforms and ramps
        dx = np.random.randint(-m_to_idx(0.1), m_to_idx(0.1))
        dy = np.random.randint(-m_to_idx(0.3), m_to_idx(0.3))
        
        # Add platform
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height)
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length
        
        if i < 5:  # Add ramp only for 5 out of 6 iterations
            # Add ramp
            direction = 1 if i % 2 == 0 else -1
            ramp_height = platform_height + np.random.uniform(platform_height_min, platform_height_max)
            add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, ramp_height, direction)
            cur_x += platform_length + dx + gap_length

    # Final goal behind the last platform
    goals[-1] = [cur_x - m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals