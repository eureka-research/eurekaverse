import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Combination of stairs, narrow beams, and sloped surfaces traversing a pit for the robot to climb on and jump across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Distance between key features
    gap_length = 0.4 + 0.4 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    # Function to add stairs
    def add_stairs(start_x, end_x, mid_y, steps, step_height):
        half_width = m_to_idx(0.6)  # making stairs wider
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        stair_spacing = (x2 - x1) // steps
        for i in range(steps):
            height_field[x1 + i * stair_spacing : x1 + (i + 1) * stair_spacing, y1:y2] = i * step_height

    # Function to add beams
    def add_beam(start_x, end_x, mid_y):
        half_width = m_to_idx(0.4)  # narrow beams
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        beam_height = np.random.uniform(0.15, 0.3)
        height_field[x1:x2, y1:y2] = beam_height

    # Function to add slopes
    def add_slope(start_x, end_x, mid_y, direction):
        half_width = m_to_idx(0.5)
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slope_height = np.random.uniform(0.1 + 0.1 * difficulty, 0.25 + 0.25 * difficulty)
        slant = np.linspace(0, slope_height, num=x2-x1)
        if direction == 'up':
            height_field[x1:x2, y1:y2] = slant[:, None]
        else:
            height_field[x1:x2, y1:y2] = slant[::-1][:, None]

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at the end of the spawn area

    # Set remaining area to be a pit
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    features = ['stair', 'beam', 'slope'] * 2  # Repeat feature types
    random.shuffle(features)

    for i in range(6):  # Set up 6 features
        dx = random.randint(-m_to_idx(0.1), m_to_idx(0.1))
        if features[i] == 'stair':
            add_stairs(cur_x, cur_x + m_to_idx(1.2) + dx, mid_y, 5, 0.1 + 0.1 * difficulty)
        elif features[i] == 'beam':
            add_beam(cur_x, cur_x + m_to_idx(1.0) + dx, mid_y)
        elif features[i] == 'slope':
            direction = 'up' if i % 2 == 0 else 'down'
            add_slope(cur_x, cur_x + m_to_idx(1.0) + dx, mid_y, direction)

        # Put goal in the center of each feature
        goals[i+1] = [cur_x + (m_to_idx(1.0) + dx) / 2, mid_y]

        # Add gap
        cur_x += m_to_idx(1.0) + dx + gap_length

    # Add final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals