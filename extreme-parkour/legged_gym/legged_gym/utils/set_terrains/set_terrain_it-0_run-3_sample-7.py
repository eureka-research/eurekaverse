import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Series of hurdles and pits, forcing the quadruped to jump and avoid falling."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Configuration of hurdles and pits
    hurdle_height_min, hurdle_height_max = 0.1 + 0.2 * difficulty, 0.2 + 0.3 * difficulty
    pit_depth = -0.1 - 0.3 * difficulty
    hurdle_width = 0.5 + 0.5 * difficulty
    hurdle_width = m_to_idx(hurdle_width)
    passage_width = 1.0 + 0.5 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_hurdle(start_x, width):
        height = np.random.uniform(hurdle_height_min, hurdle_height_max)
        x1, x2 = start_x, start_x + width
        y1, y2 = mid_y - hurdle_width // 2, mid_y + hurdle_width // 2
        height_field[x1:x2, y1:y2] = height

    def add_pit(start_x, length):
        x1, x2 = start_x, start_x + length
        height_field[x1:x2, :] = pit_depth

    # Initializing spawn area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(6):  # Create 6 hurdle & pit sequences
        hurdle_width_rand = np.random.uniform(hurdle_width * 0.8, hurdle_width * 1.2)
        hurdle_width_rand = m_to_idx(hurdle_width_rand)
        
        # Add the hurdle
        add_hurdle(cur_x, hurdle_width_rand)
        goals[i+1] = [cur_x + hurdle_width_rand // 2, mid_y]

        # Move to the end of the hurdle and add the pit
        cur_x += hurdle_width_rand
        pit_length = np.random.uniform(passage_width * 0.8, passage_width * 1.2)
        pit_length = m_to_idx(pit_length)
        add_pit(cur_x, pit_length)
        cur_x += pit_length

    # Add final goal just past the last hurdle
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals