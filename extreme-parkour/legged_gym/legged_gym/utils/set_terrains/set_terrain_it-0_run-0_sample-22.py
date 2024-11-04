import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """A sequence of hurdles and ramps for the robot to climb over and navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Defining obstacles parameters
    hurdle_height = 0.1 + 0.3 * difficulty  # Height of hurdles
    hurdle_width = 1.0  # Width of each hurdle
    hurdle_gap_min = 0.4  # Minimum gap between hurdles
    hurdle_gap_max = 0.8 # Maximum gap between hurdles

    ramp_length = 1.0
    ramp_height = 0.05 + 0.2 * difficulty  # Height of ramps based on difficulty

    mid_y = m_to_idx(width) // 2

    def add_hurdle(start_x, mid_y):
        """Adds a hurdle obstacle."""
        x1, x2 = start_x, start_x + m_to_idx(hurdle_width)
        half_width = m_to_idx(hurdle_width) // 2
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = hurdle_height

    def add_ramp(start_x, mid_y, ascending=True):
        """Adds a ramp obstacle."""
        length = m_to_idx(ramp_length)
        half_width = m_to_idx(hurdle_width) // 2
        y1, y2 = mid_y - half_width, mid_y + half_width
        for offset, x in enumerate(range(start_x, start_x + length)):
            height = offset / length * ramp_height if ascending else ramp_height - (offset / length * ramp_height)
            height_field[x, y1:y2] = height

    # Initialize spawn area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # First goal at the spawn area
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    goal_count = 1

    # Create sequences of hurdles and ramps
    while cur_x < m_to_idx(length) - m_to_idx(2) and goal_count < 8:
        # Add hurdle
        add_hurdle(cur_x, mid_y)
        cur_x += m_to_idx(hurdle_width)
        # Place goal after hurdle
        goals[goal_count] = [cur_x + m_to_idx(0.5), mid_y]
        goal_count += 1
        
        # Add random gap
        cur_x += m_to_idx(random.uniform(hurdle_gap_min, hurdle_gap_max))

        # Add ramp (alternating ascending and descending)
        add_ramp(cur_x, mid_y, ascending=(goal_count % 2 == 1))
        cur_x += m_to_idx(ramp_length)
        # Place goal after ramp
        goals[goal_count] = [cur_x + m_to_idx(0.5), mid_y]
        goal_count += 1

        # Add random gap
        cur_x += m_to_idx(random.uniform(hurdle_gap_min, hurdle_gap_max))

    # Add final goal at the end of terrain if not already filled
    if goal_count < 8:
        goals[goal_count:] = [[m_to_idx(length) - m_to_idx(0.5), mid_y]] * (8 - goal_count)

    return height_field, goals