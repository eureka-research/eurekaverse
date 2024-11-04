import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Mixed obstacles: narrow passages, ramps, and pit jumps to test a balance of navigation and climbing skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform length and width configurations
    narrow_width = m_to_idx(0.3)
    wide_width = m_to_idx(1.0)
    platform_height_min, platform_height_max = 0.1, 0.4 * difficulty
    gap_length = 0.5 * difficulty
    
    mid_y = m_to_idx(width) // 2

    def add_narrow_passage(start_x, end_x):
        """Add a narrow hallway the robot must navigate through."""
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - narrow_width // 2, mid_y + narrow_width // 2
        height_field[x1:x2, y1:y2] = platform_height_max

    def add_ramp(start_x, end_x, incline=True):
        """Add a ramp with incline or decline."""
        half_width = wide_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.linspace(0, platform_height_max if incline else -platform_height_max, x2 - x1)
        height_field[x1:x2, y1:y2] = ramp_height[:, None]

    def add_pit(start_x, gap_length):
        """Add a pit the robot must jump over."""
        end_x = start_x + m_to_idx(gap_length)
        height_field[start_x:end_x, :] = -1.0
        return end_x

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length

    # Section 1: Narrow passage
    add_narrow_passage(cur_x, cur_x + m_to_idx(1.5))
    goals[1] = [cur_x + m_to_idx(0.75), mid_y]
    cur_x += m_to_idx(1.5)
    
    # Section 2: Incline ramp
    add_ramp(cur_x, cur_x + m_to_idx(1.2), incline=True)
    goals[2] = [cur_x + m_to_idx(0.6), mid_y]
    cur_x += m_to_idx(1.2)

    # Section 3: Stepping stones
    step_length = 0.4 * difficulty
    for i in range(3):
        end_x = add_pit(cur_x, gap_length)
        add_narrow_passage(end_x, end_x + m_to_idx(step_length))
        goals[i + 3] = [end_x + m_to_idx(step_length) // 2, mid_y]
        cur_x = end_x + m_to_idx(step_length)

    # Section 4: Pit Jump
    cur_x = add_pit(cur_x, m_to_idx(0.8))

    # Section 5: Decline ramp
    add_ramp(cur_x, cur_x + m_to_idx(2.0), incline=False)
    goals[7] = [cur_x + m_to_idx(1.0), mid_y]
    cur_x += m_to_idx(2.0)

    # Final goal
    goals[7] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals