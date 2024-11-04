import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Dynamic sideways ramps, moving platforms, and variable height steps for diverse skill training and increased difficulty."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform and ramp dimensions
    platform_length = 0.7 + 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.4, 0.6)  # Narrower platforms
    platform_width = m_to_idx(platform_width)
    gap_length = 0.4 + 0.6 * difficulty  # Wider gaps to increase difficulty
    gap_length = m_to_idx(gap_length)

    ramp_height_min, ramp_height_max = 0.1 * difficulty, 0.4 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, length, height, y_offset=0):
        half_width = platform_width // 2
        x2 = start_x + length
        y1, y2 = mid_y + y_offset - half_width, mid_y + y_offset + half_width
        height_field[start_x:x2, y1:y2] = height

    def add_ramp(start_x, length, height, y_offset=0, direction=1):
        half_width = platform_width // 2
        x2 = start_x + length
        y1, y2 = mid_y + y_offset - half_width, mid_y + y_offset + half_width
        ramp = np.linspace(0, height, num=x2-start_x)[::direction]
        height_field[start_x:x2, y1:y2] = ramp[:, None]

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn location
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length

    # Add some dynamic sideways ramps and alternating level platforms
    for i in range(4):
        platform_height = np.random.uniform(ramp_height_min, ramp_height_max)
        ramp_direction = (-1)**i  # Alternate ramp directions
        y_offset = ramp_direction * m_to_idx(0.5)
        
        add_ramp(cur_x, platform_length, platform_height, y_offset, ramp_direction)
        goals[i+1] = [cur_x + platform_length // 2, mid_y + y_offset]
        cur_x += platform_length + gap_length

    # Adding moving platforms
    moving_platforms = 2
    movement_amplitude = m_to_idx(0.3)
    for p in range(moving_platforms):
        avg_movement = np.sin(np.linspace(0, np.pi, platform_length))
        avg_movement = movement_amplitude * avg_movement - movement_amplitude / 2
        for j in range(platform_length):
            y_movement = avg_movement[j]
            add_platform(cur_x + j, 1, platform_height, y_movement)
        goals[4+p] = [cur_x + platform_length // 2, mid_y]
        cur_x += platform_length + gap_length

    # Finish with flat platforms
    for k in range(2):
        add_platform(cur_x, platform_length, platform_height)
        goals[6+k] = [cur_x + platform_length // 2, mid_y]
        cur_x += platform_length + gap_length

    height_field[cur_x:, :] = 0

    return height_field, goals