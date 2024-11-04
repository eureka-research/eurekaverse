import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Complex terrain with raised platforms, narrow beams, and dynamic obstacles."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up obstacle dimensions
    platform_length = 1.0 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.4)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.3 + 0.3 * difficulty
    beam_length = np.random.uniform(0.8, 1.2)
    beam_length = m_to_idx(beam_length)
    beam_width = 0.3
    beam_width = m_to_idx(beam_width)
    gap_length = 0.2 + 0.4 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_beam(start_x, height):
        half_width = beam_width // 2
        x1, x2 = start_x, start_x + beam_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_dynamic_obstacles(cur_x):
        height_variation = np.linspace(platform_height_min, platform_height_max, num=platform_length)
        x1, x2 = cur_x, cur_x + platform_length
        for i in range(m_to_idx(platform_length)):
            height_field[x1 + i, mid_y-1:mid_y+2] = height_variation[i]  # vary heights in a narrow section

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(3):  # Adding 3 raised platforms
        height = np.random.uniform(platform_height_min, platform_height_max)
        add_platform(cur_x, cur_x + platform_length, height)
        goals[i + 1] = [cur_x + platform_length // 2, mid_y]
        cur_x += platform_length + gap_length

    for i in range(2):  # Adding 2 narrow beams
        height = np.random.uniform(platform_height_min, platform_height_max)
        add_beam(cur_x, height)
        goals[i + 4] = [cur_x + beam_length // 2, mid_y]
        cur_x += beam_length + gap_length

    for i in range(2):  # Adding 2 sections with dynamic obstacles
        add_dynamic_obstacles(cur_x)
        goals[i + 6] = [cur_x + platform_length // 2, mid_y]
        cur_x += platform_length + gap_length

    # Add final goal behind the last obstacle
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals