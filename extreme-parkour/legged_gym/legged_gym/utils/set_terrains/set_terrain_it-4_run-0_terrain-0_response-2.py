import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Alternating narrow and wide platforms with varied heights, staggered beams, and offset steps."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Parameters for obstacles
    platform_min_width = 0.4  # minimum width for narrow beams
    platform_max_width = 1.8  # maximum width for wider platforms
    platform_min_height = 0.1  # minimum height for platforms
    platform_max_height = 0.6 * difficulty  # maximum height increasing with difficulty
    gap_length_base = 0.2  # base gap length in meters
    gap_length_incr = 0.2 * difficulty  # gap length increment based on difficulty

    def add_platform(start_x, end_x, y_center, is_narrow=False):
        """Adds a platform with specified width and height to the height_field."""
        width = np.random.uniform(platform_min_width, platform_max_width if not is_narrow else 0.6)
        half_width = m_to_idx(width) // 2
        x1, x2 = start_x, end_x
        y1, y2 = y_center - half_width, y_center + half_width
        height = np.random.uniform(platform_min_height, platform_max_height)
        height_field[x1:x2, y1:y2] = height

    def add_step(start_x, mid_y):
        """Adds an offset step to the height_field."""
        width = np.random.uniform(platform_min_width, platform_max_width)
        length = m_to_idx(0.4)  # step length
        height = np.random.uniform(platform_min_height, platform_max_height)
        
        half_width = m_to_idx(width) // 2
        y1, y2 = mid_y - half_width, mid_y + half_width
        
        for sign in [-1, 1]:
            offset_y = y2 if sign == 1 else y1 - length
            height_field[start_x:start_x + length, offset_y:offset_y + length] = height * sign

    mid_y = m_to_idx(width) // 2
    spawn_length = m_to_idx(2)
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Set the spawn area to flat ground
    height_field[0:spawn_length, :] = 0

    cur_x = spawn_length
    segments = 7  # Number of segments

    for i in range(segments):
        is_narrow = (i % 2 == 0)
        segment_length = np.random.uniform(0.8, 1.4)
        segment_length_idx = m_to_idx(segment_length)
        add_platform(cur_x, cur_x + segment_length_idx, mid_y, is_narrow)

        # Place goal appropriately at each segment.
        goals[i+1] = [cur_x + segment_length_idx // 2, mid_y]

        # Between platforms, add steps periodically for more challenges
        if i % 2 == 1:
            add_step(cur_x + segment_length_idx, mid_y)
        
        # Add gap
        gap_length = gap_length_base + gap_length_incr
        cur_x += segment_length_idx + m_to_idx(gap_length)
    
    # Add the final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals