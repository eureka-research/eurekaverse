import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Urban parkour with staggered steps, narrow passageways, and pitfalls to navigate."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    mid_y = m_to_idx(width / 2)
    
    # Define obstacle dimensions and heights based on difficulty
    step_height = 0.1 + difficulty * 0.4
    step_width = m_to_idx(1.0)  # Each step is 1 m wide
    narrow_width = m_to_idx(0.4)  # Width of the narrow passageways
    gap_height = -0.5 - difficulty * 0.5  # Deeper pits with higher difficulty
    
    # Set up staggered steps
    def add_step(start_x, mid_y, height):
        half_width = step_width // 2
        x1, x2 = start_x, start_x + step_width
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at spawn area
    
    cur_x = spawn_length
    for i in range(3):  # Create 3 staggered steps
        add_step(cur_x, mid_y, step_height * (i + 1))
        goals[i + 1] = [cur_x + step_width / 2, mid_y]
        cur_x += step_width + m_to_idx(0.4)  # Move to next step position with a gap of 0.4 meters

    # Narrow passageways
    def add_passage(start_x, mid_y):
        half_width = narrow_width // 2
        x1, x2 = start_x, start_x + narrow_width
        y1, y2 = mid_y - narrow_width, mid_y + narrow_width
        height_field[x1:x2, y1:y2] = 0
        height_field[x1:x2, :y1] = -1.0  # Lower ground outside passageway
        height_field[x1:x2, y2:] = -1.0

    # Add first narrow passage against a pit
    pit_start_x = cur_x
    height_field[pit_start_x:pit_start_x + m_to_idx(2), :] = gap_height
    cur_x += m_to_idx(2)  # Move over the pit
    add_passage(cur_x, mid_y)
    goals[4] = [cur_x + narrow_width / 2, mid_y]

    # Second staggered steps
    cur_x += narrow_width + m_to_idx(0.4)
    for i in range(3):  # Create 3 more staggered steps
        add_step(cur_x, mid_y, step_height * (i + 1))
        goals[i + 5] = [cur_x + step_width / 2, mid_y]
        cur_x += step_width + m_to_idx(0.4)  # Move to next step position with a gap of 0.4 meters

    # Second narrow passage
    pit2_start_x = cur_x
    height_field[pit2_start_x:pit2_start_x + m_to_idx(2), :] = gap_height
    cur_x += m_to_idx(2)  # Move over the pit
    add_passage(cur_x, mid_y)
    goals[-1] = [cur_x + narrow_width / 2, mid_y]

    return height_field, goals