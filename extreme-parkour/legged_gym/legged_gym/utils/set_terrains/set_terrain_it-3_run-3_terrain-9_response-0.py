import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Varying-width platforms and balance beams with small gaps, testing balance and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform dimensions
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    balance_beam_length = 1.0 - 0.4 * difficulty
    balance_beam_length = m_to_idx(balance_beam_length)
    platform_width_min, platform_width_max = 0.4, 0.8 + 0.6 * difficulty
    beam_width = 0.3
    beam_width = m_to_idx(beam_width)
    platform_height_min, platform_height_max = 0.0 + 0.2 * difficulty, 0.05 + 0.25 * difficulty
    gap_length = 0.1 + 0.4 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, mid_y):
        width = np.random.uniform(platform_width_min, platform_width_max)
        width = m_to_idx(width)
        half_width = width // 2
        x1 = start_x
        x2 = start_x + platform_length
        y1 = mid_y - half_width
        y2 = mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height
        
    def add_balance_beam(start_x, mid_y):
        half_width = beam_width // 2
        x1 = start_x
        x2 = start_x + balance_beam_length
        y1 = mid_y - half_width
        y2 = mid_y + half_width
        beam_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = beam_height

    dx_min, dx_max = m_to_idx(-0.05), m_to_idx(0.05)  # Slight horizontal variability
    dy_min, dy_max = m_to_idx(-0.2), m_to_idx(0.2)  # Slight vertical variability

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    for i in range(4):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        # Add platform or balance beam alternately
        if i % 2 == 0:
            add_platform(cur_x, mid_y + dy)
            goals[i + 1] = [cur_x + platform_length / 2, mid_y + dy]
            cur_x += platform_length + dx + gap_length
        else:
            add_balance_beam(cur_x, mid_y + dy)
            goals[i + 1] = [cur_x + balance_beam_length / 2, mid_y + dy]
            cur_x += balance_beam_length + dx + gap_length

    # Add extra challenges towards the end to increase difficulty
    for i in range(4, 6):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        # Add platform or balance beam alternately with increased width variability
        if i % 2 == 0:
            platform_width_min += difficulty
            platform_width_max += difficulty
            add_platform(cur_x, mid_y + dy)
            goals[i + 1] = [cur_x + platform_length / 2, mid_y + dy]
            cur_x += platform_length + dx + gap_length
        else:
            add_balance_beam(cur_x, mid_y + dy)
            goals[i + 1] = [cur_x + balance_beam_length / 2, mid_y + dy]
            cur_x += balance_beam_length + dx + gap_length

    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals