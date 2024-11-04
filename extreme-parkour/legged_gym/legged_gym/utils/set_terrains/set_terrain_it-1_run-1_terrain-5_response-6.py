import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Narrow elevated pathways and pits requiring careful navigation and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform and pit dimensions
    platform_length_range = [0.6, 1.2]
    platform_width_range = [0.35, 0.6]  # Slightly narrow platforms
    platform_height_min, platform_height_max = 0.0 + 0.2 * difficulty, 0.1 + 0.3 * difficulty
    pit_width_range = [1.0, 1.5]

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, width, height):
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_pit(start_x, end_x, width):
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = -1.0  # Depth of the pit

    # Convert lengths and widths to indices
    platform_length_range = m_to_idx(platform_length_range)
    platform_width_range = m_to_idx(platform_width_range)
    pit_width_range = m_to_idx(pit_width_range)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    for i in range(4):
        # Add a platform
        platform_length = np.random.randint(platform_length_range[0], platform_length_range[1])
        platform_width = np.random.randint(platform_width_range[0], platform_width_range[1])
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        add_platform(cur_x, cur_x + platform_length, platform_width, platform_height)
        goals[i*2 + 1] = [cur_x + platform_length // 2, mid_y]

        cur_x += platform_length

        # Add a pit
        pit_width = np.random.randint(pit_width_range[0], pit_width_range[1])
        add_pit(cur_x, cur_x + pit_width, pit_width)
        goals[i*2 + 2] = [cur_x + pit_width // 2, mid_y]  # Mid-pit goal to encourage jumping

        cur_x += pit_width

    # Ensure we cover the remaining length till 12 meters
    final_section_length = m_to_idx(1)
    height_field[cur_x:, :] = 0
    goals[-1] = [cur_x + final_section_length // 2, mid_y]

    return height_field, goals