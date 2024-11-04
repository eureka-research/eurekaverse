import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Incorporating complex obstacles including narrow beams, sideways ramps, and elevated platforms to test precision and navigation skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Obstacle dimensions (platforms, beams, ramps)
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.3)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1 + 0.3 * difficulty, 0.2 + 0.4 * difficulty
    beam_length = platform_length / 2.0
    beam_width = m_to_idx(np.random.uniform(0.4, 0.6))
    ramp_height_min, ramp_height_max = 0.1 + 0.4 * difficulty, 0.2 + 0.5 * difficulty
    gap_length = 0.3 + 0.7 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform_or_beam(start_x, end_x, mid_y, is_beam=False):
        half_width = beam_width if is_beam else platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = height

    def add_sideways_ramp(start_x, end_x, mid_y, direction):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slope_height = np.random.uniform(ramp_height_min, ramp_height_max)
        slope = np.linspace(0, slope_height, num=y2 - y1)[::direction]
        slope = slope[None, :]  # Add a dimension for broadcasting
        height_field[x1:x2, y1:y2] = slope

    dx_min, dx_max = -0.1, 0.1
    dy_min, dy_max = -0.2, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    obstacle_types = ['platform', 'beam', 'ramp']

    for i in range(6):
        obstacle_type = np.random.choice(obstacle_types, p=[0.5, 0.25, 0.25])
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        if obstacle_type == 'platform':
            add_platform_or_beam(cur_x, cur_x + platform_length + dx, mid_y + dy)
        elif obstacle_type == 'beam':
            add_platform_or_beam(cur_x, cur_x + beam_length + dx, mid_y + dy, is_beam=True)
        elif obstacle_type == 'ramp':
            direction = (-1) ** i
            dy = dy * direction
            add_sideways_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, direction)
        
        goals[i + 1] = [cur_x + (platform_length + dx if obstacle_type != 'beam' else beam_length + dx) / 2, mid_y + dy]
        
        cur_x += (platform_length + dx if obstacle_type != 'beam' else beam_length + dx) + gap_length

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals