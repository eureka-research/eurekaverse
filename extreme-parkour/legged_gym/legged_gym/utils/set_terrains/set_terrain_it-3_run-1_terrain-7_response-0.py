import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Obstacle course with staggered platforms, ramps, and gaps requiring the quadruped to balance, climb, and jump effectively."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length = m_to_idx(1.0 - 0.2 * difficulty)
    platform_width = m_to_idx(np.random.uniform(0.8, 1.2))
    platform_height_min, platform_height_max = 0.1 * difficulty, 0.3 * difficulty
    ramp_length = m_to_idx(0.5)  # keeping ramps shorter
    ramp_height_min, ramp_height_max = 0.2, 0.4 + 0.3 * difficulty
    gap_length = m_to_idx(0.3 + 0.5 * difficulty)  # Increase gap length

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_ramp(start_x, end_x, mid_y, height, direction):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slope = np.linspace(0, height, num=end_x-start_x)
        if direction > 0:
            height_field[x1:x2, y1:y2] = slope[:, np.newaxis]
        else:
            height_field[x1:x2, y1:y2] = slope[::-1, np.newaxis]

    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0.0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    for i in range(4):  # Create 4 main sections: 2 platforms and 2 ramps
        height = np.random.uniform(platform_height_min, platform_height_max)
        if i % 2 == 0:  # Add platforms on even iterations
            add_platform(cur_x, cur_x + platform_length, mid_y, height)
            goals[i + 1] = [cur_x + platform_length // 2, mid_y]
            cur_x += platform_length + gap_length
        else:  # Add ramps on odd iterations
            ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
            direction = 1 if i % 4 == 1 else -1
            add_ramp(cur_x, cur_x + ramp_length, mid_y, ramp_height, direction)
            goals[i + 1] = [cur_x + ramp_length // 2, mid_y]
            cur_x += ramp_length + gap_length

    final_height = np.random.uniform(platform_height_min, platform_height_max)
    add_platform(cur_x, cur_x + platform_length, mid_y, final_height)
    goals[5] = [cur_x + platform_length // 2, mid_y]
    cur_x += platform_length

    for i in range(2):  # add some simple stepping obstacles
        height = np.random.uniform(platform_height_min, platform_height_max)
        dx = m_to_idx(0.3 * (i + 1))
        dy = m_to_idx(0.5 * (i + 1))
        add_platform(cur_x + dx, cur_x + dx + platform_length, mid_y + dy, height)
        goals[6 + i] = [cur_x + dx + platform_length // 2, mid_y + dy]
        cur_x += platform_length + gap_length

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0.0

    return height_field, goals