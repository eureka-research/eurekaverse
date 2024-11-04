import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Narrow passageways and raised walkways to test precision and careful navigation."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]
    
    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Configure parameters based on difficulty
    path_width = 0.4 + (0.6 * (1 - difficulty))  # Path width between 0.4m and 1m
    passage_height = 0.05 + (0.3 * difficulty)  # Passage height between 0.05m and 0.35m
    walkway_height = 0.1 + (0.3 * difficulty)  # Walkway height between 0.1m and 0.4m
    section_length = 1.0 + (1.0 * difficulty)  # Varying section lengths, longer with higher difficulty

    path_width = m_to_idx(path_width)
    passage_height = np.random.uniform(passage_height, passage_height + 0.1 * difficulty)
    walkway_height = np.random.uniform(walkway_height, walkway_height + 0.1 * difficulty)
    section_length = m_to_idx(section_length)

    # Initial flat ground area for spawn point
    spawn_area = m_to_idx(2)
    height_field[:spawn_area, :] = 0
    mid_y = m_to_idx(width) // 2
    goals[0] = [spawn_area - m_to_idx(0.5), mid_y]

    cur_x = spawn_area

    def add_narrow_passage(start_x, length, height, center_y):
        half_width = path_width // 2
        x_start, x_end = start_x, start_x + length
        y_start, y_end = center_y - half_width, center_y + half_width
        height_field[x_start:x_end, y_start:y_end] = height

    # Create a sequence of narrow passages and raised walkways
    for i in range(7):
        if i % 2 == 0:
            # Add narrow passage
            add_narrow_passage(cur_x, section_length, passage_height, mid_y)
            goals[i+1] = [cur_x + section_length / 2, mid_y]
        else:
            # Add raised walkway
            height_field[cur_x:cur_x + section_length, :] = walkway_height
            goals[i+1] = [cur_x + section_length / 2, mid_y]

        cur_x += section_length

    # Final goal at the end of the course
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    return height_field, goals