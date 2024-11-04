import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Series of staircases and narrow corridors for the robot to navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up staircase and corridor dimensions
    stair_height_min, stair_height_max = 0.05 * difficulty, 0.15 * difficulty
    stair_width_min, stair_width_max = 0.4, 1.0
    corridor_width_min, corridor_width_max = 0.4, 1.5
    corridor_length = 1.0 + 1.0 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_staircase(start_x, end_x, start_height, stair_height):
        for x in range(start_x, end_x):
            height = start_height + (x - start_x) * stair_height
            height_field[x, :] = height

    def add_corridor(start_x, end_x, mid_y, corridor_width):
        half_width = corridor_width // 2
        y1, y2 = max(0, mid_y - half_width), min(m_to_idx(width), mid_y + half_width)
        for x in range(start_x, end_x):
            height_field[x, y1:y2] = 0.0

    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [1, mid_y]

    cur_x = spawn_length
    for i in range(4):  # Create 4 staircases and 4 corridors
        stair_height = np.random.uniform(stair_height_min, stair_height_max)
        stair_width = np.random.uniform(stair_width_min, stair_width_max)
        stair_width = m_to_idx(stair_width)

        add_staircase(cur_x, cur_x + stair_width, height_field[cur_x - 1, 0] if cur_x > 0 else 0, stair_height)
        goals[i * 2 + 1] = [cur_x + stair_width // 2, mid_y]

        cur_x += stair_width
        
        corridor_width = np.random.uniform(corridor_width_min, corridor_width_max)
        corridor_width = m_to_idx(corridor_width)
        corridor_end_x = cur_x + m_to_idx(corridor_length)
        
        add_corridor(cur_x, corridor_end_x, mid_y, corridor_width)
        goals[i * 2 + 2] = [cur_x + m_to_idx(corridor_length) // 2, mid_y]
        
        cur_x = corridor_end_x  # Update current position

    goals[7] = [cur_x + m_to_idx(1.5), mid_y]
    height_field[cur_x:, :] = 0  # Flatten the terrain at the end

    return height_field, goals