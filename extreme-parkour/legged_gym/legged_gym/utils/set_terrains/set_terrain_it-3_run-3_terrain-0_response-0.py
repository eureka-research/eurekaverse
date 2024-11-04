import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Complex terrain with mixed platforms, ramps, and narrow beams to challenge the quadruped's balance, jumping, and climbing abilities."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up dimensions for platforms, ramps, and beams
    platform_length = 1.0
    platform_length = m_to_idx(platform_length)
    platform_width = m_to_idx(np.random.uniform(0.8, 1.2))
    platform_height_min, platform_height_max = 0.2, 0.4
    
    ramp_length = platform_length // 2
    ramp_height_min, ramp_height_max = 0.3, 0.6

    beam_length = platform_length
    beam_width = m_to_idx(0.3)
    beam_height = 0.2

    gap_min, gap_max = m_to_idx(0.3), m_to_idx(0.7)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_ramp(start_x, end_x, mid_y, ramp_height):
        half_width = platform_width // 2
        r_height_per_step = ramp_height / (end_x - start_x)
        ramp_heights = np.linspace(0, ramp_height, end_x - start_x)
        for i, x in enumerate(range(start_x, end_x)):
            height_field[x, mid_y - half_width:mid_y + half_width] = ramp_heights[i]

    def add_beam(start_x, end_x, mid_y):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = beam_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0.0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    for i in range(3):  # Adding three sets of platform and ramps
        gap_length = np.random.randint(gap_min, gap_max)

        # Add Platform
        add_platform(cur_x, cur_x + platform_length, mid_y)
        goals[i * 2 + 1] = [cur_x + platform_length // 2, mid_y]
        cur_x += platform_length + gap_length

        # Add Ramp
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max + difficulty * 0.2)
        add_ramp(cur_x, cur_x + ramp_length, mid_y, ramp_height)
        goals[i * 2 + 2] = [cur_x + ramp_length // 2, mid_y]
        cur_x += ramp_length + gap_length

    # Add final beams
    for i in range(2):
        gap_length = np.random.randint(gap_min, gap_max)
        add_beam(cur_x, cur_x + beam_length, mid_y)
        goals[6 + i] = [cur_x + beam_length // 2, mid_y]
        cur_x += beam_length + gap_length

    # Add final goal behind the last obstacle
    goals[7] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals