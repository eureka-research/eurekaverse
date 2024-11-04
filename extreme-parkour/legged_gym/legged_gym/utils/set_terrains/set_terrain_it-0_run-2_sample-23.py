import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Series of staggered stairs for the quadruped to climb up and down."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Convert terrain dimensions to grid indices
    terrain_length = m_to_idx(length)
    terrain_width = m_to_idx(width)

    # Quadruped's center starting point
    start_x = m_to_idx(2)
    start_y = terrain_width // 2
    
    # Initial goal at start position
    goals[0] = [start_x - m_to_idx(0.5), start_y]

    # Define stair dimensions based on difficulty
    stair_width = 1.0 - 0.3 * difficulty  # decrease with difficulty
    stair_width = m_to_idx(stair_width)

    stair_height_min = 0.1 * difficulty  # increase with difficulty
    stair_height_max = 0.3 * difficulty  # increase with difficulty
    stair_length = 1.2  # fixed length of 1.2 meters
    stair_length = m_to_idx(stair_length)
    
    cur_x = start_x

    def add_stair(x, y, width, length, height):
        """Add a stair with given dimensions to the height_field."""
        half_width = width // 2
        x1, x2 = x, x + length
        y1, y2 = y - half_width, y + half_width
        height_field[x1:x2, y1:y2] += height

    for i in range(7):  # 7 sets of stairs
        stair_height = np.random.uniform(stair_height_min, stair_height_max)
        add_stair(cur_x, start_y, stair_width, stair_length, stair_height)

        # Place the goal in the center of the stair
        goals[i + 1] = [cur_x + stair_length // 2, start_y]

        # Move to the next stair position
        cur_x += stair_length

        # Adding a small gap with random width between stairs for added difficulty
        gap = np.random.uniform(0.1, 0.4) * difficulty
        gap = m_to_idx(gap)
        cur_x += gap

    # Final goal at the end of the terrain
    goals[-1] = [cur_x + m_to_idx(0.5), start_y]

    return height_field, goals