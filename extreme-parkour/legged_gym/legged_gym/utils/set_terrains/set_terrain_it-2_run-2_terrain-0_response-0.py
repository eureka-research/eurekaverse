import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Narrow walkways and alternating staircases for testing balance and agility."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Adjust layout dimensions based on difficulty
    walkway_length = 1.5
    walkway_length = m_to_idx(walkway_length)
    walkway_width = 0.3 + 0.2 * difficulty  # Start narrow, get a bit wider with difficulty
    walkway_width = m_to_idx(walkway_width)

    step_height = 0.1 + 0.2 * difficulty  # Adjust step height based on difficulty
    step_height = m_to_idx(step_height)
    step_width_min = 0.2
    step_width_max = 0.4
    step_width_min = m_to_idx(step_width_min)
    step_width_max = m_to_idx(step_width_max)

    mid_y = m_to_idx(width) // 2

    def add_walkway(start_x, length, mid_y):
        half_width = walkway_width // 2
        end_x = start_x + length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[start_x:end_x, y1:y2] = 0.1  # Set a small height for the walkway

        return end_x

    def add_staircase(start_x, mid_y, steps):
        half_width = step_width_min // 2
        x1 = start_x
        for i in range(steps):
            step_width = np.random.uniform(step_width_min, step_width_max)
            step_width = int(step_width)
            x2 = x1 + step_width
            y1, y2 = mid_y - half_width, mid_y + half_width
            height_field[x1:x2, y1:y2] = step_height * (i + 1)
            x1 = x2
        return x1

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # Put first goal at spawn area
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    for i in range(4):  # Adding 4 sections of walkways and staircases
        cur_x = add_walkway(cur_x, walkway_length, mid_y)
        goals[i*2 + 1] = [cur_x - walkway_length / 2, mid_y]  # Set goal at the center of each walkway

        # Adding a staircase after walkway
        steps = 3  # Number of steps in the staircase
        cur_x = add_staircase(cur_x, mid_y, steps)
        goals[i*2 + 2] = [cur_x - (np.random.uniform(step_width_min, step_width_max) / 2), mid_y]  # Goal at the end of staircase

    # Place the last goal at the end of the final walkway
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0  # Ensure the final section is flat ground

    return height_field, goals