import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Uneven terrain with steps of varying heights and widths to test the robot's climbing and descending capabilities."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    # Initialize height_field and goals
    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Parameters for steps
    step_length = 0.6 - 0.2 * difficulty  # Length of each step
    step_width = 3.5                      # Width of each step, spans almost entire width
    min_height = 0.05                     # Minimum height of a step
    max_height = 0.2 + 0.3 * difficulty   # Maximum height of a step

    step_length_idx = m_to_idx(step_length)
    step_width_idx = m_to_idx(step_width)

    def add_step(start_x, end_x, height):
        """Adds a step (flat region) to the height field."""
        height_field[start_x:end_x, :] = height

    spawn_length_idx = m_to_idx(2)
    goals[0] = [1, width / 2]  # First goal is near the initial spawn point

    # Ensure the starting area is flat
    height_field[0:spawn_length_idx, :] = 0

    cur_x = spawn_length_idx
    step_heights = np.linspace(min_height, max_height, 6)

    # Create steps with varying heights
    for idx, height in enumerate(step_heights):
        add_step(cur_x, cur_x + step_length_idx, height)
        
        if idx < 6:
            goals[idx + 1] = [(cur_x + step_length_idx // 2) * field_resolution, width / 2]  # Place goal in the middle of each step
        
        cur_x += step_length_idx

    # Fill the rest of the terrain with flat ground up to the end
    height_field[cur_x:, :] = 0
    goals[-1] = [min(cur_x + step_length_idx // 2, m_to_idx(length) - 1) * field_resolution, width / 2]

    return height_field, goals