import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Multi-tier staircases followed by narrow beams for the robot to climb and balance on."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Staircase dimensions
    num_steps = int(3 + 3 * difficulty)
    step_height = 0.05 + 0.15 * difficulty
    step_height = m_to_idx(step_height)
    step_depth = 0.5 - 0.2 * difficulty
    step_depth = m_to_idx(step_depth)
    staircase_width = 1.2
    staircase_width = m_to_idx(staircase_width)

    # Beam dimensions
    beam_length = 1.2 - 0.4 * difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = 0.2 + 0.15 * difficulty
    beam_width = m_to_idx(beam_width)

    mid_y = m_to_idx(width) // 2

    def add_staircase(start_x, num_steps, step_height, step_depth):
        for i in range(num_steps):
            x1 = start_x + i * step_depth
            x2 = x1 + step_depth
            y1 = mid_y - staircase_width // 2
            y2 = mid_y + staircase_width // 2
            height_field[x1:x2, y1:y2] = i * step_height

    def add_beam(start_x, end_x):
        x1, x2 = start_x, end_x
        y1 = mid_y - beam_width // 2
        y2 = mid_y + beam_width // 2
        height_field[x1:x2, y1:y2] = 0.25  # Elevated enough to pose a balancing challenge

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    # Add two staircases, alternating with beams
    for i in range(2):
        # Add staircase
        add_staircase(cur_x, num_steps, step_height, step_depth)
        mid_point_stair = cur_x + (num_steps * step_depth // 2)
        goals[2*i+1] = [mid_point_stair, mid_y]

        cur_x += num_steps * step_depth
        cur_x += m_to_idx(0.5)  # Small flat area after staircase

        # Add Beam
        add_beam(cur_x, cur_x + beam_length)
        goals[2*i+2] = [cur_x + beam_length // 2, mid_y]

        cur_x += beam_length
        cur_x += m_to_idx(0.5)  # Small flat area after beam

    # Final goal area
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals