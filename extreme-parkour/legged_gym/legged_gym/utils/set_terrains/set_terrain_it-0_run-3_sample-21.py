import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Series of ramps and narrow beams for the robot to ascend and descend, testing balance and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Configuring ramp and beam dimensions
    ramp_length = 2.0
    ramp_length = m_to_idx(ramp_length)
    ramp_width = 1.0
    ramp_width = m_to_idx(ramp_width)
    max_ramp_height = 0.4 * difficulty

    beam_length = 2.0
    beam_length = m_to_idx(beam_length)
    beam_width = 0.4
    beam_width = m_to_idx(beam_width)
    beam_height = 0.05
    beam_height = m_to_idx(beam_height)

    def add_ramp(start_x, end_x, start_y, height):
        for x in range(start_x, end_x):
            for y in range(start_y - ramp_width // 2, start_y + ramp_width // 2):
                height_field[x, y] = height * (x - start_x) / (end_x - start_x)

    def add_beam(start_x, end_x, mid_y):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = beam_height

    mid_y = m_to_idx(width) // 2
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(4):  # Set up 4 ramps and beams
        dx_min, dx_max = m_to_idx(0.1 - 0.05 * difficulty), m_to_idx(0.5 * difficulty)
        dx = np.random.randint(dx_min, dx_max)
        dy_min, dy_max = m_to_idx(-0.4), m_to_idx(0.4)
        dy = np.random.randint(dy_min, dy_max)

        # Add ramp
        add_ramp(cur_x, cur_x + ramp_length + dx, mid_y + dy, max_ramp_height)

        # Place goal at the end of each ramp
        goals[i*2 + 1] = [cur_x + (ramp_length + dx) / 2, mid_y + dy]

        cur_x += ramp_length + dx

        # Add beam
        dy_min, dy_max = m_to_idx(-0.2), m_to_idx(0.2)
        dy = np.random.randint(dy_min, dy_max)
        add_beam(cur_x, cur_x + beam_length, mid_y + dy)

        # Place goal at the end of each beam
        goals[i*2 + 2] = [cur_x + beam_length / 2, mid_y + dy]

        cur_x += beam_length

    # Final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals