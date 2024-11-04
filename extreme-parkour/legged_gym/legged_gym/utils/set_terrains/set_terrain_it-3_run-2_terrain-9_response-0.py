import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Combines inclined ramps, high platforms with steps, narrow beams, and variable terrain heights for increased difficulty."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Convert parameters to index space
    platform_length = m_to_idx(2.0 - 0.3 * difficulty)
    platform_width = m_to_idx(0.8 * (1.0 - difficulty))
    platform_height_range = (0.2 * difficulty, 0.4 * difficulty)
    ramp_length = m_to_idx(0.7 + 0.2 * difficulty)
    beam_width = m_to_idx(0.35 - 0.15 * difficulty)
    gap_length = m_to_idx(0.3 + 0.5 * difficulty)
    spawn_length = m_to_idx(2)
    mid_y = m_to_idx(width) // 2

    def add_inclined_ramp(start_x, end_x, mid_y, height, direction):
        delta_height = np.linspace(0, height, end_x - start_x)
        if direction == "down":
            delta_height = delta_height[::-1]
        height_field[start_x:end_x, mid_y - platform_width // 2:mid_y + platform_width // 2] = delta_height[:, np.newaxis]

    def add_platform(start_x, end_x, mid_y, height):
        height_field[start_x:end_x, mid_y - platform_width // 2:mid_y + platform_width // 2] = height

    def add_narrow_beam(start_x, end_x, mid_y):
        height_field[start_x:end_x, mid_y - beam_width // 2:mid_y + beam_width // 2] = platform_height_range[1]

    # Set flat spawn area
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]
    cur_x = spawn_length

    # Add inclined ramp
    ramp_height = np.random.uniform(*platform_height_range)
    add_inclined_ramp(cur_x, cur_x + ramp_length, mid_y, ramp_height, direction="up")
    goals[1] = [cur_x + ramp_length // 2, mid_y]
    cur_x += ramp_length + gap_length

    # Add high platforms with steps
    for step in range(2):
        platform_height = np.random.uniform(*platform_height_range)
        add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)
        goals[2 + step] = [cur_x + platform_length // 2, mid_y]
        cur_x += platform_length + gap_length

    # Add narrow beam navigation
    add_narrow_beam(cur_x, cur_x + platform_length, mid_y)
    goals[4] = [cur_x + platform_length // 2, mid_y]
    cur_x += platform_length + gap_length

    # Add variable terrain heights
    for i in range(2):
        height = np.random.uniform(*platform_height_range)
        add_platform(cur_x, cur_x + platform_length, mid_y, height)
        goals[5 + i] = [cur_x + platform_length // 2, mid_y]
        cur_x += platform_length + gap_length

    # Add final goal after last platform
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals