import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Combination of side ramps, platforms, and narrow beams to test precision, balance, and agility."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    mid_y = m_to_idx(width) // 2
    
    # General obstacle dimensions
    platform_length = m_to_idx(1.2 - 0.3 * difficulty)
    platform_width = m_to_idx(np.random.uniform(1.0, 1.5))
    platform_height_min = 0.1 + 0.2 * difficulty
    platform_height_max = 0.2 + 0.3 * difficulty

    ramp_slope = np.linspace(0, m_to_idx(0.4 + 0.4 * difficulty), platform_width)
    beam_width = m_to_idx(0.4)
    beam_length = m_to_idx(1.5)
    gap_length = m_to_idx(0.1 + 0.5 * difficulty)

    def add_platform(start_x, end_x, y, height):
        """Add a rectangular platform."""
        half_width = platform_width // 2
        height_field[start_x:end_x, y - half_width:y + half_width] = height

    def add_ramp(start_x, mid_y, direction=1):
        """Add a ramp oriented as specified by direction (1 indicates upwards, -1 indicates downwards)."""
        half_width = platform_width // 2
        ramp_height = np.random.uniform(platform_height_min, platform_height_max)
        ramp = np.outer(np.linspace(0, direction * ramp_height, platform_length), np.ones(2 * half_width))
        height_field[start_x:start_x + platform_length, mid_y - half_width:mid_y + half_width] = ramp

    def add_beam(start_x, end_x, y, height):
        """Add a narrow beam."""
        half_width = beam_width // 2
        height_field[start_x:end_x, y - half_width:y + half_width] = height

    # Initialize flat spawn area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]
    
    cur_x = spawn_length

    for i in range(3):
        # Alternating between platforms and ramps
        if i % 2 == 0:
            platform_height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)
            goals[i + 1] = [cur_x + platform_length // 2, mid_y]
        else:
            direction = (-1)**i  # Alternate ramp direction (upwards/downwards)
            add_ramp(cur_x, mid_y, direction)
            goals[i + 1] = [cur_x + platform_length // 2, mid_y]
        
        cur_x += platform_length + gap_length
    
    # Add beams in between ramps
    for j in range(3, 5):
        add_beam(cur_x, cur_x + beam_length, mid_y, 0)
        goals[j + 1] = [cur_x + beam_length // 2, mid_y]
        cur_x += beam_length + gap_length

    # Add final platform leading to the last goal
    final_platform_height = np.random.uniform(platform_height_min, platform_height_max)
    add_platform(cur_x, cur_x + platform_length, mid_y, final_platform_height)
    goals[-1] = [cur_x + platform_length // 2, mid_y]

    return height_field, goals