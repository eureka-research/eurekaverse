import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Rolling logs of increasing difficulty for balance and timing challenges."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    log_length = 0.8 + 0.2 * difficulty  # Dynamic log length increasing with difficulty
    log_radius = 0.1 + 0.15 * difficulty  # Log radius increases with difficulty
    platform_length = 0.8  # Static platform for staging and rest areas
    platform_height_min, platform_height_max = 0.1, 0.3  # Height of static platforms for variety
    gap_length = 0.3 * difficulty

    log_length = m_to_idx(log_length)
    log_radius = m_to_idx(log_radius)
    platform_length = m_to_idx(platform_length)
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_length // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_log(x_center, y_center, radius):
        for x in range(x_center - radius, x_center + radius):
            dz = np.sqrt(radius**2 - (x_center - x)**2)
            height_field[x, y_center - radius:y_center + radius] = dz

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at spawn area

    cur_x = spawn_length

    # Introduce a combination of static platform stages and rolling logs
    for i in range(3):
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)
        goals[i+1] = [cur_x + platform_length // 2, mid_y]
        cur_x += platform_length + gap_length

        log_x = cur_x
        log_y = mid_y
        add_log(log_x, log_y, log_radius)
        goals[i+4] = [log_x, log_y]
        cur_x += 2 * log_radius + gap_length

    # Add final goal for course completion
    goals[7] = [m_to_idx(length) - m_to_idx(1), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals