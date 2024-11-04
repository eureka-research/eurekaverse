import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Stepping stones over varied terrain requiring precise stepping and jumping."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up stepping stone dimensions
    base_step_size = 0.4  # meters
    step_size_variation = 0.4 * difficulty
    step_size = base_step_size + np.random.uniform(-step_size_variation, step_size_variation)
    step_size = m_to_idx(step_size)
    step_height_variation = 0.1 * difficulty
    gap_min = 0.2
    gap_max = 0.4 + 0.3 * difficulty
    gap_min = m_to_idx(gap_min)
    gap_max = m_to_idx(gap_max)

    def add_stepping_stone(start_x, start_y, end_x, height):
        """Adds a stepping stone at specified location."""
        height_field[start_x:end_x, start_y] = height
    
    mid_y = m_to_idx(width) // 2
    height_min, height_max = 0.1, 0.4

    current_x = m_to_idx(2)  # Starting x position after spawn area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0  # Flat spawn area
    
    # Place first goal at the spawn area
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    for i in range(6):
        height = random.uniform(height_min, height_max + step_height_variation)
        y_position = mid_y + random.randint(-step_size // 2, step_size // 2)
        add_stepping_stone(current_x, y_position, current_x + step_size, height)
        
        # Set goal in the middle of the step
        goals[i + 1] = [current_x + step_size / 2, y_position]

        # Move to next step position
        current_x += step_size + random.randint(gap_min, gap_max)

    # Ensure there is enough space for the last goal and straight line travel
    remaining_space = m_to_idx(length) - current_x
    if remaining_space < m_to_idx(1):
        current_x -= m_to_idx(1)

    # Place final goal beyond last stepping stone
    goals[-1] = [current_x + m_to_idx(0.5), mid_y]
    height_field[current_x:, :] = 0  # Flat goal area

    return height_field, goals