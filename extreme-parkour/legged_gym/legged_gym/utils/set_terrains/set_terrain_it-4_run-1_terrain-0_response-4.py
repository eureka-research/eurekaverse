import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Complex obstacle course with elevated platforms, ramps, and uneven stepping stones."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length_min = 0.4
    platform_length_max = 1.0 - 0.3 * difficulty
    platform_height_min, platform_height_max = 0.25 * difficulty, 0.5 * difficulty
    gap_length_min = 0.3
    gap_length_max = 0.7 * difficulty
    ramp_length = 1.0
    ramp_height = 0.3 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = m_to_idx(random.uniform(1.0, 1.5))
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[start_x:end_x, y1:y2] = height

    def add_ramp(start_x, end_x, mid_y, height, direction):
        half_width = m_to_idx(random.uniform(1.0, 1.2))
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slope = np.linspace(0, height, end_x - start_x) if direction == "up" else np.linspace(height, 0, end_x - start_x)
        height_field[x1:x2, y1:y2] = slope[:, None]

    def add_stepping_stones(start_x, end_x, mid_y, height, num_stones):
        stone_length, stone_width = m_to_idx(0.3), m_to_idx(0.3)
        x_positions = np.linspace(start_x, end_x, num_stones + 1)[:-1]
        for x in x_positions:
            y_offset = random.randint(-m_to_idx(0.5), m_to_idx(0.5))
            y_start, y_end = mid_y + y_offset - stone_width // 2, mid_y + y_offset + stone_width // 2
            x_start, x_end = x, x + stone_length
            height_field[x_start:x_end, y_start:y_end] = height

    cur_x = m_to_idx(2)
    spawn_length = m_to_idx(2)
    height_field[:spawn_length, :] = 0  # Flat ground for spawning
    goals[0] = [cur_x - m_to_idx(0.5), mid_y]  # First goal at the end of spawn area

    # Add platforms, ramps, and stepping stones in sequence
    for i in range(5):
        platform_length = m_to_idx(random.uniform(platform_length_min, platform_length_max))
        platform_height = random.uniform(platform_height_min, platform_height_max)
        add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)
        goals[i + 1] = [cur_x + platform_length // 2, mid_y]
        cur_x += platform_length + m_to_idx(random.uniform(gap_length_min, gap_length_max))

        # Add alternate ramps
        ramp_direction = "up" if i % 2 == 0 else "down"
        add_ramp(cur_x, cur_x + ramp_length, mid_y, ramp_height, ramp_direction)
        goals[i + 2] = [cur_x + ramp_length // 2, mid_y]
        cur_x += ramp_length + m_to_idx(random.uniform(gap_length_min, gap_length_max))

        # Add stepping stones
        add_stepping_stones(cur_x, cur_x + m_to_idx(1.0), mid_y, random.uniform(platform_height_min, platform_height_max), 3)
        goals[i + 3] = [cur_x + m_to_idx(0.5), mid_y]

    # Place the final goal at the end of the last obstacle
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0  # Ensure terrain is flat after the last obstacle

    return height_field, goals