import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Series of varied platforms, ramps, and narrow bridges to challenge the quadruped's navigation and balance skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up different obstacle dimensions
    platform_length = 1.0 - 0.3 * difficulty
    platform_length_idx = m_to_idx(platform_length)
    
    platform_heights = [0.1 + 0.2 * difficulty, 0.3 + 0.3 * difficulty]
    bridge_width = 0.4  # meters
    bridge_width_idx = m_to_idx(bridge_width)
    bridge_height = 0.4  # constant bridge height
    
    gap_length = 0.3 + 0.7 * difficulty
    gap_length_idx = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width_idx // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_bridge(start_x, end_x, mid_y, height):
        half_width = bridge_width_idx // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height
    
    def add_ramp(start_x, end_x, mid_y, is_upward):
        height = 0.4  # ramp at 0.4 meters height
        half_width = platform_width_idx // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_slope = np.linspace(0, height, num=x2-x1)[None, :] if is_upward else np.linspace(height, 0, num=x2-x1)[None, :]
        
        height_field[x1:x2, y1:y2] = ramp_slope.T

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(3):  # Three sets of platforms or ramps
        dx = np.random.randint(-m_to_idx(0.2), m_to_idx(0.3))  # Small variation in length
        dy = np.random.randint(-m_to_idx(0.4), m_to_idx(0.4))  # Small variation in width

        if i % 3 == 0:
            # Add varied platforms
            height = np.random.choice(platform_heights)
            add_platform(cur_x, cur_x + platform_length_idx + dx, mid_y + dy, height)
        elif i % 3 == 1:
            # Add ramps (alternating upward and downward)
            is_upward = i % 6 == 1
            add_ramp(cur_x, cur_x + platform_length_idx + dx, mid_y + dy, is_upward)
        else:
            # Add narrow bridges
            add_bridge(cur_x, cur_x + platform_length_idx + dx, mid_y + dy, bridge_height)
        
        # Set goals for each obstacle
        goals[i+1] = [cur_x + (platform_length_idx + dx) / 2, mid_y + dy]

        # Add a gap
        cur_x += platform_length_idx + dx + gap_length_idx

    # Add final goal and fill the gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0
    
    return height_field, goals