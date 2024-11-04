import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Series of slopes and ramps for the robot to climb and descend."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define slope and ramp parameters
    slope_length = 2.0 - 1.5 * difficulty  # Slope length decreases with difficulty
    slope_height = 0.1 + 0.4 * difficulty  # Slope height increases with difficulty
    slope_length_idx = m_to_idx(slope_length)
    slope_height_idx = m_to_idx(slope_height)

    ramp_length = 1.5 - 1.0 * difficulty  # Ramp length decreases with difficulty
    ramp_height = 0.05 + 0.3 * difficulty  # Ramp height increases with difficulty
    ramp_length_idx = m_to_idx(ramp_length)
    ramp_height_idx = m_to_idx(ramp_height)

    # Ensure the robot spawns on flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # First goal is set at the end of the spawn area
    goals[0] = [spawn_length - m_to_idx(0.5), m_to_idx(width / 2)]

    # Functions to add ramp and slope
    def add_slope(start_x, end_x, height):
        """Creates a slope from start_x to end_x with given maximum height."""
        x_range = np.linspace(0, 1, end_x - start_x)
        slope_height = np.sin(x_range * np.pi) * height  # Sine wave for smooth slopes
        for x in range(start_x, end_x):
            height_field[x, :] = slope_height[x - start_x]

    def add_ramp(start_x, end_x, height):
        """Creates a linear ramp from start_x to end_x with given height."""
        for x in range(start_x, end_x):
            height_field[x, :] = ((x - start_x) / (end_x - start_x)) * height

    # Placing slopes and ramps
    cur_x = spawn_length
    num_obstacles = 6  # Number of slopes and ramps

    for i in range(1, num_obstacles + 1):
        if i % 2 == 0:
            # Add a ramp
            add_ramp(cur_x, cur_x + ramp_length_idx, ramp_height)
            goals[i] = [cur_x + ramp_length_idx // 2, m_to_idx(width / 2)]
            cur_x += ramp_length_idx
        else:
            # Add a slope
            add_slope(cur_x, cur_x + slope_length_idx, slope_height)
            goals[i] = [cur_x + slope_length_idx // 2, m_to_idx(width / 2)]
            cur_x += slope_length_idx

    # Set final goal at the end of the last obstacle
    goals[-1] = [cur_x + m_to_idx(0.5), m_to_idx(width / 2)]
    height_field[cur_x:, :] = 0

    return height_field, goals