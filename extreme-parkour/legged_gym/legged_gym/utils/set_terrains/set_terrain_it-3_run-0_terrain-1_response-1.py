import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """A mix of platforms, narrow beams, and side ramps to test the quadruped's balance, coordination, and jumping abilities."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform and obstacle parameters
    platform_length = 1.0 - 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(1.0, 1.2)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.2 + 0.3 * difficulty
    gap_length = 0.2 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    beam_length = 1.5 - 0.4 * difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = 0.3 - 0.1 * difficulty
    beam_width = m_to_idx(beam_width)

    ramp_height_min, ramp_height_max = 0.1 + 0.3 * difficulty, 0.2 + 0.4 * difficulty
    ramp_slope = 0.1 + 0.2 * difficulty

    mid_y = m_to_idx(width) // 2
    spawn_length = m_to_idx(2)

    # Helper functions to add different obstacles
    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_beam(start_x, end_x, mid_y):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = platform_height_max
        
    def add_ramp(start_x, end_x, mid_y, direction):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        slant = np.linspace(0, direction * ramp_height, num=y2-y1)[:, None]
        height_field[x1:x2, y1:y2] = slant

    # Set spawn area to flat ground
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Set remaining area to be a pit for jumping obstacles
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    for i in range(6):
        # Randomly choose between platform, beam, and ramp
        obstacle_type = random.choice(["platform", "beam", "ramp"])
        if obstacle_type == "platform":
            height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, cur_x + platform_length, mid_y, height)
            goals[i + 1] = [cur_x + platform_length // 2, mid_y]
            cur_x += platform_length + gap_length
        elif obstacle_type == "beam":
            add_beam(cur_x, cur_x + beam_length, mid_y)
            goals[i + 1] = [cur_x + beam_length // 2, mid_y]
            cur_x += beam_length + gap_length
        elif obstacle_type == "ramp":
            direction = random.choice([-1, 1])
            add_ramp(cur_x, cur_x + platform_length, mid_y, direction)
            goals[i + 1] = [cur_x + platform_length // 2, mid_y]
            cur_x += platform_length + gap_length
    
    # Add final goal behind the last obstacle and fill the remaining area with flat ground
    goals[7] = [m_to_idx(length) - m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals