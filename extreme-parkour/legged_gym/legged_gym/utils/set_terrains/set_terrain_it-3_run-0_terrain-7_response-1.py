import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Series of stepping stones with varying heights and gaps, placed over a pit, testing the robot's precision and jumping abilities."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    # Initialize height_field and goals arrays
    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Configuration of stepping stones
    step_length = 0.6 - 0.3 * difficulty  # Length of each step
    step_length = m_to_idx(step_length)
    step_width = np.random.uniform(0.4, 0.6)  # Width of each step
    step_width = m_to_idx(step_width)
    step_height_min, step_height_max = 0.1 + 0.2 * difficulty, 0.2 + 0.5 * difficulty
    gap_length = 0.2 + 0.7 * difficulty  # Length of gaps between steps
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2  # Middle of the field in y-axis

    def add_step(start_x, end_x, center_y):
        half_width = step_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = center_y - half_width, center_y + half_width
        step_height = np.random.uniform(step_height_min, step_height_max)
        height_field[x1:x2, y1:y2] = step_height  # Set height for the step
    
    # Create a flat spawn area and set the first goal
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Set remaining area to be a pit
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length  # Initial x-coordinate after spawn area
    for i in range(6):  # Create 6 stepping stones
        dx = np.random.randint(-m_to_idx(0.05), m_to_idx(0.05))  # Small random offset in x
        dy = np.random.randint(-m_to_idx(0.3), m_to_idx(0.3))  # Random offset in y
        add_step(cur_x, cur_x + step_length + dx, mid_y + dy)

        # Set goal in the center of the step
        goals[i+1] = [cur_x + (step_length + dx) / 2, mid_y + dy]
        
        cur_x += step_length + dx + gap_length  # Move to the next step position

    # Set final goal at the end of the course and make the rest of the terrain flat
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:] = 0

    return height_field, goals