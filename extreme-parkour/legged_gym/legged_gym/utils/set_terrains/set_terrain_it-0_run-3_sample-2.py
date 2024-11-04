import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Ramps, narrow passages, and elevated platforms to simulate urban challenges."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    mid_y = m_to_idx(width) // 2

    # Set first goal at the spawn point
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Define ramp and passage parameters
    ramp_length = max(1.0, 1.5 - 0.5 * difficulty)  # Decrease ramp length with difficulty
    ramp_length = m_to_idx(ramp_length)
    ramp_height = np.linspace(0, 0.25 + 0.35 * difficulty, ramp_length)  # Incline increases with difficulty
    
    narrow_passage_width = np.random.uniform(0.4, 0.5) + difficulty * 0.3  # Make narrower with higher difficulty
    narrow_passage_width = m_to_idx(narrow_passage_width)

    # Platform parameters
    platform_height = 0.2 + 0.2 * difficulty
    platform_length = m_to_idx(1.0)
    platform_width = m_to_idx(1.0)

    def add_ramp(start_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, start_x + ramp_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = ramp_height[:, np.newaxis]

    def add_passage(start_x, mid_y):
        half_width = narrow_passage_width // 2
        x1, x2 = start_x, start_x + platform_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height_field[x1 - 1, y1]  # Continue from the previous height

    def add_platform(start_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, start_x + platform_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = platform_height

    # Initialize current x position just after spawn area
    cur_x = spawn_length

    # Add ramp
    add_ramp(cur_x, mid_y)
    goals[1] = [cur_x + ramp_length // 2, mid_y]  # Middle of the first ramp
    cur_x += ramp_length
    
    # Add passage
    add_passage(cur_x, mid_y)
    goals[2] = [cur_x + platform_length // 2, mid_y]  # Middle of the narrow passage
    cur_x += platform_length

    # Add platform
    add_platform(cur_x, mid_y)
    goals[3] = [cur_x + platform_length // 2, mid_y]  # Middle of the platform
    cur_x += platform_length

    for i in range(4, 8):
        if i % 2 == 0:
            # Alternate between ramp and platform
            add_ramp(cur_x, mid_y)
            goals[i] = [cur_x + ramp_length // 2, mid_y]
            cur_x += ramp_length
        else:
            add_platform(cur_x, mid_y)
            goals[i] = [cur_x + platform_length // 2, mid_y]
            cur_x += platform_length

    return height_field, goals