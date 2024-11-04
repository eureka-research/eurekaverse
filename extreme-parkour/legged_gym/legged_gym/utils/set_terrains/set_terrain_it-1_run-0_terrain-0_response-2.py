import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Series of hurdles and narrow passages to test the robot's agility and ability to make tight turns."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]
    
    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define hurdle dimensions
    hurdle_height_min = 0.2 * difficulty
    hurdle_height_max = 0.4 * difficulty
    hurdle_width = 1.0
    hurdle_depth = 0.2
    hurdle_gap_min = 0.5
    hurdle_gap_max = 1.0
    hurdle_width_idx = m_to_idx(hurdle_width)
    hurdle_depth_idx = m_to_idx(hurdle_depth)
    hurdle_gap_min_idx = m_to_idx(hurdle_gap_min)
    hurdle_gap_max_idx = m_to_idx(hurdle_gap_max)
    
    # Define passage dimensions
    passage_width = 0.5 + 0.2 * (1 - difficulty)  # Narrower for higher difficulty
    passage_length = 2.0
    passage_height = 0.05
    passage_width_idx = m_to_idx(passage_width)
    passage_length_idx = m_to_idx(passage_length)
    passage_height_idx = m_to_idx(passage_height)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    
    # First goal at the spawn area
    mid_y = m_to_idx(width) // 2
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(4):  # Create 4 sets of hurdles and passages
        # Adding a hurdle
        hurdle_height = np.random.uniform(hurdle_height_min, hurdle_height_max)
        height_field[cur_x:cur_x + hurdle_depth_idx, mid_y - hurdle_width_idx // 2: mid_y + hurdle_width_idx // 2] = hurdle_height
        
        # Setting goal after the hurdle
        cur_x += hurdle_depth_idx + hurdle_gap_min_idx
        goals[i + 1] = [cur_x - hurdle_gap_min_idx // 2, mid_y]

        # Adding a narrow passage
        passage_start_x = cur_x
        passage_end_x = cur_x + passage_length_idx
        dy_passage = np.random.randint(-passage_width_idx // 2, passage_width_idx // 2)
        height_field[passage_start_x:passage_end_x, mid_y + dy_passage - passage_width_idx // 2:mid_y + dy_passage + passage_width_idx // 2] = -passage_height

        # Setting goal after passing through
        cur_x = passage_end_x + hurdle_gap_max_idx
        goals[i + 2] = [cur_x - hurdle_gap_max_idx // 2, mid_y + dy_passage]

    # Final goal
    final_goal_x = cur_x + m_to_idx(0.5)
    goals[-1] = [final_goal_x, mid_y]

    return height_field, goals