import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Narrow beams, staggered platforms, and sideways ramps to test balance, precision, and gap traversal."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define obstacle dimensions based on difficulty
    min_beam_width = 0.4
    max_beam_width = 1.0 - 0.2 * difficulty
    min_platform_width = 1.0
    max_platform_width = 1.6 - 0.2 * difficulty
    min_ramp_height = 0.0 + 0.2 * difficulty
    max_ramp_height = 0.55 * difficulty
    gap_min = 0.2
    gap_max = 1.0 * difficulty

    mid_y = m_to_idx(width / 2)

    def add_beam(start_x, end_x, mid_y, beam_width, height):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_platform(start_x, end_x, mid_y, platform_width, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_ramp(start_x, end_x, mid_y, direction, height):
        half_width = m_to_idx(1.0) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slant_height = np.linspace(0, height, num=x2-x1)[::direction]
        slant_height = slant_height[:, None]  # Add a dimension for broadcasting to y
        height_field[x1:x2, y1:y2] = slant_height

    dx_min = m_to_idx(-0.1)
    dx_max = m_to_idx(0.1)
    dy_min = m_to_idx(0.0)
    dy_max = m_to_idx(0.4)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    # Define different types of obstacles
    num_obstacles = 6
    for i in range(num_obstacles):
        if i % 3 == 0:
            # Add beams for balance
            beam_width = np.random.uniform(min_beam_width, max_beam_width)
            beam_length = 1.0 + 0.4 * difficulty
            beam_length = m_to_idx(beam_length)
            height = np.random.uniform(min_ramp_height, max_ramp_height)
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)

            add_beam(cur_x, cur_x + beam_length + dx, mid_y + dy, m_to_idx(beam_width), height)
            goals[i+1] = [cur_x + (beam_length + dx) / 2, mid_y + dy]

            cur_x += beam_length + dx + m_to_idx(np.random.uniform(gap_min, gap_max))
        
        elif i % 3 == 1:
            # Add staggered platforms
            platform_width = np.random.uniform(min_platform_width, max_platform_width)
            platform_length = 1.5 + 0.3 * difficulty
            platform_length = m_to_idx(platform_length)
            height = np.random.uniform(min_ramp_height, max_ramp_height)
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)

            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, m_to_idx(platform_width), height)
            goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

            cur_x += platform_length + dx + m_to_idx(np.random.uniform(gap_min, gap_max))
        
        else:
            # Add ramps facing alternating directions
            ramp_length = 1.0 + 0.4 * difficulty
            ramp_length = m_to_idx(ramp_length)
            ramp_height = np.random.uniform(min_ramp_height, max_ramp_height)
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)
            direction = (-1)**i  # Alternate ramp direction

            add_ramp(cur_x, cur_x + ramp_length + dx, mid_y + dy, direction, ramp_height)
            goals[i+1] = [cur_x + (ramp_length + dx) / 2, mid_y + dy]

            cur_x += ramp_length + dx + m_to_idx(np.random.uniform(gap_min, gap_max))

    # Add final goal beyond the last obstacle
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0
    
    return height_field, goals