import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Mixed terrain with step heights and narrow balance beams for the robot to navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up step heights
    base_step_height = 0.05 + 0.2 * difficulty
    height_variation = 0.1 * difficulty
    step_width = 1.0
    step_width = m_to_idx(step_width)
    
    # Set up narrow balance beams
    beam_width = 0.4
    beam_width = m_to_idx(beam_width)
    
    mid_y = m_to_idx(width) // 2

    def add_step_row(start_x, end_x, mid_y, step_height):
        height_field[start_x:end_x, :] = step_height

    def add_balance_beam(start_x, end_x, mid_y):
        half_beam_width = beam_width // 2
        y1, y2 = mid_y - half_beam_width, mid_y + half_beam_width
        height_field[start_x:end_x, y1:y2] = base_step_height + height_variation  # Beam is raised

    # Initial flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    current_goal = 1

    # First set of steps
    step_length = 1.0
    step_length = m_to_idx(step_length)
    for i in range(3):
        step_height = base_step_height + (i * height_variation)
        add_step_row(cur_x, cur_x + step_length, mid_y, step_height)
        goals[current_goal] = [cur_x + step_length // 2, mid_y]
        cur_x += step_length
        current_goal += 1

    # Next, a narrow beam
    balance_beam_length = 2.0
    balance_beam_length = m_to_idx(balance_beam_length)
    add_balance_beam(cur_x, cur_x + balance_beam_length, mid_y)
    goals[current_goal] = [cur_x + balance_beam_length // 2, mid_y]
    cur_x += balance_beam_length
    current_goal += 1

    # Another set of steps on the other side
    for i in range(3):
        step_height = base_step_height + ((2 - i) * height_variation)
        add_step_row(cur_x, cur_x + step_length, mid_y, step_height)
        goals[current_goal] = [cur_x + step_length // 2, mid_y]
        cur_x += step_length
        current_goal += 1

    # End flat ground as end goal
    height_field[cur_x:, :] = 0
    goals[current_goal] = [cur_x + m_to_idx(0.5), mid_y]

    return height_field, goals