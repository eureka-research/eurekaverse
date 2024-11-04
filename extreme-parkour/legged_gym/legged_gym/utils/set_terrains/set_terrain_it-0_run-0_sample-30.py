import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """A combination of elevated and recessed stepping stones for the robot to traverse."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Obstacle specifications
    step_length = 0.75
    step_length = m_to_idx(step_length)
    step_width = 0.8
    step_width = m_to_idx(step_width)
    step_height_min = 0.05 + 0.1 * difficulty
    step_height_max = 0.15 + 0.3 * difficulty
    step_gap = 0.2 + 0.5 * difficulty
    step_gap = m_to_idx(step_gap)

    mid_y = m_to_idx(width) // 2

    def add_step(x, y, height):
        """Add a step at location (x, y) with given height"""
        half_width = step_width // 2
        x1, x2 = x, x + step_length
        y1, y2 = y - half_width, y + half_width
        height_field[x1:x2, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Initial step down (negative height) to force descent initially
    initial_step = -0.15 - 0.2 * difficulty
    height_field[spawn_length:m_to_idx(3), :] = initial_step
    goals[1] = [m_to_idx(2.5), mid_y]

    cur_x = m_to_idx(3)
    for i in range(5):  # Create 5 steps
        step_height = np.random.uniform(step_height_min, step_height_max)
        add_step(cur_x, mid_y, step_height)

        # Place a goal at each step
        goals[i + 2] = [cur_x + step_length / 2, mid_y]

        # Add gap between steps
        cur_x += step_length + step_gap

    # Last step up and then back to ground level
    final_step_height = np.random.uniform(step_height_min, step_height_max)
    add_step(cur_x, mid_y, final_step_height)
    goals[7] = [cur_x + step_length + m_to_idx(0.5), mid_y]

    # Ground level after last step
    height_field[cur_x + step_length:, :] = 0

    return height_field, goals