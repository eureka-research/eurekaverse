import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Narrow beams and alternate height platforms for challenging balance and jump skill."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up narrow beam dimensions
    beam_length = 1.0 - 0.3 * difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = np.random.uniform(0.4, 0.6)
    beam_width = m_to_idx(beam_width)
    beam_height_min, beam_height_max = 0.2 * difficulty, 0.4 * difficulty
    gap_length = 0.2 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, mid_y, height):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_platform(start_x, end_x, mid_y, height):
        platform_width = m_to_idx(1.0)  
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_variation = 0.2
    dy_variation = m_to_idx(dy_variation)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Set first goal at spawn area
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Set remaining area to be a pit
    # We do this to force the robot to jump from platform to platform
    # Otherwise, the robot can just jump down and climb back up
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    alternating_height = beam_height_min

    # Add beams and platforms alternately
    for i in range(6):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(-dy_variation, dy_variation)

        if i % 2 == 0:  # Add beam
            beam_height = alternating_height
            add_beam(cur_x, cur_x + beam_length + dx, mid_y + dy, beam_height)
            goals[i+1] = [cur_x + (beam_length + dx) / 2, mid_y + dy]
            alternating_height = beam_height_min if alternating_height == beam_height_max else beam_height_max
        else:  # Add platform
            platform_height = alternating_height
            add_platform(cur_x, cur_x + beam_length + dx, mid_y + dy, platform_height)
            goals[i+1] = [cur_x + (beam_length + dx) / 2, mid_y + dy]
            alternating_height = beam_height_min if alternating_height == beam_height_max else beam_height_max

        # Add gap
        cur_x += beam_length + dx + gap_length

    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals