import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Series of ascending and descending ramps for the robot to navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Ramps dimensions
    ramp_length_min, ramp_length_max = 1.0, 2.0
    ramp_length_range = ramp_length_max - ramp_length_min
    ramp_height_range = 0.2 * difficulty

    def add_ramp(start_x, ramp_length, height_increment):
        ramp_start_y = m_to_idx(width // 2) - m_to_idx(1)  # Centered in the width
        ramp_end_y = ramp_start_y + m_to_idx(2)  # 1m width for ramps
        
        x_indices = np.arange(start_x, start_x + ramp_length)
        heights = np.linspace(0, height_increment, ramp_length)
        
        height_field[x_indices[:, None], ramp_start_y:ramp_end_y] += heights[:, None]  # Build ascending ramp
        return start_x + ramp_length, height_increment

    def add_flat(start_x, flat_length, init_height):
        flat_start_y = m_to_idx(width // 2) - m_to_idx(1)
        flat_end_y = flat_start_y + m_to_idx(2)

        height_field[start_x:start_x+flat_length, flat_start_y:flat_end_y] = init_height
        return start_x + flat_length

    spawn_length = m_to_idx(2)
    goal_index = 0

    # Initial flat with the first goal at the spawn area
    height_field[0:spawn_length, :] = 0.0
    goals[goal_index] = [spawn_length - m_to_idx(0.5), m_to_idx(width // 2)]
    goal_index += 1

    cur_x = spawn_length
    current_height = 0.0
    for i in range(4):  # Alternate between ramps and flats for 4 pairs
        # Ascending ramp
        ramp_length = m_to_idx(random.uniform(ramp_length_min, ramp_length_min + ramp_length_range))
        height_increment = random.uniform(0.05, ramp_height_range)
        cur_x, new_height = add_ramp(cur_x, ramp_length, height_increment)
        goals[goal_index] = [cur_x - m_to_idx(0.5), m_to_idx(width // 2)]
        goal_index += 1
        current_height = new_height

        # Flat area before descending
        flat_length = m_to_idx(random.uniform(0.5, 1.0))
        cur_x = add_flat(cur_x, flat_length, current_height)
        goals[goal_index] = [cur_x - m_to_idx(0.5), m_to_idx(width // 2)]
        goal_index += 1

        # Descending ramp
        ramp_length = m_to_idx(random.uniform(ramp_length_min, ramp_length_min + ramp_length_range))
        height_decrement = -random.uniform(0.05, ramp_height_range)
        cur_x, new_height = add_ramp(cur_x, ramp_length, height_decrement)
        goals[goal_index] = [cur_x - m_to_idx(0.5), m_to_idx(width // 2)]
        goal_index += 1
        current_height += height_decrement
    
    # Final flat area leading to the last goal
    flat_length = m_to_idx(2)  # Ensure there is a flat space before finish
    cur_x = add_flat(cur_x, flat_length, current_height)
    goals[goal_index] = [cur_x, m_to_idx(width // 2)]

    return height_field, goals