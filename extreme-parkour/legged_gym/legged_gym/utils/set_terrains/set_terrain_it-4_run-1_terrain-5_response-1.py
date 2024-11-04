import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Staggered elevated steps and bridges for the robot to climb, navigate and balance across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up staggered step and elevated bridge dimensions
    # We make the step height near 0 at minimum difficulty so the quadruped can learn to climb up
    step_length = 0.8 - 0.2 * difficulty
    step_length = m_to_idx(step_length)
    step_width = np.random.uniform(0.4, 0.6)
    step_width = m_to_idx(step_width)
    step_height_min, step_height_max = 0.1 * difficulty, 0.3 * difficulty
    
    bridge_length = 1.0 - 0.3 * difficulty
    bridge_length = m_to_idx(bridge_length)
    bridge_width = np.random.uniform(0.5, 0.8)
    bridge_width = m_to_idx(bridge_width)
    bridge_height_min, bridge_height_max = 0.2 * difficulty, 0.5 * difficulty

    gap_length = 0.2 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_step(start_x, end_x, mid_y, height):
        half_width = step_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_bridge(start_x, end_x, mid_y, height):
        half_width = bridge_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height
    
    dx_min, dx_max = -0.05, 0.05
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.1, 0.1
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn area
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]
    
    cur_x = spawn_length
    for i in range(3):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        step_height = np.random.uniform(step_height_min, step_height_max)
        add_step(cur_x, cur_x + step_length + dx, mid_y + dy, step_height)

        # Put goal in the center of the step
        goals[i+1] = [cur_x + (step_length + dx) / 2, mid_y + dy]

        cur_x += step_length + dx + gap_length

    for i in range(3, 7):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        bridge_height = np.random.uniform(bridge_height_min, bridge_height_max)
        add_bridge(cur_x, cur_x + bridge_length + dx, mid_y + dy, bridge_height)

        # Put goal in the center of the bridge
        goals[i+1] = [cur_x + (bridge_length + dx) / 2, mid_y + dy]

        cur_x += bridge_length + dx + gap_length
    
    # Add final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals