import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Multiple narrow corridors with variable heights to challenge balance and jumping capabilities."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    corridor_length_min = 0.5
    corridor_length_max = 1.5
    corridor_height_min, corridor_height_max = 0.1 * difficulty, 0.4 * difficulty
    corridor_width_min, corridor_width_max = 0.4 * (1 - difficulty), 0.6 * (1 - difficulty)
    gap_length = 0.2 + 0.6 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_corridor(start_x, mid_y, length, width, height):
        half_width = width // 2
        x1, x2 = start_x, start_x + length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    for i in range(7):  # Create 7 corridors
        length = np.random.uniform(corridor_length_min, corridor_length_max)
        length = m_to_idx(length)
        height = np.random.uniform(corridor_height_min, corridor_height_max)
        width = np.random.uniform(corridor_width_min, corridor_width_max)
        width = m_to_idx(width)

        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        add_corridor(cur_x, mid_y + dy, length + dx, width, height)

        # Place goal at the center of the corridor
        goals[i + 1] = [cur_x + length // 2, mid_y + dy]
        
        cur_x += length + dx + m_to_idx(gap_length)
    
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]  # Final goal
    height_field[cur_x:, :] = 0

    return height_field, goals