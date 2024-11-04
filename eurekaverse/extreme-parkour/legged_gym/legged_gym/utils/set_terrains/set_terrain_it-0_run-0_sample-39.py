import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """A series of narrow and wide ramps to test the robot's balance and climbing skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set dimensions for ramps and gaps
    ramp_length_min, ramp_length_max = 0.8, 1.2
    ramp_width_min, ramp_width_max = 0.4, 1.6
    ramp_height_min, ramp_height_max = 0.05, 0.25

    gap_length = 0.1 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_ramp(start_x, ramp_length, ramp_width, height):
        half_width = ramp_width // 2
        x1, x2 = start_x, start_x + ramp_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(6):  # Set up 6 ramps
        ramp_length = np.random.uniform(ramp_length_min, ramp_length_max) - (0.2 * difficulty)
        ramp_length = m_to_idx(ramp_length)
        ramp_width = np.random.uniform(ramp_width_min, ramp_width_max) - (0.3 * difficulty)
        ramp_width = m_to_idx(ramp_width)
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max) * difficulty
        
        add_ramp(cur_x, ramp_length, ramp_width, ramp_height)

        # Set goal in the center of the ramp
        goals[i+1] = [cur_x + ramp_length // 2, mid_y]

        # Add gap
        cur_x += ramp_length + gap_length

    # Add final goal behind the last ramp, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals