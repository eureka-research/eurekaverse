import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Complex mixed terrain with narrow beams, stepping stones, and varying height platforms."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    def add_narrow_beam(start_x, mid_y, length, width, height):
        """Add a narrow beam to the height field."""
        half_width = width // 2
        x1, x2 = start_x, start_x + length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_stepping_stones(start_x, end_x, mid_y, num_stones, stone_size, stone_height):
        """Add multiple stepping stones to the height field."""
        stone_gap = (end_x - start_x) // num_stones
        for i in range(num_stones):
            stone_x1 = start_x + i * stone_gap
            stone_x2 = stone_x1 + stone_size
            height_field[stone_x1:stone_x2, mid_y - stone_size//2:mid_y + stone_size//2] = stone_height

    def add_platform(start_x, mid_y, length, width, height):
        """Add a platform to the height field."""
        half_width = width // 2
        x1, x2 = start_x, start_x + length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    # Dimensions
    narrow_beam_length, narrow_beam_width = m_to_idx(1.5 - 0.5 * difficulty), m_to_idx(0.45)
    narrow_beam_height = 0.1 + 0.15 * difficulty
    stepping_stone_size, stepping_stone_height = m_to_idx(0.6), 0.2 + 0.15 * difficulty
    gap_length = m_to_idx(0.4 + 0.6 * difficulty)
    platform_length, platform_width = m_to_idx(1.0), m_to_idx(1.2)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.3 + 0.3 * difficulty

    mid_y = m_to_idx(width) // 2
    cur_x = m_to_idx(2)

    # Set spawn area to flat ground
    height_field[0:cur_x, :] = 0
    goals[0] = [cur_x - m_to_idx(0.5), mid_y]

    # Add a sequence of narrow beams, stepping stones, and platforms
    even_goal_distrib = np.linspace(1, 6, num=6, endpoint=True, dtype=np.int16)

    for i, rel_goal in enumerate(even_goal_distrib):
        if i % 3 == 0:
            add_narrow_beam(cur_x, mid_y, narrow_beam_length, narrow_beam_width, narrow_beam_height)
            goals[rel_goal] = [cur_x + narrow_beam_length / 2, mid_y]
            cur_x += narrow_beam_length + gap_length
        elif i % 3 == 1:
            add_stepping_stones(cur_x, cur_x + platform_length, mid_y, 5, stepping_stone_size, stepping_stone_height)
            goals[rel_goal] = [cur_x + platform_length / 2, mid_y]
            cur_x += platform_length + gap_length
        else:
            platform_height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, mid_y, platform_length, platform_width, platform_height)
            goals[rel_goal] = [cur_x + platform_length / 2, mid_y]
            cur_x += platform_length + gap_length

    # Place the final goal safely beyond the last obstacle
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    # Ensure the last few meters are flat ground
    height_field[cur_x:, :] = 0

    return height_field, goals