import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Alternating slopes and stairs ascending to a final goal."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    length_idx = m_to_idx(length)
    width_idx = m_to_idx(width)
    mid_y = width_idx // 2

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # Initial goal at spawn point
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Obstacle configurations
    slope_length = m_to_idx(1.0)  # length of each slope
    stair_length = m_to_idx(0.5)  # length of each stair segment
    max_slope_height = 0.1 + 0.3 * difficulty  # maximum height of the slope
    step_height = 0.05 + 0.2 * difficulty  # height of each stair step

    # Create first slope
    slope_start_x = spawn_length
    slope_end_x = slope_start_x + slope_length
    slope_height = np.linspace(0, max_slope_height, slope_length)
    for i in range(slope_length):
        height_field[slope_start_x + i, :] = slope_height[i]

    # First goal at end of first slope
    goals[1] = [slope_end_x - m_to_idx(0.5), mid_y]

    # Create first set of stairs
    stair_start_x = slope_end_x
    stair_end_x = stair_start_x + stair_length
    num_steps = stair_length
    for i in range(num_steps):
        height_field[stair_start_x + i, :] = max_slope_height + i * step_height

    # Second goal at top of the first stairs
    goals[2] = [stair_end_x - m_to_idx(0.25), mid_y]

    # Create second slope
    slope_start_x = stair_end_x
    slope_end_x = slope_start_x + slope_length
    max_slope_height = max_slope_height + step_height * num_steps
    slope_height = np.linspace(height_field[slope_start_x, 0], max_slope_height, slope_length)
    for i in range(slope_length):
        height_field[slope_start_x + i, :] = slope_height[i]

    # Third goal at end of second slope
    goals[3] = [slope_end_x - m_to_idx(0.5), mid_y]

    # Create second set of stairs
    stair_start_x = slope_end_x
    stair_end_x = stair_start_x + stair_length
    num_steps = stair_length
    for i in range(num_steps):
        height_field[stair_start_x + i, :] = max_slope_height + i * step_height

    # Fourth goal at top of the second stairs
    goals[4] = [stair_end_x - m_to_idx(0.25), mid_y]

    # Create final slope to the last goal
    slope_start_x = stair_end_x
    slope_end_x = min(length_idx, slope_start_x + slope_length)
    max_slope_height = max_slope_height + step_height * num_steps
    slope_height = np.linspace(height_field[slope_start_x, 0], max_slope_height, slope_end_x - slope_start_x)
    for i in range(slope_end_x - slope_start_x):
        height_field[slope_start_x + i, :] = slope_height[i]

    # Place the remaining goals
    goals[5] = [slope_end_x - m_to_idx(0.5), mid_y]
    
    final_goal_x = min(length_idx - 1, slope_end_x + m_to_idx(2))
    height_field[slope_end_x:final_goal_x, :] = max_slope_height

    goals[6] = [final_goal_x - m_to_idx(1), mid_y]
    goals[7] = [final_goal_x - m_to_idx(0.5), mid_y]

    return height_field, goals