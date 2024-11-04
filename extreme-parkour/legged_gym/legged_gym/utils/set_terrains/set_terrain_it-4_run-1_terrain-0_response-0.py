import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Dynamic terrain with moving platforms and varying heights for the robot to balance, climb, and jump across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length = 0.4
    platform_length = m_to_idx(platform_length)
    platform_width = 1.0
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.0 + 0.2 * difficulty, 0.1 + 0.3 * difficulty
    gap_length_min, gap_length_max = 0.2, 0.6 + 0.5 * difficulty
    gap_length_min, gap_length_max = m_to_idx(gap_length_min), m_to_idx(gap_length_max)

    ramp_length = 0.8
    ramp_length = m_to_idx(ramp_length)
    ramp_height_min, ramp_height_max = 0.2, 0.4 + 0.3 * difficulty
    
    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_ramp(start_x, end_x, mid_y, direction):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        slant = np.linspace(0, ramp_height, num=y2-y1)[::direction]
        slant = slant[None, :]  # Add a dimension for broadcasting to x
        height_field[x1:x2, y1:y2] = slant

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at spawn

    cur_x = spawn_length

    for i in range(4):
        dx = np.random.randint(gap_length_min, gap_length_max)
        dy = np.random.randint(m_to_idx(0.0), m_to_idx(0.6))

        if i % 2 == 0:
            add_platform(cur_x, cur_x + platform_length, mid_y + dy)
            goals[i + 1] = [cur_x + platform_length // 2, mid_y + dy]
        else:
            add_ramp(cur_x, cur_x + ramp_length, mid_y + dy, direction=(-1) ** i)
            goals[i + 1] = [cur_x + ramp_length // 2, mid_y + dy]

        cur_x += platform_length + dx if i % 2 == 0 else ramp_length + dx

    # Adding final straight-run obstacle and a final goal
    final_run_length = m_to_idx(2.5)
    final_run_ramp = m_to_idx(2.0)
    final_run_height = np.random.uniform(0.2, 0.3 + 0.1 * difficulty)
    half_width = platform_width // 2
    y1, y2 = mid_y - half_width, mid_y + half_width
    ramp_height = np.linspace(0, final_run_height, num=final_run_ramp)
    height_field[cur_x:cur_x + final_run_ramp, y1:y2] = ramp_height[:, np.newaxis]
    cur_x += final_run_ramp

    y_current = height_field[cur_x:cur_x + final_run_length, y1:y2][-1, 0]
    height_field[cur_x:cur_x + final_run_length, y1:y2] = y_current  # Ending straight path

    goals[-1] = [cur_x + final_run_length // 2, mid_y]

    return height_field, goals