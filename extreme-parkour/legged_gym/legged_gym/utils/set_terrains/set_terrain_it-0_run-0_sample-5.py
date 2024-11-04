import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Hurdles and stepping stones, requiring the quadruped to climb and navigate narrow paths."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define segment dimensions
    hurdle_width = 1.0      # Width of each hurdle
    hurdle_gap = 0.2 + 0.8 * difficulty  # Gap between hurdles, more challenging with more difficulty
    hurdle_height = 0.1 + 0.4 * difficulty  # Height of hurdles
    platform_width = 0.45 + 0.3 * difficulty  # Narrow platforms, harder at higher difficulty

    hurdle_width_idx = m_to_idx(hurdle_width)
    hurdle_gap_idx = m_to_idx(hurdle_gap)
    platform_width_idx = m_to_idx(platform_width)
    hurdle_height_idx = m_to_idx(hurdle_height)

    mid_y = m_to_idx(width) // 2

    def add_hurdle(x, height):
        """Adds hurdles across the width of the terrain."""
        height_field[x:x+hurdle_width_idx, :] = height

    def add_stepping_stones(x_start, y_mid, count, stair_type="ascend"):
        """Adds stepping stones in a sequential narrow path."""
        y_offset = m_to_idx(0.5) * (-1 if stair_type == "ascend" else 1)
        for i in range(count):
            x = x_start + i * (platform_width_idx + hurdle_gap_idx)
            y = y_mid - (i * y_offset)
            height_field[x:x+platform_width_idx, y:y+platform_width_idx] = hurdle_height * (i + 1) if stair_type == "ascend" else hurdle_height * (count - i)
            goals[i + goal_start[0]] = [x + platform_width_idx // 2, y + platform_width_idx // 2]

    # Set spawn area to flat ground
    spawn_length_idx = m_to_idx(2)
    height_field[:spawn_length_idx, :] = 0
    goals[0] = [spawn_length_idx - m_to_idx(0.5), mid_y]  

    current_x = spawn_length_idx

    # Add first hurdle obstacle
    add_hurdle(current_x, hurdle_height)
    goals[1] = [current_x + hurdle_width_idx // 2, mid_y]
    current_x += hurdle_width_idx + hurdle_gap_idx
    
    # Add stepping stones - ascending
    step_count = 3 + int(3 * difficulty)
    goal_start = [2, step_count]
    add_stepping_stones(current_x, mid_y, step_count, stair_type="ascend")
    current_x += step_count * (platform_width_idx + hurdle_gap_idx)
 
    # Add second hurdle obstacle
    add_hurdle(current_x, hurdle_height)
    goals[step_count + 1] = [current_x + hurdle_width_idx // 2, mid_y]
    current_x += hurdle_width_idx + hurdle_gap_idx

    # Add stepping stones - descending
    step_count = 3 + int(3 * difficulty)
    goal_start = [step_count + 2, step_count]
    add_stepping_stones(current_x, mid_y, step_count, stair_type="descend")
    current_x += step_count * (platform_width_idx + hurdle_gap_idx)

    # Add the final goal just past the last platform
    goals[-1] = [current_x + m_to_idx(0.5), mid_y]

    return height_field, goals