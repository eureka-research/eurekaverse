import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """A series of ramps and steps to test the quadruped's climbing and stability skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    ramp_length = 2.0 - 1.5 * difficulty   # Ramp length dependent on difficulty
    ramp_length = m_to_idx(ramp_length)
    step_height_min, step_height_max = 0.1, 0.3 * difficulty   # Step height range depending on the difficulty
    step_length = 0.5  # Step length (each step is 0.5 meters in depth)
    step_length = m_to_idx(step_length)
    
    mid_y = m_to_idx(width) // 2

    def add_ramp(start_x, end_x, mid_y, start_height, end_height):
        half_width = 7  # approximately 350mm for 7 cells which suits most quad size
        x1, x2 = start_x, end_x
        height_increment = (end_height - start_height) / (x2 - x1)
        for i in range(x2 - x1):
            y1, y2 = mid_y - half_width, mid_y + half_width
            height_field[x1 + i, y1:y2] = start_height + i * height_increment

    def add_step(start_x, mid_y, height):
        half_width = 7  # approximately 350mm for 7 cells which suits most quad size
        x1, x2 = start_x, start_x + step_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = step_length, step_length * 3
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    altitude = 0
    for i in range(6):  # Create 3 ramps and 3 steps alternating
        if i % 2 == 0:
            # Add ramp (up or down based on even or odd indices)
            ramp_start_height = altitude
            ramp_end_height = altitude + np.random.uniform(step_height_min, step_height_max)
            add_ramp(cur_x, cur_x + ramp_length, mid_y, ramp_start_height, ramp_end_height)
            altitude = ramp_end_height
            goal_x = cur_x + ramp_length // 2
            cur_x += ramp_length
        else:
            # Add step (flat top surface)
            step_height = np.random.uniform(step_height_min, step_height_max)
            add_step(cur_x, mid_y, altitude + step_height)
            goal_x = cur_x + step_length // 2
            cur_x += step_length
        
        # Place goal in line
        goals[i+1] = [goal_x, mid_y]

        # Increase length between obstacles slightly based on difficulty
        dx = np.random.randint(dx_min, dx_max)
        cur_x += dx
    
    # Add final goal after last obstacle
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals