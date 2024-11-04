import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Tilted platforms and narrow beams for the robot to balance and climb."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Parameters for obstacles
    platform_width = 0.6  # width in meters for narrow beams
    platform_height_base = 0.1  # base height for platforms
    platform_height_incr = 0.1 * difficulty  # height increment based on difficulty
    gap_length_base = 0.2  # base gap length in meters
    gap_length_incr = 0.1 * difficulty  # gap length increment based on difficulty
    
    def add_platform(start_x, end_x, y_center, tilt_direction=0):
        """
        Adds a tilted platform to the height_field.
        """
        width_idx = m_to_idx(platform_width)
        half_width = width_idx // 2
        x1, x2 = start_x, end_x
        y1, y2 = y_center - half_width, y_center + half_width
        height = platform_height_base + platform_height_incr * difficulty
        if tilt_direction != 0:
            # Create a linear gradient for the tilt
            slope = np.linspace(0, height, y2 - y1) * tilt_direction
            for i in range(x1, x2):
                height_field[i, y1:y2] = slope
        else:
            height_field[x1:x2, y1:y2] = height

    mid_y = m_to_idx(width) // 2
    spawn_length = m_to_idx(2)
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Set spawn area to flat ground
    height_field[0:spawn_length, :] = 0

    cur_x = spawn_length
    segments = 7  # Number of segments including both platforms and beams

    for i in range(segments):
        tilt_direction = (-1) ** i  # Alternate tilt direction
        segment_length = np.random.uniform(0.8, 1.2)  # length of each segment in meters
        segment_length_idx = m_to_idx(segment_length)
        add_platform(cur_x, cur_x + segment_length_idx, mid_y, tilt_direction)
        
        # Set goal in the middle of the segment
        goals[i+1] = [cur_x + segment_length_idx // 2, mid_y]
        
        # Add gap between segments
        gap_length = gap_length_base + gap_length_incr
        cur_x += segment_length_idx + m_to_idx(gap_length)
    
    # Add final goal at the end
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals
