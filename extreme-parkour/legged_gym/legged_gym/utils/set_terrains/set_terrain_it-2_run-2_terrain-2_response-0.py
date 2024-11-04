import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Multiple narrow platforms and angled beams traversing a pit for the robot to balance and jump across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform, beam dimensions and parameters
    platform_length_min = 0.7  # reduced minimum platform length
    platform_length_max = 1.2  # allow slightly longer platforms
    platform_width = np.random.uniform(0.4, 0.7)  # platforms are narrower
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.05 + 0.15 * difficulty, 0.15 + 0.35 * difficulty
    gap_length_min = 0.2 + 0.3 * difficulty
    gap_length_max = 0.4 + 0.6 * difficulty
    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_angled_beam(start_x, end_x, mid_y, direction):
        half_width = platform_width // 2
        y_range = end_x - start_x
        beam_height = np.linspace(0, np.random.uniform(platform_height_min, platform_height_max), y_range)[::direction]
        beam_height = beam_height[None, :]  # Add a dimension for broadcasting to y
        height_field[start_x:end_x, mid_y - half_width:mid_y + half_width] = beam_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.0, 0.4  # Polarity of dy will alternate
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)
    angled_beam_ratio = 0.5  # ratio of beams to platforms

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Set remaining area to be a pit
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    is_angled_beam = False  # start with platform
    for i in range(6):  # Set up 6 obstacles, alternating platforms and angled beams
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        gap_length = np.random.randint(gap_length_min, gap_length_max)

        if is_angled_beam:
            add_angled_beam(cur_x, cur_x + platform_length_max + dx, mid_y + dy, (-1) ** i)
            goals[i+1] = [cur_x + (platform_length_max + dx) / 2, mid_y + dy]
        else:
            add_platform(cur_x, cur_x + platform_length_max + dx, mid_y + dy)
            goals[i+1] = [cur_x + (platform_length_max + dx) / 2, mid_y + dy]

        is_angled_beam = not is_angled_beam
        cur_x += platform_length_max + dx + gap_length
    
    # Add final goal behind the last platform or beam
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals