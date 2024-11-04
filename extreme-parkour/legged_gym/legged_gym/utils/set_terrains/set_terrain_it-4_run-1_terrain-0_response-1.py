import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Advanced course with steep ramps and narrow bridges for the robot to climb, balance, and jump across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Obstacle specifications based on difficulty
    ramp_height_base = 0.1 + 0.4 * difficulty
    ramp_length = 2.0 - 0.5 * difficulty
    ramp_length = m_to_idx(ramp_length)
    
    bridge_width_min = 0.3
    bridge_width_max = 0.8 - 0.3 * difficulty

    gap_length_base = 0.4 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length_base)

    def add_ramp(start_x, end_x, mid_y, height):
        slope = np.linspace(0, height, num=end_x-start_x)
        height_field[start_x:end_x, mid_y] = slope

    def add_bridge(start_x, end_x, start_y, width):
        half_width = m_to_idx(width) // 2
        y1, y2 = max(0, start_y - half_width), min(m_to_idx(width * field_resolution), start_y + half_width)
        height_field[start_x:end_x, y1:y2] = height_field[start_x:start_x + 1, y1:y2]

    # Initial settings for the course
    mid_y = m_to_idx(width) // 2
    cur_x = spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # Set the start goal at the end of the spawn area
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Add first ramp and goal
    ramp_height = ramp_height_base
    add_ramp(cur_x, cur_x + ramp_length, mid_y, ramp_height)
    goals[1] = [cur_x + ramp_length // 2, mid_y]
    cur_x += ramp_length + gap_length

    # Add series of narrow bridges and goals
    for i in range(6):
        bridge_width = random.uniform(bridge_width_min, bridge_width_max)
        bridge_length = m_to_idx(1.5 + 0.5 * difficulty)
        bridge_start_y = mid_y + m_to_idx(random.uniform(-1, 1))

        add_bridge(cur_x, cur_x + bridge_length, bridge_start_y, bridge_width)
        goals[i + 2] = [cur_x + bridge_length // 2, bridge_start_y]

        # Add next ramp
        cur_x += bridge_length + gap_length
        ramp_height += 0.1 * difficulty
        add_ramp(cur_x, cur_x + ramp_length, mid_y, ramp_height)
        goals[i + 3] = [cur_x + ramp_length // 2, mid_y]

        cur_x += ramp_length + gap_length

    # Adjust final goal and flat ground at end of course
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals