import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Staggered steps and narrow passages to test climbing dexterity and precision navigation."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform and obstacle parameters
    step_length = 1.0  # Constant step length for training consistency
    step_height_min, step_height_max = 0.1 * difficulty, 0.3 * difficulty
    platform_width = 0.4
    passage_width = 0.4  # Narrow passage to force precise navigation
    gap_length_min, gap_length_max = 0.1, 0.3 * difficulty

    step_length_idx = m_to_idx(step_length)
    platform_width_idx = m_to_idx(platform_width)
    passage_width_idx = m_to_idx(passage_width)
    gap_length_min_idx = m_to_idx(gap_length_min)
    gap_length_max_idx = m_to_idx(gap_length_max)

    mid_y = m_to_idx(width) // 2

    def add_step(start_x, end_x, height, mid_y):
        half_width = platform_width_idx // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_passage(start_x, end_x, height, mid_y):
        half_width = passage_width_idx // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    # Initial flat ground for spawn
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y] 

    # Create staggered steps and narrow passages
    cur_x = spawn_length
    for i in range(6):
        step_height = random.uniform(step_height_min, step_height_max)
        add_step(cur_x, cur_x + step_length_idx, step_height, mid_y)
        
        # Place goal in the middle of each step
        goals[i + 1] = [cur_x + step_length_idx // 2, mid_y]

        # Narrow passage
        cur_x += step_length_idx
        passage_length_idx = random.randint(gap_length_min_idx, gap_length_max_idx)
        add_passage(cur_x, cur_x + passage_length_idx, step_height, mid_y)

        cur_x += passage_length_idx

    # Final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals