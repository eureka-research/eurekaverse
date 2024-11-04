import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Moderately challenging mixed course with gentler platforms, ramps, and uniform gaps."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and ramp dimensions
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 1.2  # Consistent platform width
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 * difficulty, 0.2 + 0.2 * difficulty

    gap_length = 0.3  # Uniform gap length
    gap_length = m_to_idx(gap_length)

    ramp_height = 0.1 + 0.3 * difficulty  # Moderate ramp height

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, length, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, start_x + length
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_ramp(start_x, length, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, start_x + length
        y1, y2 = mid_y - half_width, mid_y + half_width
        slope = np.linspace(0, height, x2 - x1)[None, :]
        slope = np.tile(slope, (height_field.shape[1], 1)).transpose()
        height_field[x1:x2, y1:y2] = slope if height >= 0 else slope[::-1]

    dx_variation = m_to_idx(0.1)  # Small variation in platform and gap lengths

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Variables to track course assembly
    cur_x = spawn_length
    current_y = mid_y

    for i in range(6):  # Create 6 mixed obstacles
        if i % 2 == 0:  # Platforms
            length_variation = platform_length + np.random.randint(-dx_variation, dx_variation)
            add_platform(cur_x, length_variation, current_y)
            goals[i+1] = [cur_x + length_variation / 2, current_y]
            cur_x += length_variation + gap_length
        else:  # Ramps
            length_variation = platform_length - 0.2 + np.random.randint(-dx_variation, dx_variation)
            add_ramp(cur_x, length_variation, current_y, ramp_height)
            ramp_height = -ramp_height  # Alternate height direction for up/down ramps
            goals[i+1] = [cur_x + length_variation / 2, current_y]
            cur_x += length_variation + gap_length

    # Set final goal behind last obstacle
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals