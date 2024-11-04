import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Diverse high-difficulty course with inclined planes, staggered platforms, and large gaps."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_width = np.random.uniform(0.5, 1.0)
    platform_width = m_to_idx(platform_width)
    
    platform_length = 0.8  # Consistent length for platforms
    platform_length = m_to_idx(platform_length)
    
    gap_length_min, gap_length_max = 0.3 + 0.4 * difficulty, 0.5 + 0.6 * difficulty  # significant gaps
    height_variation_min, height_variation_max = 0.2 * difficulty, 0.6 + 0.4 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, y_center):
        half_width = platform_width // 2
        y_start, y_end = y_center - half_width, y_center + half_width
        height = np.random.uniform(height_variation_min, height_variation_max)
        height_field[start_x:end_x, y_start:y_end] = height

    def add_ramp(start_x, end_x, y_center, angle):
        len_x = end_x - start_x
        y_start, y_end = y_center - platform_width // 2, y_center + platform_width // 2
        x_indices = np.arange(len_x)
        heights = np.tan(angle) * x_indices * field_resolution  # slope height profile
        height_field[start_x:end_x, y_start:y_end] = heights[:, None].T  # Broadcasting to y dimension

    dx_min, dx_max = -0.2, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3  # Varied y offsets
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)
    
    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(6):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        if i % 2 == 0:
            # Dynamic decision to add either ramp or platform for diversity
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
        else:
            ramp_angle = np.pi / 6 * (1 + 0.5 * difficulty)  # Steeper ramps with difficulty
            add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, ramp_angle)
        
        goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + np.random.randint(m_to_idx(gap_length_min), m_to_idx(gap_length_max))
    
    # Add final goal behind the last obstacle, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals