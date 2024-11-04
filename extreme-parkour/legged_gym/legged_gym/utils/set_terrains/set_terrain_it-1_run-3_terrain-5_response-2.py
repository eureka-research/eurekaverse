import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Complex mix of angled ramps, narrow beams, platforms, and gaps for advanced challenges."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Obstacle segments (platforms, ramps, beams, gaps) dimensions based on difficulty
    platform_length = m_to_idx(1.2 - 0.4 * difficulty)
    platform_width = np.random.uniform(0.8, 1.2) # Narrower platforms
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 * difficulty, 0.4 * difficulty

    beam_length = m_to_idx(2.0 - 0.5 * difficulty)
    beam_width = m_to_idx(0.4)  # Narrow beam width
    beam_height_min, beam_height_max = 0.2 * difficulty, 0.5 * difficulty

    ramp_length = m_to_idx(1.0)
    ramp_height_min, ramp_height_max = 0.1 + 0.4 * difficulty, 0.2 + 0.6 * difficulty

    gap_length = m_to_idx(0.2 + 0.6 * difficulty)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_ramp(start_x, end_x, mid_y, up):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        slant = np.linspace(0, ramp_height, num=x2-x1) if up else np.linspace(ramp_height, 0, num=x2-x1)
        height_field[x1:x2, y1:y2] = slant[:, None]  # Broadcast to y dimension

    def add_beam(start_x, end_x, mid_y):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        beam_height = np.random.uniform(beam_height_min, beam_height_max)
        height_field[x1:x2, y1:y2] = beam_height

    dx_min, dx_max = -0.1, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)
    dy_flip = 1  # Variable to alternate y direction

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Set remaining area to be a pit
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    num_obstacles = 7  # Total obstacles to fit within the length
    
    for i in range(num_obstacles - 1):  # Create combined segments (platform, ramps, beams)
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max) * dy_flip
        dy_flip *= -1 # Alternative y direction

        if i % 3 == 0:
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i + 1] = [cur_x + (platform_length + dx) // 2, mid_y + dy]
        elif i % 3 == 1:
            add_ramp(cur_x, cur_x + ramp_length + dx, mid_y + dy, up=(i % 6 != 4))
            goals[i + 1] = [cur_x + (ramp_length + dx) // 2, mid_y + dy]
        elif i % 3 == 2:
            add_beam(cur_x, cur_x + beam_length + dx, mid_y + dy)
            goals[i + 1] = [cur_x + (beam_length + dx) // 2, mid_y + dy]

        cur_x += m_to_idx(dx) + m_to_idx(gap_length)
    
    # Add final goal behind the last obstacle, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals