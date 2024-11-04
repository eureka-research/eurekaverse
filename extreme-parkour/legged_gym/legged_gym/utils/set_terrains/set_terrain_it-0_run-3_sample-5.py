import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Series of steps and ramps to challenge the quadruped's climbing and descending skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    step_height = 0.1 + 0.3 * difficulty
    step_height = m_to_idx(step_height)
    ramp_length = 1.0 + 1.0 * difficulty
    ramp_length = m_to_idx(ramp_length)
    mid_y = m_to_idx(width) // 2
    cur_x = m_to_idx(2)

    def add_step(start_x, width, height):
        half_width = width // 2
        end_x = start_x + width
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[start_x:end_x, y1:y2] = height

    def add_ramp(start_x, width, height, upward=True):
        half_width = width // 2
        end_x = start_x + width
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.linspace(0, height, end_x - start_x) if upward else np.linspace(height, 0, end_x - start_x)
        for x in range(start_x, end_x):
            height_field[x, y1:y2] = ramp_height[x - start_x]

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Add steps and ramps alternatively
    for i in range(3):
        add_step(cur_x, m_to_idx(0.4), step_height * (i+1))
        goals[i+1] = [cur_x + m_to_idx(0.2), mid_y]
        cur_x += m_to_idx(0.4)

        add_ramp(cur_x, ramp_length, step_height * (i+2), upward=True)
        goals[i+4] = [cur_x + ramp_length // 2, mid_y]
        cur_x += ramp_length

    # Ensure the final goal and some flat ground after last obstacle
    final_height = step_height * 4
    add_step(cur_x, m_to_idx(0.4), final_height)
    goals[6] = [cur_x + m_to_idx(0.2), mid_y]
    cur_x += m_to_idx(0.4)
    height_field[cur_x:, :] = final_height
    goals[7] = [cur_x + m_to_idx(0.5), mid_y]

    return height_field, goals