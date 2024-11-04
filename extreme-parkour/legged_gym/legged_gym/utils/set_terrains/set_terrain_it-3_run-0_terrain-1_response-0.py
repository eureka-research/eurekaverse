import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Stairs, narrow beams, and ramps for the robot to climb, balance, and navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    mid_y = m_to_idx(width) // 2
    spawn_length = m_to_idx(2)
    
    # General obstacle dimensions
    step_height_diff = 0.18 * difficulty
    beam_width = 0.16 * (1 - difficulty)
    ramp_slope = 0.2 * difficulty

    def add_step_stair(start_x, num_steps, height_diff_per_step):
        for i in range(num_steps):
            height = i * height_diff_per_step
            x1, x2 = start_x + i * step_length, start_x + (i + 1) * step_length
            y1, y2 = mid_y - step_width // 2, mid_y + step_width // 2
            height_field[x1:x2, y1:y2] = height

    def add_narrow_beam(start_x, length, width):
        half_width = m_to_idx(width) // 2
        x1, x2 = start_x, start_x + m_to_idx(length)
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height_diff * difficulty

    def add_ramp(start_x, length, slope):
        x1, x2 = start_x, start_x + m_to_idx(length)
        y1, y2 = mid_y - ramp_width // 2, mid_y + ramp_width // 2
        ramp_height = np.linspace(0, slope * length, x2 - x1)[:, None]
        height_field[x1:x2, y1:y2] = ramp_height

    # Set spawn area to flat ground
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    current_x = spawn_length
    total_goals = 1

    # Design the obstacle course
    num_obstacles = 5 + round(3 * difficulty)
    step_length = m_to_idx(0.4)
    step_width = m_to_idx(1.2)
    ramp_width = m_to_idx(1.0)
    
    for obstacle in range(num_obstacles):
        # Randomly choose obstacle type
        obstacle_type = random.choice(['step', 'beam', 'ramp'])

        if obstacle_type == 'step':
            add_step_stair(current_x, 3, step_height_diff)
            goals[total_goals] = [current_x + step_length * 1.5, mid_y]
            current_x += step_length * 3
        elif obstacle_type == 'beam':
            add_narrow_beam(current_x, 2.0, beam_width)
            goals[total_goals] = [current_x + m_to_idx(1.0), mid_y]
            current_x += m_to_idx(2.0)
        elif obstacle_type == 'ramp':
            add_ramp(current_x, 2.0, ramp_slope)
            goals[total_goals] = [current_x + m_to_idx(1.0), mid_y]
            current_x += m_to_idx(2.0)
        
        # Ensure goals are within bounds
        total_goals += 1
        if total_goals >= 8:
            break

    # Fill remaining goals if any
    while total_goals < 8:
        current_x += m_to_idx(1.0)
        goals[total_goals] = [current_x, mid_y]
        total_goals += 1

    # Flatten the terrain after the last obstacle
    height_field[current_x:, :] = 0

    return height_field, goals