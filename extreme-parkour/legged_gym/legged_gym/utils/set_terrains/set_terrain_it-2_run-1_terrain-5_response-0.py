import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Stepping stones and raised platforms for the robot to navigate, testing its jumping and balance skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and stepping stone dimensions
    stepping_stone_size = [0.4, 0.6]  # size range in meters
    stepping_stone_height = np.random.uniform(0.1, 0.3) + 0.2 * difficulty
    gap_length = 0.1 + 0.7 * difficulty

    platform_width = 1.0  # fixed width for larger platforms
    platform_width = m_to_idx(platform_width)
    platform_height = np.random.uniform(0.2, 0.4) + 0.2 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_stepping_stone(center_x, center_y, size, height):
        x, y = center_x - m_to_idx(size / 2), center_y - m_to_idx(size / 2)
        height_field[x: x + m_to_idx(size), y: y + m_to_idx(size)] = height

    def add_platform(start_x, start_y, width, height):
        x1, x2 = start_x, start_x + m_to_idx(1.0)
        y1, y2 = start_y - width // 2, start_y + width // 2
        height_field[x1:x2, y1:y2] = height

    # Add initial flat area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(4):  # Stepping stones section with 4 stones
        size = np.random.uniform(*stepping_stone_size)
        height = stepping_stone_height + np.random.uniform(-0.1, 0.1)
        add_stepping_stone(cur_x + m_to_idx(size / 2), mid_y, size, height)
        goals[i + 1] = [cur_x + m_to_idx(size / 2), mid_y]
        cur_x += m_to_idx(size + gap_length)

    # Add intermediate larger platform
    add_platform(cur_x, mid_y, platform_width, platform_height)
    goals[5] = [cur_x + m_to_idx(0.5), mid_y]
    cur_x += m_to_idx(1.0 + gap_length)

    for i in range(2):  # Another set of stepping stones
        size = np.random.uniform(*stepping_stone_size)
        height = stepping_stone_height + np.random.uniform(-0.1, 0.1)
        add_stepping_stone(cur_x + m_to_idx(size / 2), mid_y, size, height)
        goals[6 + i] = [cur_x + m_to_idx(size / 2), mid_y]
        cur_x += m_to_idx(size + gap_length)

    # Complete the terrain with a final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals