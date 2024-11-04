import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Series of narrow walkways and jumps testing balance and agility of the quadruped."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up walkway dimensions based on difficulty
    walkway_width_min, walkway_width_max = 0.4, 0.7
    walkway_width_min, walkway_width_max = m_to_idx(walkway_width_min), m_to_idx(walkway_width_max)
    walkway_height_min, walkway_height_max = 0.1, 0.5
    gap_length = 0.2 + 0.8 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_walkway(start_x, end_x, mid_y, difficulty):
        width = random.randint(walkway_width_min, walkway_width_max)
        height = np.random.uniform(walkway_height_min, walkway_height_max)
        
        if difficulty > 0.5:
            # To make it harder, vary widths along the walkway
            for i in range(start_x, end_x, width):
                height_field[i:i+width, mid_y-width//2:mid_y+width//2] = height
        else:
            height_field[start_x:end_x, mid_y-width//2:mid_y+width//2] = height

    dx_min, dx_max = m_to_idx(0.2), m_to_idx(0.4)
    dy_min, dy_max = m_to_idx(-0.5), m_to_idx(0.5)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Place the first goal at the spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(6):
        dx = random.randint(dx_min, dx_max)
        dy = random.randint(dy_min, dy_max)
        walkway_length = m_to_idx(1.5 + 0.3 * difficulty)
        add_walkway(cur_x, cur_x + walkway_length + dx, mid_y + dy, difficulty)

        # Place goal in the center of the walkway
        goals[i + 1] = [cur_x + (walkway_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += walkway_length + dx + gap_length

    # Place final goal on flat ground behind the last walkway, fill the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals