import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Series of ascending and descending steps and slopes for the robot to climb and navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    step_height_min, step_height_max = 0.05 * difficulty, 0.25 * difficulty
    slope_length_min, slope_length_max = 1.0 - 0.4 * difficulty, 1.0 - 0.1 * difficulty
    step_length = m_to_idx(0.5)
    mid_y = m_to_idx(width) // 2
    
    def add_step(start_x, end_x, height):
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - m_to_idx(0.75), mid_y + m_to_idx(0.75)
        height_field[x1:x2, y1:y2] = height

    def add_slope(start_x, end_x, start_height, end_height):
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - m_to_idx(0.75), mid_y + m_to_idx(0.75)
        slope = np.linspace(start_height, end_height, x2 - x1)
        for i in range(x2 - x1):
            height_field[x1 + i, y1:y2] = slope[i]

    cur_x = m_to_idx(2)  # start adding obstacles after the quadruped spawn area
    height_field[0:cur_x, :] = 0

    goals[0] = [cur_x - m_to_idx(0.5), mid_y]  # set first goal at end of spawn area
    
    for i in range(1, 8, 2):  # 4 step segments and 4 slope segments
        # Add step up
        step_height = random.uniform(step_height_min, step_height_max)
        add_step(cur_x, cur_x + step_length, step_height)
        goals[i] = [cur_x + step_length / 2, mid_y]
        cur_x += step_length
        
        # Add slope down
        slope_length = random.uniform(slope_length_min, slope_length_max)
        add_slope(cur_x, cur_x + m_to_idx(slope_length), step_height, 0)
        goals[i + 1] = [cur_x + m_to_idx(slope_length) / 2, mid_y]
        cur_x += m_to_idx(slope_length)

    # Final flat goal area
    height_field[cur_x:, :] = 0
    goals[7] = [cur_x + m_to_idx(0.5), mid_y]  # final goal after the last slope

    return height_field, goals