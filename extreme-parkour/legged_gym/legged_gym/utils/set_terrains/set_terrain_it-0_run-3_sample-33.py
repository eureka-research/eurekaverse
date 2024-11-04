import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Stepped terrain with inclines and declines for the robot to navigate, focusing on its balance and adaptive movement."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Helper function to add a stepped incline/decline
    def add_step(start_x, height_change, step_length):
        """Adds a stepped incline or decline to the terrain."""
        end_x = start_x + step_length
        for h in range(height_change):
            step_start = start_x + m_to_idx((h / height_change) * step_length)
            step_end = step_start + m_to_idx(step_length / height_change)
            height_field[step_start:step_end, :] = h * step_increment
        return end_x

    # Parameters
    step_length = m_to_idx(1.0 - 0.5 * difficulty)
    max_step_height = 0.2 + 0.8 * difficulty
    step_increment = max_step_height / m_to_idx(length / 4)

    mid_y = m_to_idx(width) // 2

    # Flat ground (initial area)
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    current_x = spawn_length

    # Generation of stepped terrain
    num_steps = 4
    for i in range(1, num_steps + 1):
        height_change = m_to_idx((i * max_step_height) / num_steps)
        current_x = add_step(current_x, height_change, step_length)
        goals[i] = [current_x - m_to_idx(0.5 * step_length), mid_y]

    # Flat ground between steps and at the end
    flat_length = m_to_idx(1)
    height_field[current_x:current_x + flat_length, :] = height_field[current_x - 1, mid_y]
    goals[5] = [current_x + m_to_idx(flat_length / 2), mid_y]

    current_x += flat_length

    # Adding declined steps
    for i in range(1, num_steps + 1):
        height_change = m_to_idx((i * max_step_height) / num_steps)
        current_x = add_step(current_x, -height_change, step_length)
        goals[5 + i] = [current_x - m_to_idx(0.5 * step_length), mid_y]

    # Setup goals
    goals[7] = [current_x + m_to_idx(0.5), mid_y]
    height_field[current_x:, :] = height_field[current_x - 1, mid_y]

    return height_field, goals