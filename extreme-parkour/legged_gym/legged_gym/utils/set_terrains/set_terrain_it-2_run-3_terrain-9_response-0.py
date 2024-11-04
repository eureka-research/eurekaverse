import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Platforms, ramps, and narrow beams for complex navigation tasks."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define obstacle parameters based on difficulty
    platform_length = 1.0 - 0.3 * difficulty  # meters
    platform_length_idx = m_to_idx(platform_length)
    ramp_width = np.random.uniform(1.0, 1.1)  # Less width for ramps
    ramp_width_idx = m_to_idx(ramp_width)
    platform_height_min, platform_height_max = 0.2 * difficulty, 0.25 * difficulty
    gap_length_min, gap_length_max = 0.1, 0.4 * difficulty  # Variable gap lengths
    beam_width = np.random.uniform(0.4, 0.6)  # Narrow beams for high difficulty
    beam_width_idx = m_to_idx(beam_width)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = m_to_idx(1.0) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_ramp(start_x, end_x, mid_y):
        half_width = ramp_width_idx // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = random.uniform(platform_height_min, platform_height_max)
        slope = np.linspace(0, ramp_height, x2 - x1)
        height_field[x1:x2, y1:y2] = slope[:, None]

    def add_beam(start_x, mid_y):
        half_width = beam_width_idx // 2
        x1, x2 = start_x, start_x + m_to_idx(1.0)
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = random.uniform(platform_height_min, platform_height_max)

    # Setup the flat ground for the spawn area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0.0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    num_obstacles = 6

    for i in range(num_obstacles):
        # Probabilistically decide whether to place a platform, ramp, or beam.
        obstacle_type = random.choices(['platform', 'ramp', 'beam'], [0.4, 0.4, 0.2])[0]

        if obstacle_type == 'platform':
            platform_height = random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, cur_x + platform_length_idx, mid_y, platform_height)
            goals[i + 1] = [cur_x + platform_length_idx / 2, mid_y]
            cur_x += platform_length_idx + random.randint(m_to_idx(gap_length_min), m_to_idx(gap_length_max))

        elif obstacle_type == 'ramp':
            ramp_length = platform_length_idx
            add_ramp(cur_x, cur_x + ramp_length, mid_y)
            goals[i + 1] = [cur_x + ramp_length / 2, mid_y]
            cur_x += ramp_length + random.randint(m_to_idx(gap_length_min), m_to_idx(gap_length_max))

        elif obstacle_type == 'beam':
            add_beam(cur_x, mid_y)
            goals[i + 1] = [cur_x + m_to_idx(0.5), mid_y]
            cur_x += m_to_idx(1.0) + random.randint(m_to_idx(gap_length_min), m_to_idx(gap_length_max))

    # Final goal at the end, ensuring the course tries to fully utilize the provided length.
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0.0

    return height_field, goals