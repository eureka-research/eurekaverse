import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Multiple beams, platforms, and slopes testing balance, climbing, and jumping abilities."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Dimensions configurations
    platform_width_range = [1.0, 1.6]
    beam_width_range = [0.4 + 0.1 * difficulty, 0.6 + 0.1 * difficulty]
    platform_length = m_to_idx(1.0 - 0.2 * difficulty)
    pit_depth = -1.0
    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, width, height):
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_slope(start_x, end_x, mid_y, width, height, direction):
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slant = np.linspace(0, height, num=y2-y1)[::direction]
        slant = slant[None, :]  # Add a dimension for broadcasting across x
        height_field[x1:x2, y1:y2] = slant
    
    # Initial flat area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Setting up obstacles
    cur_x = spawn_length
    segment_lengths = [platform_length, platform_length // 1.5]

    for i in range(7):  # Setting up 7 obstacles
        width = np.random.uniform(platform_width_range[0], platform_width_range[1]) if i % 2 == 0 else np.random.uniform(beam_width_range[0], beam_width_range[1])
        width = m_to_idx(width)
        section_length = segment_lengths[i % 2]
        elevated = np.random.uniform(0.0 + 0.2 * difficulty, 0.5 * difficulty) if width > m_to_idx(0.6) else np.random.uniform(0.1 * difficulty, 0.3 * difficulty)
        
        if i % 3 == 2:  # Every third obstacle is a slope
            add_slope(cur_x, cur_x + section_length, mid_y, width, elevated, direction=(-1)**i)
        else:
            add_platform(cur_x, cur_x + section_length, mid_y, width, elevated)
        
        goals[i + 1] = [cur_x + section_length / 2, mid_y]
        cur_x += section_length + m_to_idx(0.3 + 0.7 * difficulty)
        height_field[cur_x:, :] = pit_depth  # Adding a pit between obstacles

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0  # End area is flat

    return height_field, goals