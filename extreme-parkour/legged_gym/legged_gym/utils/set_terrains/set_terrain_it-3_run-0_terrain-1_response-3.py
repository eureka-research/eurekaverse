import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Combines alternating ramps, narrow beams, and platforms to test the robot's balance and climbing skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length = m_to_idx(1.0 - 0.3 * difficulty)
    platform_width = m_to_idx(1.0 + 0.3 * difficulty)
    platform_height_min, platform_height_max = 0.1 * difficulty, 0.3 * difficulty

    gap_length = m_to_idx(0.5 * difficulty)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, height, width_offset):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width + width_offset, mid_y + half_width + width_offset
        height_field[x1:x2, y1:y2] = height

    def add_ramp(start_x, end_x, height, incline=True):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        if incline:
            slant = np.linspace(0, height, num=x2-x1)[None, :]
        else:
            slant = np.linspace(height, 0, num=x2-x1)[None, :]
        height_field[x1:x2, y1:y2] = slant

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    current_x = spawn_length
    steps = 4
    ramps = 2
    
    for i in range(steps):
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        add_platform(current_x, current_x + platform_length, platform_height, 0)
        goals[i+1] = [current_x + platform_length // 2, mid_y]
        current_x += platform_length + gap_length

    for i in range(ramps):
        ramp_height = np.random.uniform(platform_height_min, platform_height_max)
        add_ramp(current_x, current_x + platform_length, ramp_height, incline=(i % 2 == 0))
        goals[steps+i+1] = [current_x + platform_length // 2, mid_y]
        current_x += platform_length + gap_length

    # Add final goal at the end
    goals[-1] = [m_to_idx(11.5), mid_y]
    height_field[m_to_idx(11):, :] = 0

    return height_field, goals