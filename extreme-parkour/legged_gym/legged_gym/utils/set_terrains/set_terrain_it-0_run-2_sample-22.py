import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Stepping stones obstacle course testing the quadruped's precision and agility."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up step dimensions
    step_size = 0.3  # Each stone has a diameter of approximately 0.3 meters
    step_size_idx = m_to_idx(step_size)
    gap_min = 0.4  # Minimum gap between steps
    gap_max = 0.8  # Maximum gap between steps
    gap_min_idx = m_to_idx(gap_min)
    gap_max_idx = m_to_idx(gap_max)
    step_height_min, step_height_max = 0.1, 0.4  # Height range for steps
    step_height_min += 0.1 * difficulty
    step_height_max += 0.3 * difficulty

    mid_y = m_to_idx(width // 2)

    def add_step(x, y):
        """Adds a stepping stone at the specified (x, y) location."""
        radius = step_size_idx // 2
        step_height = np.random.uniform(step_height_min, step_height_max)
        height_field[x - radius:x + radius, y - radius:y + radius] = step_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # Place the first goal right at the spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    cur_y = mid_y

    for i in range(7):  # Set up 7 stepping stones
        add_step(cur_x, cur_y)

        # Update the goal to the center of the current step
        goals[i+1] = [cur_x, cur_y]

        # Move to the next position for the next step
        gap_x = np.random.randint(gap_min_idx, gap_max_idx)
        cur_x += gap_x

        # Slightly randomize the y position for the next step
        dy = np.random.uniform(-gap_max / 2, gap_max / 2)
        cur_y = np.clip(cur_y + m_to_idx(dy), step_size_idx, m_to_idx(width) - step_size_idx)
    
    # Ensure the last goal is reachable and set on flat ground
    goals[-1] = [cur_x + gap_min_idx, mid_y]
    height_field[cur_x + gap_min_idx:, :] = 0

    return height_field, goals