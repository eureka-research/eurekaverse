import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Complex terrain combining slopes, narrow beams, and platforms for enhanced difficulty."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Dimensions for platforms, ramps, and narrow beams
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.3)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.3 + 0.5 * difficulty
    narrow_beam_width = 0.4 - 0.1 * difficulty
    narrow_beam_width = m_to_idx(narrow_beam_width)
    gap_length = 0.2 + 0.8 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_narrow_beam(start_x, end_x, mid_y, height):
        half_width = narrow_beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Initial pit setup forcing precise jumps
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length

    # Arrange obstacles complexity increases with gap jumps and varying heights
    for i in range(4):
        platform_height = np.random.uniform(platform_height_min, platform_height_max)

        # Alternate between platforms and narrow beams
        if i % 2 == 0:
            add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)
            goals[i+1] = [cur_x + platform_length / 2, mid_y]
            cur_x += platform_length + gap_length
        else:
            add_narrow_beam(cur_x, cur_x + platform_length, mid_y, platform_height)
            goals[i+1] = [cur_x + platform_length / 2, mid_y]
            cur_x += platform_length + gap_length

    # Add final challenging section with ramps
    def add_ramp(start_x, end_x, mid_y, direction):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(platform_height_min, platform_height_max)
        slant = np.linspace(0, ramp_height, num=y2-y1)[::direction]
        slant = slant[None, :]  # Add a dimension for broadcasting to x
        height_field[x1:x2, y1:y2] = slant

    for i in range(5, 8):
        direction = 1 if i % 2 == 0 else -1
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        add_ramp(cur_x, cur_x + platform_length, mid_y, direction)
        goals[i] = [cur_x + platform_length / 2, mid_y]
        cur_x += platform_length + gap_length

    # Final goal behind the last ramp, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals