import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Complex course with beams, raised platforms, and wider gaps to test the quadruped's navigation, balance, and jumping skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Dimensions for obstacles, adjusting their size with difficulty
    narrow_beam_width = m_to_idx(0.25 - 0.1 * difficulty)
    platform_length = m_to_idx(1.0 - 0.3 * difficulty)
    platform_width = m_to_idx(1.0 - 0.2 * difficulty)
    platform_height_min, platform_height_max = 0.1 + 0.25 * difficulty, 0.5 + 0.4 * difficulty
    gap_length = m_to_idx(0.7 + 0.6 * difficulty)

    mid_y = m_to_idx(width / 2)

    def add_narrow_beam(start_x, end_x, mid_y):
        half_width = narrow_beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        beam_height = np.random.uniform(0.15, 0.4) * difficulty
        height_field[x1:x2, y1:y2] = beam_height

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    dx_min, dx_max = m_to_idx(-0.1), m_to_idx(0.1)
    dy_min, dy_max = m_to_idx(-0.4), m_to_idx(0.4)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    # Add a mixture of obstacles
    for i in range(3):  # First, add 3 narrow beams
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_narrow_beam(cur_x, cur_x + platform_length + dx, mid_y + dy)
        goals[i + 1] = [cur_x + (platform_length + dx) // 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length
    
    for i in range(3, 6):  # Add 3 raised platforms
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
        goals[i + 1] = [cur_x + (platform_length + dx) // 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

    goals[6] = [cur_x + m_to_idx(0.5), mid_y]

    # For the final challenge, add an extended platform with a larger gap
    large_gap_length = m_to_idx(1.0 + 0.4 * difficulty)
    cur_x += large_gap_length
    add_platform(cur_x, cur_x + platform_length, mid_y)
    goals[7] = [cur_x + platform_length // 2, mid_y]

    # Fill remaining area after final goal
    height_field[cur_x:, :] = 0

    return height_field, goals