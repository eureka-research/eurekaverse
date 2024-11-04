import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Narrow passages between tall walls for the robot to navigate through."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set terrain properties
    wall_height = np.linspace(0.8, 1.5, num=8) * difficulty + 0.1
    passage_width_min = 0.4
    passage_width_max = 1.0 - 0.5 * difficulty  # Narrower passages at higher difficulty
    passage_widths = np.linspace(passage_width_max, passage_width_min, num=8)
    wall_thickness = m_to_idx(0.2)

    spawn_length = m_to_idx(2)
    mid_y = m_to_idx(width / 2)

    # Set initial flat area for robot spawn
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    current_x = spawn_length

    # Create narrow passageways
    for i in range(1, 8):
        passage_width = m_to_idx(passage_widths[i-1])
        half_passage_width = passage_width // 2
        left_wall_y_start = mid_y - half_passage_width - wall_thickness
        left_wall_y_end = mid_y - half_passage_width
        right_wall_y_start = mid_y + half_passage_width
        right_wall_y_end = mid_y + half_passage_width + wall_thickness

        wall_height_value = wall_height[i-1]

        # Set left wall
        height_field[current_x:current_x + m_to_idx(1), left_wall_y_start:left_wall_y_end] = wall_height_value

        # Set right wall
        height_field[current_x:current_x + m_to_idx(1), right_wall_y_start:right_wall_y_end] = wall_height_value

        # Set goal in the middle of the passage
        goals[i] = [current_x + m_to_idx(0.5), mid_y]

        current_x += m_to_idx(1.5)

    return height_field, goals