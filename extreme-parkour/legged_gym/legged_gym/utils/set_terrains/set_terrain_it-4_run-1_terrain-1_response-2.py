import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Combination of elevated beams, stairs, narrow paths, and hurdles to challenge the robot's agility, balance, and climbing skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up dimensions for different obstacles
    beam_width = np.random.uniform(0.4, 0.7)  # Narrower than previous, to test balance
    beam_width = m_to_idx(beam_width)
    beam_height = 0.2 + 0.3 * difficulty  # Elevated beams

    step_height = 0.3 * difficulty
    step_width = 1.0  # Consistent width for climbing
    step_length = m_to_idx(0.4)
    
    hurdle_height = 0.2 + 0.5 * difficulty
    hurdle_width = 0.4  # Narrow hurdles
    hurdle_length = m_to_idx(0.5)

    gap_length = 0.1 + 0.5 * difficulty  # Gaps between obstacles
    gap_length = m_to_idx(gap_length)
    
    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, mid_y):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = beam_height

    def add_steps(start_x, mid_y):
        half_width = m_to_idx(step_width) // 2
        y1, y2 = mid_y - half_width, mid_y + half_width
        step_heights = np.arange(0, step_height * 3, step_height)
        for i, height in enumerate(step_heights):
            x1, x2 = start_x + i * step_length, start_x + (i + 1) * step_length
            height_field[x1:x2, y1:y2] = height

    def add_hurdle(start_x, end_x, mid_y):
        half_width = m_to_idx(hurdle_width) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = hurdle_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Place first goal after spawn area
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    cur_goal_index = 1

    # Add elevated beam
    beam_length = m_to_idx(3.0)
    add_beam(cur_x, cur_x + beam_length, mid_y)
    goals[cur_goal_index] = [cur_x + beam_length / 2, mid_y]
    cur_x += beam_length + gap_length
    cur_goal_index += 1

    # Add steps
    add_steps(cur_x, mid_y)
    goals[cur_goal_index] = [cur_x + 1.5 * step_length, mid_y]
    cur_x += 3 * step_length + gap_length
    cur_goal_index += 1

    # Add several hurdles
    for i in range(2):
        hurdle_start_x = cur_x
        hurdle_end_x = cur_x + hurdle_length
        add_hurdle(hurdle_start_x, hurdle_end_x, mid_y)
        goals[cur_goal_index] = [cur_x + hurdle_length / 2, mid_y]
        cur_goal_index += 1
        cur_x += hurdle_length + gap_length

    # Add another set of elevated beams
    add_beam(cur_x, cur_x + beam_length, mid_y)
    goals[cur_goal_index] = [cur_x + beam_length / 2, mid_y]
    cur_x += beam_length + gap_length
    cur_goal_index += 1

    # Add the final steps
    add_steps(cur_x, mid_y)
    goals[cur_goal_index] = [cur_x + 1.5 * step_length, mid_y]

    # Place the final goal at the end
    final_goal_x = min(m_to_idx(length) - 1, cur_x + 3 * step_length + gap_length)
    goals[-1] = [final_goal_x, mid_y]
    height_field[final_goal_x:, :] = 0

    return height_field, goals