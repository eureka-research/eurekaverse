import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Combination of narrow beams, higher platforms, and rotating slopes for enhanced difficulty challenging balance and climbing."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Dimensions of various obstacles
    platform_length = 1.2 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.4, 0.6)  # Significantly narrower width for beams
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.3 + 0.3 * difficulty, 0.6 + 0.4 * difficulty
    gap_length = 0.4 + 0.8 * difficulty
    gap_length = m_to_idx(gap_length)
    slope_height = 0.2 + 0.5 * difficulty  # Increase slope height as well
    mid_y = m_to_idx(width) // 2

    def add_narrow_beam(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        beam_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = beam_height

    def add_slope(start_x, end_x, mid_y, direction):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slope = np.linspace(0, slope_height, num=y2-y1)[::direction]
        slope = slope[None, :]
        height_field[x1:x2, y1:y2] = slope

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_pipeline = [-0.4, 0.4]  # Alternating dy for platform width
    dy_min, dy_max = m_to_idx(dy_pipeline[0]), m_to_idx(dy_pipeline[1])

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    height_field[spawn_length:, :] = -1.0  # Force terrain

    cur_x = spawn_length
    for i in range(4):  # Alternating platforms and slopes
        dx = np.random.randint(dx_min, dx_max)
        dy = dy_pipeline[i % 2]
        add_narrow_beam(cur_x, cur_x + platform_length + dx, mid_y + dy)
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        
        cur_x += platform_length + dx + gap_length

        # Add slope
        direction = (-1) ** i
        add_slope(cur_x, cur_x + platform_length, mid_y, direction)
        goals[i+1] = [cur_x + platform_length / 2, mid_y]

        cur_x += platform_length + gap_length

    # Final goal behind the last beam
    add_narrow_beam(cur_x, cur_x + platform_length, mid_y)
    goals[-2] = [cur_x + platform_length / 2, mid_y]
    cur_x += platform_length + gap_length  # Behind the last beam
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]  # Last goal

    height_field[cur_x:, :] = 0  # Complete with flat ground if remaining

    return height_field, goals