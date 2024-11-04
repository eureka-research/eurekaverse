import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Slalom course with narrow poles for the quadruped to navigate around."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up pole dimensions
    pole_radius = 0.1  # 10cm radius poles
    pole_radius_idx = m_to_idx(pole_radius)
    pole_gap_min = 0.6  # Minimum gap between poles
    pole_gap_max = 1.2 - 0.6 * difficulty  # Max gap shrinks with difficulty
    pole_gap_min_idx, pole_gap_max_idx = m_to_idx(pole_gap_min), m_to_idx(pole_gap_max)

    mid_y = m_to_idx(width) // 2

    def add_pole(center_x, center_y):
        radius_idx = pole_radius_idx
        x1, x2 = center_x - radius_idx, center_x + radius_idx
        y1, y2 = center_y - radius_idx, center_y + radius_idx
        height_field[x1:x2, y1:y2] = 1.0  # Poles are 1 meter tall

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length + pole_gap_max_idx // 2  # Start poles just after spawn
    direction = 1  # Direction to alternate between left and right

    for i in range(7):  # Set up 7 poles
        gap = np.random.randint(pole_gap_min_idx, pole_gap_max_idx)
        cur_y = mid_y + direction * m_to_idx(0.5) * (1 - difficulty)  # Vary offset based on difficulty
        add_pole(cur_x, cur_y)
        # Put goal just ahead of the current pole
        goals[i + 1] = [cur_x + gap // 2, cur_y]

        cur_x += gap
        direction *= -1  # Change direction for the next pole

    # Add final goal at the end of the course
    goals[-1] = [cur_x + pole_gap_max_idx // 2, mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals