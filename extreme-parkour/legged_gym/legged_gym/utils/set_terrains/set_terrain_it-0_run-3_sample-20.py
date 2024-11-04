import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """
    Multiple narrow ledges and wide steps for the robot to navigate by 
    balancing and stepping deftly from one ledge to the next.
    """

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define obstacle dimensions
    ledge_length = 1.0 - 0.3 * difficulty
    ledge_length = m_to_idx(ledge_length)
    ledge_width = 0.4 + 0.3 * difficulty
    ledge_width = m_to_idx(ledge_width)
    ledge_height_min, ledge_height_max = 0.1 + 0.2 * difficulty, 0.15 + 0.3 * difficulty
    step_length = 0.6
    step_length = m_to_idx(step_length)
    step_width = 1.0 + 0.5 * difficulty
    step_width = m_to_idx(step_width)
    step_height_min, step_height_max = 0.05 + 0.15 * difficulty, 0.1 + 0.2 * difficulty

    max_dx = 0.2 * difficulty
    max_dx = m_to_idx(max_dx)

    mid_y = m_to_idx(width) // 2

    def add_ledge(start_x, end_x, mid_y):
        half_width = ledge_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ledge_height = np.random.uniform(ledge_height_min, ledge_height_max)
        height_field[x1:x2, y1:y2] = ledge_height

    def add_step(start_x, end_x, mid_y):
        half_width = step_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        step_height = np.random.uniform(step_height_min, step_height_max)
        height_field[x1:x2, y1:y2] = step_height

    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y] 

    cur_x = spawn_length
    step_positions = [(3, 0.4), (4, 1.2), (5, 0.6)]
    for i, (step_spacing, _) in enumerate(step_positions):
        spacing = m_to_idx(step_spacing)

        for j in range(spacing):
            dx = np.random.randint(-max_dx, max_dx)
            if j % 2 == 0:
                add_step(cur_x + j * (dx + step_length), cur_x + (j + 1) * (dx + step_length), mid_y + dx)
            else:
                add_ledge(cur_x + j * (dx + ledge_length), cur_x + (j + 1) * (dx + ledge_length), mid_y + dx)

            goals[i*3+j+1] = [cur_x + (j + 0.5) * (dx + step_length), mid_y + dx]

        cur_x += spacing * step_length
    
    goals[7] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals