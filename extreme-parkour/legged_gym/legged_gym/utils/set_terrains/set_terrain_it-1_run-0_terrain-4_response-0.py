import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Urban themed course with stairs, ramps, and narrow walkways to test climbing and balancing skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    mid_y = m_to_idx(width) // 2
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    def add_stairs(start_x, start_y, step_height, step_depth, num_steps):
        """Adds a staircase starting at (start_x, start_y)."""
        step_height_idx = m_to_idx(step_height)
        step_depth_idx = m_to_idx(step_depth)
        half_width = m_to_idx(1) // 2
        
        for i in range(num_steps):
            height_field[start_x + i * step_depth_idx: start_x + (i + 1) * step_depth_idx, start_y - half_width: start_y + half_width] = (i+1) * step_height_idx / field_resolution

    def add_ramp(start_x, start_y, length, height_diff):
        """Adds a ramp starting at (start_x, start_y)."""
        ramp_length_idx = m_to_idx(length)
        ramp_height_diff_idx = m_to_idx(height_diff)
        half_width = m_to_idx(1) // 2

        for i in range(ramp_length_idx):
            height_field[start_x + i, start_y - half_width: start_y + half_width] = (ramp_height_diff_idx * i / ramp_length_idx) / field_resolution

    def add_narrow_walkway(start_x, start_y, length):
        """Adds a narrow walkway starting at (start_x, start_y)."""
        walkway_length_idx = m_to_idx(length)
        half_width = m_to_idx(0.4) // 2
        
        height_field[start_x: start_x + walkway_length_idx, start_y - half_width: start_y + half_width] = 0.2

    current_x = spawn_length
    step_height = 0.1 + 0.1 * difficulty
    step_depth = 0.2 + 0.1 * difficulty
    num_steps = 3 + int(difficulty * 5)
    gap_between_obstacles = m_to_idx(0.5)

    # Add a staircase
    add_stairs(current_x, mid_y, step_height, step_depth, num_steps)
    current_x += m_to_idx(step_depth) * num_steps + gap_between_obstacles
    goals[1] = [current_x - gap_between_obstacles, mid_y]

    # Add a ramp
    ramp_length = 2 + 2 * difficulty
    ramp_height_diff = 0.4 + 0.4 * difficulty
    add_ramp(current_x, mid_y, ramp_length, ramp_height_diff)
    current_x += m_to_idx(ramp_length) + gap_between_obstacles
    goals[2] = [current_x - gap_between_obstacles, mid_y]

    # Add a narrow walkway
    walkway_length = 3 + 3 * difficulty
    add_narrow_walkway(current_x, mid_y, walkway_length)
    current_x += m_to_idx(walkway_length) + gap_between_obstacles
    goals[3] = [current_x - gap_between_obstacles, mid_y]

    # Add another staircase
    add_stairs(current_x, mid_y, step_height, step_depth, num_steps)
    current_x += m_to_idx(step_depth) * num_steps + gap_between_obstacles
    goals[4] = [current_x - gap_between_obstacles, mid_y]

    # Add another ramp
    add_ramp(current_x, mid_y, ramp_length, ramp_height_diff)
    current_x += m_to_idx(ramp_length) + gap_between_obstacles
    goals[5] = [current_x - gap_between_obstacles, mid_y]

    # Add another narrow walkway
    add_narrow_walkway(current_x, mid_y, walkway_length)
    current_x += m_to_idx(walkway_length) + gap_between_obstacles
    goals[6] = [current_x - gap_between_obstacles, mid_y]

    # Final goal
    goals[7] = [current_x + m_to_idx(0.5), mid_y]

    return height_field, goals