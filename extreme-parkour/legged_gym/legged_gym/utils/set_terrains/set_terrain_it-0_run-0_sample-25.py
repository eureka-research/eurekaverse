import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Obstacle course featuring inclined ramps, steps, and narrow bridges."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    def add_ramp(start_x, start_y, end_x, end_y, height_start, height_end):
        """Adds a ramp from (start_x, start_y) to (end_x, end_y) with a linear height gradient."""
        x1, y1 = start_x, start_y
        x2, y2 = end_x, end_y

        dx = x2 - x1
        dy = y2 - y1
        dh = height_end - height_start

        for i in range(dx):
            height_field[x1 + i, y1:y2] = height_start + dh * (i / dx)
    
    def add_steps(base_x, base_y, step_height, step_length, num_steps):
        """Adds a series of steps."""
        half_length = step_length // 2
        for i in range(num_steps):
            x1 = base_x + i * step_length
            x2 = base_x + (i + 1) * step_length
            y1 = base_y - half_length
            y2 = base_y + half_length
            height_field[x1:x2, y1:y2] = (i + 1) * step_height
    
    def add_bridge(start_x, start_y, bridge_length):
        """Adds a narrow bridge."""
        half_width = m_to_idx(0.2)  # 0.4 meters wide
        height_field[start_x:start_x + bridge_length, start_y - half_width:start_y + half_width] = 0.5 + 0.4 * difficulty

    mid_y = m_to_idx(width) // 2

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # Set goals at strategic points
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # 1. First ramp
    add_ramp(spawn_length, mid_y - m_to_idx(0.5), spawn_length + m_to_idx(1), mid_y + m_to_idx(0.5), 0, 0.2 + 0.3 * difficulty)
    goals[1] = [spawn_length + m_to_idx(0.5), mid_y]

    # 2. Steps
    add_steps(spawn_length + m_to_idx(1), mid_y, step_height=0.1 + 0.1 * difficulty, step_length=m_to_idx(0.3), num_steps=5)
    goals[2] = [spawn_length + m_to_idx(2), mid_y]

    # 3. Second ramp
    add_ramp(spawn_length + m_to_idx(2), mid_y - m_to_idx(0.5), spawn_length + m_to_idx(3.5), mid_y + m_to_idx(0.5), 0.2 + 0.3 * difficulty, 0)
    goals[3] = [spawn_length + m_to_idx(2.5), mid_y]

    # 4. Bridge
    add_bridge(spawn_length + m_to_idx(3.5), mid_y, bridge_length=m_to_idx(1))
    goals[4] = [spawn_length + m_to_idx(4), mid_y]

    # 5. Step up and down
    add_steps(spawn_length + m_to_idx(4.5), mid_y, step_height=0.1 + 0.1 * difficulty, step_length=m_to_idx(0.3), num_steps=3)
    add_steps(spawn_length + m_to_idx(5.5), mid_y, step_height=-0.1 - 0.1 * difficulty, step_length=m_to_idx(0.3), num_steps=3)
    goals[5] = [spawn_length + m_to_idx(5), mid_y]

    # 6. Final ramp
    add_ramp(spawn_length + m_to_idx(6), mid_y - m_to_idx(0.5), spawn_length + m_to_idx(7), mid_y + m_to_idx(0.5), 0, 0.2 + 0.3 * difficulty)
    goals[6] = [spawn_length + m_to_idx(6.5), mid_y]

    # Last goal
    goals[7] = [spawn_length + m_to_idx(8), mid_y]

    return height_field, goals