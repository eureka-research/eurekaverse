import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Narrow paths, higher platforms, and wider gaps for comprehensive balance, navigation, and jumping challenges."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform and gap dimension variables
    platform_length = 0.8 - 0.3 * difficulty  # Increasing difficulty decreases platform size
    platform_length = m_to_idx(platform_length)
    platform_width = 0.6 + 0.3 * difficulty  # Making the platform width narrower with increased difficulty
    platform_width = m_to_idx(platform_width)
    platform_height_min = 0.2 + 0.3 * difficulty  # Taller platforms
    platform_height_max = 0.4 + 0.4 * difficulty
    gap_length = 0.2 + 0.8 * difficulty  # Wider gaps
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, center_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = center_y - half_width, center_y + half_width
        height_field[x1:x2, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[:spawn_length, :] = 0  # Ensuring flat spawn area
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at spawn

    last_x = spawn_length
    for i in range(1, 8):
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        start_x = last_x + gap_length
        end_x = start_x + platform_length

        center_y_offset = (-1) ** i * np.random.randint(0, m_to_idx(0.3))  # alternating offsets

        add_platform(start_x, end_x, mid_y + center_y_offset, platform_height)

        goals[i] = [start_x + platform_length / 2, mid_y + center_y_offset]

        last_x = end_x

    return height_field, goals