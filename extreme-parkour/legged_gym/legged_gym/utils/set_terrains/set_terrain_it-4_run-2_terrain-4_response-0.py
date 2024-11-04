import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Alternating narrow beams, wide platforms, and sloped ramps for varied challenges."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform sizes and parameters
    narrow_width = 0.4 + 0.2 * difficulty  # Narrow beams
    wide_width = 1.0 + 0.4 * difficulty  # Wider platforms
    slope_height = 0.0 + 0.2 * difficulty  # Heights for sloped ramps
    platform_min_height, platform_max_height = 0.05 * difficulty, 0.35 * difficulty

    narrow_width, wide_width = m_to_idx(narrow_width), m_to_idx(wide_width)
    slope_height = m_to_idx(slope_height)
    gap_length = 0.1 + 0.4 * difficulty  # Varied gap lengths
    gap_length = m_to_idx(gap_length)
    
    mid_y = m_to_idx(width) // 2

    def add_narrow_beam(start_x, end_x, mid_y):
        half_width = narrow_width // 2
        height = np.random.uniform(platform_min_height, platform_max_height)
        height_field[start_x:end_x, mid_y - half_width:mid_y + half_width] = height

    def add_wide_platform(start_x, end_x, mid_y):
        half_width = wide_width // 2
        height = np.random.uniform(platform_min_height, platform_max_height)
        height_field[start_x:end_x, mid_y - half_width:mid_y + half_width] = height

    def add_ramp(start_x, end_x, mid_y):
        half_width = wide_width // 2
        slant_height = np.random.uniform(platform_min_height, platform_max_height)
        slant = np.linspace(0, slant_height, num=end_x - start_x)
        slant = slant[:, None]  # Add a dimension for broadcasting to y
        height_field[start_x:end_x, mid_y-half_width:mid_y+half_width] = slant

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(1), mid_y]  # First goal at the spawn point

    cur_x = spawn_length
    # Define the alternating course patterns
    course_components = [add_narrow_beam, add_wide_platform, add_ramp]
    
    for i in range(6):
        component = course_components[i % len(course_components)]
        component(cur_x, cur_x + gap_length, mid_y)
        goals[i+1] = [cur_x + gap_length // 2, mid_y]
        cur_x += gap_length
        
        # Add varied gaps
        cur_x += gap_length

    # Add final goal behind the last obstacle, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(1), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals