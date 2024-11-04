import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Step and incline course: It tests the quadruped's climbing and descending skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    step_height_min, step_height_max = 0.1 + 0.15 * difficulty, 0.15 + 0.2 * difficulty
    incline_angle_min, incline_angle_max = 5.0 + 5.0 * difficulty, 10.0 + 10.0 * difficulty
    incline_length = 1.0
    incline_length = m_to_idx(incline_length)

    mid_y = m_to_idx(width) // 2

    def add_step(start_x, end_x, mid_y, height):
        """Adds a step in the terrain."""
        half_width = m_to_idx(1.0)  # At least 1 meter wide
        y1, y2 = mid_y - half_width // 2, mid_y + half_width // 2
        height_field[start_x:end_x, y1:y2] = height

    def add_incline(start_x, mid_y, angle):
        """Adds an incline in the terrain."""
        half_width = m_to_idx(1.0)  # At least 1 meter wide
        y1, y2 = mid_y - half_width // 2, mid_y + half_width // 2
        for i in range(incline_length):
            height_field[start_x + i, y1:y2] = np.tan(np.deg2rad(angle)) * i * field_resolution

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    
    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(3):  # Create 3 sets of steps
        step_height = np.random.uniform(step_height_min, step_height_max)
        step_length = m_to_idx(1.0)
        add_step(cur_x, cur_x + step_length, mid_y, step_height)
        goals[i * 2 + 1] = [cur_x + step_length // 2, mid_y]

        cur_x += step_length
        add_step(cur_x, cur_x + step_length, mid_y, -step_height)
        goals[i * 2 + 2] = [cur_x + step_length // 2, mid_y]

        cur_x += step_length

    for i in range(3):  # Create 3 inclines
        incline_angle = np.random.uniform(incline_angle_min, incline_angle_max)
        add_incline(cur_x, mid_y, incline_angle)
        goals[6] = [cur_x + incline_length // 2, mid_y]

        cur_x += incline_length

        add_incline(cur_x, mid_y, -incline_angle)
        goals[7] = [cur_x + incline_length // 2, mid_y]

        cur_x += incline_length

    return height_field, goals