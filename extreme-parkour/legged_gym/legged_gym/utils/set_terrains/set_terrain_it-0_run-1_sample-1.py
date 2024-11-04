import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Sloped ramps and raised walkways for the robot to climb and walk across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define ramp dimensions
    ramp_length = 1.5  # 1.5 meters long
    ramp_length = m_to_idx(ramp_length)
    ramp_width = 1.0  # 1 meter wide
    ramp_width = m_to_idx(ramp_width)
    ramp_height = 0.2 + 0.8 * difficulty  # Height varies with difficulty
    ramp_height = m_to_idx(ramp_height)

    raised_walkway_length = 2.0  # 2 meters long
    raised_walkway_length = m_to_idx(raised_walkway_length)
    raised_walkway_width = 1.0  # 1 meter wide
    raised_walkway_width = m_to_idx(raised_walkway_width)
    raised_walkway_height = 0.3 * difficulty
    raised_walkway_height = m_to_idx(raised_walkway_height)

    mid_y = m_to_idx(width / 2)
    height_flat = m_to_idx(0.0)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = height_flat
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at spawn

    cur_x = spawn_length

    def add_ramp(start_x, mid_y, ramp_length, ramp_width, ramp_height, ascending=True):
        """Add a ramp to the height field"""
        half_width = ramp_width // 2
        x1, x2 = start_x, start_x + ramp_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        if ascending:
            for i, x in enumerate(range(x1, x2)):
                height = (i / ramp_length) * ramp_height
                height_field[x, y1:y2] = height
        else:
            for i, x in enumerate(range(x1, x2)):
                height = ramp_height - (i / ramp_length) * ramp_height
                height_field[x, y1:y2] = height

    def add_raised_walkway(start_x, mid_y, walkway_length, walkway_width, walkway_height):
        """Add a raised walkway to the height field"""
        half_width = walkway_width // 2
        x1, x2 = start_x, start_x + walkway_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = walkway_height

    # Add a series of ramps and raised walkways
    for i in range(4):
        # Add ascending ramp
        add_ramp(cur_x, mid_y, ramp_length, ramp_width, ramp_height, ascending=True)
        cur_x += ramp_length

        # Place goal at the end of the ramp
        goals[2*i + 1] = [cur_x, mid_y]

        # Add raised walkway
        add_raised_walkway(cur_x, mid_y, raised_walkway_length, raised_walkway_width, raised_walkway_height)
        cur_x += raised_walkway_length

        # Place goal at the end of the raised walkway
        goals[2*i + 2] = [cur_x, mid_y]

        # Add descending ramp
        add_ramp(cur_x, mid_y, ramp_length, ramp_width, ramp_height, ascending=False)
        cur_x += ramp_length
    
    # Add the final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    return height_field, goals