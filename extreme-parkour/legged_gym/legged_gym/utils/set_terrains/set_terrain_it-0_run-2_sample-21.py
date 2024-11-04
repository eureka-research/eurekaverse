import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Series of hurdles in succession for the quadruped to jump over or traverse underneath based on the gap heights."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]
    
    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set hurdle dimensions
    hurdle_height_min = 0.1 + 0.4 * difficulty
    hurdle_height_max = 0.3 + 0.7 * difficulty
    hurdle_width = m_to_idx(1.0)  # 1 meter wide
    gap_length = m_to_idx(1.5 - 1.0 * difficulty)  # Gaps get smaller with increased difficulty

    def add_hurdle(start_x, mid_y):
        half_width = hurdle_width // 2
        y1, y2 = mid_y - half_width, mid_y + half_width
        hurdle_height = np.random.uniform(hurdle_height_min, hurdle_height_max)
        height_field[start_x:start_x + m_to_idx(0.2), y1:y2] = hurdle_height  # Narrow hurdle

    # Place the quadruped's spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    mid_y = m_to_idx(width) // 2
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # Set first goal near the spawn for easier guidance

    cur_x = spawn_length
    dx_min, dx_max = 0, 0  # For simplicity, hurdles are directly ahead

    # Adversity pairs of hurdles
    for i in range(4):  # Since we have 8 goals, 4 hurdles ensure a goal before and after each hurdle
        dx = np.random.randint(dx_min, dx_max)
        add_hurdle(cur_x, mid_y)

        # Place goal before and after each hurdle
        goals[i*2 + 1] = [cur_x + dx + hurdle_width // 2 + m_to_idx(0.1), mid_y]
        goals[i*2 + 2] = [cur_x + dx + gap_length + hurdle_width // 2 + m_to_idx(0.1), mid_y]

        # Add gap
        cur_x += dx + gap_length + hurdle_width
    
    # Place the final goal beyond the last hurdle, fill any remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals