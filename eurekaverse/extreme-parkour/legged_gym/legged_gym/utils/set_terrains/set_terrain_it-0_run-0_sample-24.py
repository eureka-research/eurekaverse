import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Series of inclined and declined ramps for the robot to ascend and descend."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    ramp_length = 1.5 - 0.5 * difficulty
    ramp_length = m_to_idx(ramp_length)
    ramp_width = 1.4  # Fixed width of 1.4 meters
    ramp_width = m_to_idx(ramp_width)
    ramp_height_min, ramp_height_max = 0.2, 0.4
    ramp_height = lambda h: np.random.uniform(0.5 * h, h) * difficulty

    mid_y = m_to_idx(width / 2)

    def add_ramp(start_x, end_x, mid_y, incline):
        half_width = ramp_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        try:
            if incline:
                for i in range(x2 - x1):
                    height_field[x1 + i, y1:y2] = (ramp_height_max / (x2 - x1)) * i
            else:
                for i in range(x2 - x1):
                    height_field[x1 + i, y1:y2] = ramp_height_max - (ramp_height_max / (x2 - x1)) * i
        except:
            pass

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    ramp_positions = [[False, True], [True, False], [False, True], [True, False], [False, True], [True, False], [False, True]]
    for i in range(7):  # Setup 7 ramps (alternating incline/decline)
        incline, decline = ramp_positions[i % len(ramp_positions)]
        add_ramp(cur_x, cur_x + ramp_length, mid_y, incline)
        
        # Place goals in the middle of ramps
        goals[i + 1] = [cur_x + (ramp_length / 2), mid_y]

        cur_x += ramp_length

    # Ensure last goal is placed within terrain bounds
    goals[-1] = [min(cur_x, m_to_idx(length - m_to_idx(1))), mid_y]
    
    return height_field, goals