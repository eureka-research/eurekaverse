import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Obstacle course with slalom ladders and varying height barriers for the robot to navigate through."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    slalom_gap = 0.8 - 0.3 * difficulty  # Slalom gap decreases with difficulty
    slalom_gap = m_to_idx(slalom_gap)
    barrier_height = 0.05 + 0.25 * difficulty  # Barrier height increases with difficulty
    barrier_width = 1.0 + 0.5 * difficulty  # Barrier width increases slightly with difficulty
    barrier_width = m_to_idx(barrier_width)
    slalom_y_positions = [m_to_idx(1.0) + m_to_idx(2.0) * i for i in range(4)]  # Positioning slalom barriers

    def add_slalom_barrier(start_x, width, height, y_positions):
        for y in y_positions:
            height_field[start_x:start_x+width, y:y + m_to_idx(0.4)] = height

    dx_min, dx_max = 2.0, 3.0
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)

    # Initial flat ground for spawning
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    mid_y = m_to_idx(width) // 2
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(4):  # Set up 4 slalom sections
        add_slalom_barrier(cur_x, barrier_width, barrier_height, slalom_y_positions)

        # Place goals to navigate the slaloms
        goals[i+1] = [cur_x + m_to_idx(0.5), mid_y - m_to_idx(1.5) * ((i+1) % 2)]
        
        # Add a clear pathway between the slalom sections
        cur_x += barrier_width + slalom_gap

    # Add final goal at the end of the course
    goals[-1] = [cur_x + m_to_idx(1.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals