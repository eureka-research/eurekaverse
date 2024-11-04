import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Introducing larger gaps, varying heights, and figure-eight paths for enhanced difficulty."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up obstacle dimensions
    base_platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(base_platform_length)
    platform_width = np.random.uniform(0.8, 1.0)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.3 * difficulty, 0.3 + 0.5 * difficulty
    gap_length = 0.2 + 0.7 * difficulty
    gap_length = m_to_idx(gap_length)
    
    mid_y = m_to_idx(width) // 2
    
    def add_platform(start_x, end_x, center_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = center_y - half_width, center_y + half_width
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]
    
    # Sequence of Steps:
    cur_x = spawn_length
    turn_alternator = 1

    for i in range(7):
        # Make platform and set random position
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        platform_height = np.random.uniform(platform_height_min, platform_height_max)

        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height)
        
        # Set goals in the center
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Determine turning path
        if i > 0 and i % 2 == 0:
            direction = ((i // 2) % 2) * 2 - 1  # Alternates between 1 and -1
            cur_y += direction * (platform_width + 2 * gap_length)

        # Add gap before next platform
        cur_x += platform_length + dx + gap_length * turn_alternator
        turn_alternator *= -1
    
    # Final goal behind the last platform
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals