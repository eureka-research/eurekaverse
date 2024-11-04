import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Obstacle course with raised platforms, narrow beams, and sloped ramps for a balance of jumping, climbing, and balancing skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Adjust course parameters based on difficulty
    platform_length = m_to_idx(1.0 - 0.3 * difficulty)
    platform_width = m_to_idx(random.uniform(0.4, 0.8))
    beam_length = m_to_idx(1.0)
    beam_width = m_to_idx(0.2)  # Narrower beam for balancing
    ramp_length = m_to_idx(1.5)
    gap_length = m_to_idx(0.3 + 0.5 * difficulty)
    platform_height_min = 0.2 * difficulty
    platform_height_max = 0.5 * difficulty
    ramp_height_max = 0.5 * difficulty

    mid_y = m_to_idx(width / 2)
    
    def add_platform(start_x, end_x, mid_y, width):
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_beam(start_x, end_x, mid_y):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = np.random.uniform(platform_height_min, platform_height_max)

    def add_ramp(start_x, end_x, mid_y, direction):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(0.2, ramp_height_max)
        slant = np.linspace(0, ramp_height, num=end_x - start_x)[::direction]
        height_field[x1:x2, y1:y2] = slant[:, None]  # Gradual incline or decline

    dx_min, dx_max = m_to_idx(-0.1), m_to_idx(0.1)
    dy_min, dy_max = m_to_idx(-0.4), m_to_idx(0.4)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(6):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        if i % 3 == 0:
            add_platform(cur_x, cur_x + platform_length, mid_y + dy, platform_width)
            goals[i + 1] = [cur_x + platform_length // 2, mid_y + dy]
            cur_x += platform_length + gap_length
        elif i % 3 == 1:
            add_beam(cur_x, cur_x + beam_length, mid_y + dy)
            goals[i + 1] = [cur_x + beam_length // 2, mid_y + dy]
            cur_x += beam_length + gap_length
        else:
            direction = 1 if i % 2 == 0 else -1
            add_ramp(cur_x, cur_x + ramp_length, mid_y + dy, direction)
            goals[i + 1] = [cur_x + ramp_length // 2, mid_y + dy]
            cur_x += ramp_length + gap_length

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0
    
    return height_field, goals