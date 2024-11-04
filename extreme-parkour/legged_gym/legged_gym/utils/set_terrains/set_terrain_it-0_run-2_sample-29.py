import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Series of stepped platforms and ramps to test ascending and descending abilities."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    def add_platform(start_x, end_x, start_y, end_y, height):
        height_field[start_x:end_x, start_y:end_y] = height

    def add_ramp(start_x, end_x, start_y, end_y, start_height, end_height):
        step_count = end_x - start_x
        height_incr = (end_height - start_height) / step_count
        for i in range(step_count):
            height_field[start_x + i, start_y:end_y] = start_height + i * height_incr

    platform_length = m_to_idx(1.0 - 0.3 * difficulty)
    platform_width = m_to_idx(np.random.uniform(1.0, 1.6))
    platform_height_variation = 0.2 * difficulty
    ramp_length = m_to_idx(1.0)
    ramp_height_max = 0.3 + 0.5 * difficulty
    mid_y = m_to_idx(2.0)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at spawn area

    cur_x = spawn_length
    for i in range(4):  # 4 sets of platforms and ramps
        platform_height = np.random.uniform(0.0, platform_height_variation)
        add_platform(cur_x, cur_x + platform_length, mid_y - platform_width // 2, mid_y + platform_width // 2, platform_height)

        goals[2 * i + 1] = [cur_x + platform_length // 2, mid_y]

        ramp_end_height = np.random.uniform(0.0, ramp_height_max)
        add_ramp(cur_x + platform_length, cur_x + platform_length + ramp_length, mid_y - platform_width // 2, mid_y + platform_width // 2, platform_height, ramp_end_height)

        goals[2 * i + 2] = [cur_x + platform_length + ramp_length // 2, mid_y]
        cur_x += platform_length + ramp_length

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    # Set final area to flat ground
    height_field[cur_x:, :] = 0

    return height_field, goals