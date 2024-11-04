import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """A series of hurdles each with varying heights for the robot to jump over."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # Starting position for the quadruped
    starting_x = spawn_length
    mid_y = m_to_idx(width/2)

    # Set first goal
    goals[0] = [starting_x, mid_y]

    # Dimensions for hurdles
    hurdle_height_min = 0.1 * difficulty  # Minimum height of hurdles
    hurdle_height_max = 0.4 * difficulty  # Maximum height of hurdles
    hurdle_width = m_to_idx(1)  # 1 meter width
    hurdle_gap_min = m_to_idx(0.5 + 0.5 * difficulty) # Minimum gap between hurdles
    hurdle_gap_max = m_to_idx(1 + 1 * difficulty) # Maximum gap between hurdles

    num_hurdles = 6  # Number of hurdles to place

    for i in range(1, num_hurdles+1):
        # Randomly determine the height of the hurdle
        height = np.random.uniform(hurdle_height_min, hurdle_height_max)

        # Place the hurdle at the current position
        height_field[starting_x:starting_x + hurdle_width, :] = height

        # Set the goal location just before the start of the next hurdle
        goals[i] = [starting_x + hurdle_width + hurdle_gap_min//2, mid_y]

        # Move starting_x to the position after the gap
        starting_x += hurdle_width + np.random.randint(hurdle_gap_min, hurdle_gap_max)

    # Final goal, positioned at the end of the terrain.
    goals[-1] = [m_to_idx(length - 1), mid_y]

    return height_field, goals