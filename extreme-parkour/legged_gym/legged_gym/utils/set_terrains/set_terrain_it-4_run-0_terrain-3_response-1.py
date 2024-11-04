import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Multi-level platforms with varying step heights for the quadruped to climb up and down."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Multi-level platform dimensions
    base_platform_length = 1.0 - 0.2 * difficulty
    platform_length = m_to_idx(base_platform_length)
    platform_width_range = (1.0, 1.2)                         # Uniform width range for more manageability
    platform_height_min, platform_height_max = 0.1 * difficulty, 0.25 * difficulty   # Varying step height for complexity
    gap_length = 0.2 + 0.5 * difficulty                       # Larger gaps to increase challenge
    gap_length = m_to_idx(gap_length)
    
    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    current_gap_length = gap_length * 0.8 if difficulty > 0.7 else gap_length

    # Initialize quadruped spawn area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at spawn
    
    cur_x = spawn_length
    for i in range(6):  # Set up 6 platforms 
        platform_width = np.random.uniform(*platform_width_range)
        platform_width = m_to_idx(platform_width)
        platform_length = m_to_idx(base_platform_length + 0.2 * np.random.rand() * difficulty)  # Slight variation in platform length

        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)

        goals[i + 1] = [cur_x + platform_length / 2, mid_y]  # Goal in the center of the platform
        
        cur_x += platform_length + current_gap_length
        if i % 2 == 0:  # Introduce step drops every other platform
            mid_y += m_to_idx(0.2 + difficulty * 0.15 * (-1) ** np.random.randint(2))

    # Final goal placement beyond the last platform
    height_field[cur_x:, :] = 0
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    return height_field, goals