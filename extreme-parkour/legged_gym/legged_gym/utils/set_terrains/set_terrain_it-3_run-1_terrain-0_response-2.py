import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Curved paths with varying elevations, narrow beams, and small jumps for precise navigation."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    max_height = 0.5 * difficulty  # Elevate the maximum height
    min_height = 0.1 * difficulty  # Increase minimum height slightly
    path_width_min = 0.4
    path_width_max = 0.6 + 0.2 * difficulty  # Narrower pathways for higher difficulty
    gap_length_min, gap_length_max = 0.1, 0.3 + 0.2 * difficulty  # Wider gaps
    path_turn_angle = [-0.3, 0.3]  # Curved paths

    mid_y = m_to_idx(width) // 2
    cur_x = m_to_idx(2)  # Starting point for the first path segment

    def add_path_segment(start_x, end_x, width, height, mid_y):
        half_width = width // 2
        y1, y2 = mid_y - half_width, mid_y + half_width
        x1, x2 = start_x, end_x
        height_field[x1:x2, y1:y2] = height

    # Initialize the flat ground for the spawn area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    dx_min, dx_max = 0.8, 1.2  # Increase path length for more navigation time
    dy_min, dy_max = -0.4, 0.4  # More varied y-axis movement
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)
    gap_length_min, gap_length_max = m_to_idx(gap_length_min), m_to_idx(gap_length_max)

    for i in range(7):
        height = np.random.uniform(min_height, max_height)
        path_width = np.random.randint(m_to_idx(path_width_min), m_to_idx(path_width_max))
        path_length = np.random.randint(dx_min, dx_max)
        path_gap = np.random.randint(gap_length_min, gap_length_max)
        dy = np.random.uniform(dy_min, dy_max)

        add_path_segment(cur_x, cur_x + path_length, path_width, height, mid_y + dy)

        # Place the goals at the center position of each path segment
        goals[i+1] = [cur_x + path_length // 2, mid_y + dy]

        cur_x += path_length + path_gap

    # Ensure there's a clear path for the final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals