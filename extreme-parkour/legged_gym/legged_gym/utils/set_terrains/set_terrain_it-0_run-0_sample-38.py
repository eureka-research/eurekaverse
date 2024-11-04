import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Series of steps and narrow beams for the robot to navigate, testing balance and precise movements."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set dimensions for steps and beams
    step_height_min = 0.05
    step_height_max = 0.4 * difficulty + 0.1
    step_length = m_to_idx(0.5)
    step_width = m_to_idx(1.0)

    beam_height = 0.3 * difficulty + 0.05
    beam_length = m_to_idx(1.5)
    beam_width = m_to_idx(0.4)  # Narrow beam

    mid_y = m_to_idx(width) // 2

    def add_step(start_x, end_x, mid_y, height):
        y1, y2 = mid_y - step_width // 2, mid_y + step_width // 2
        height_field[start_x:end_x, y1:y2] = height

    def add_beam(start_x, end_x, mid_y, height):
        y1, y2 = mid_y - beam_width // 2, mid_y + beam_width // 2
        height_field[start_x:end_x, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at spawn area

    # Variables to keep track of x position and current goal index
    cur_x = spawn_length
    goal_index = 1

    for i in range(4):  # Create 4 steps
        step_height = np.random.uniform(step_height_min, step_height_max)
        add_step(cur_x, cur_x + step_length, mid_y, step_height)
        goals[goal_index] = [cur_x + step_length // 2, mid_y]
        cur_x += step_length
        goal_index += 1

    cur_x += m_to_idx(1.0)  # Small gap between steps and beams

    for i in range(3):  # Create 3 narrow beams
        add_beam(cur_x, cur_x + beam_length, mid_y, beam_height)
        goals[goal_index] = [cur_x + beam_length // 2, mid_y]
        cur_x += beam_length
        goal_index += 1
    
    # Add final goal behind the last beam
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    return height_field, goals