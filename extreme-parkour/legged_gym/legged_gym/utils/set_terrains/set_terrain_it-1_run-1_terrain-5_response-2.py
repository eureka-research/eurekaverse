import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Alternating narrow beams and staggered steps to test the robot’s balance and adaptability."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (is_instance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Narrow beam dimensions
    beam_length_min = 1.5  # Increased the length for complexity
    beam_length_max = 2.5
    beam_width = 0.4  # Narrow beam
    beam_height_min = 0.1 * difficulty
    beam_height_max = 0.3 * difficulty

    # Staggered step dimensions (stepping stones)
    step_length = 0.4
    step_width = 0.4
    step_height_min = 0.05 * difficulty
    step_height_max = 0.2 * difficulty
    step_spacing = 0.2 + 0.3 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, beam_length, mid_y, beam_height):
        half_width = m_to_idx(beam_width) // 2
        end_x = start_x + m_to_idx(beam_length)
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[start_x:end_x, y1:y2] = beam_height

    def add_step(start_x, start_y, step_height):
        end_x = start_x + m_to_idx(step_length)
        end_y = start_y + m_to_idx(step_width)
        height_field[start_x:end_x, start_y:end_y] = step_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(4):  # Alternating 4 beams and staggered steps
        # Add beam
        beam_length = random.randint(m_to_idx(beam_length_min), m_to_idx(beam_length_max))
        beam_height = random.uniform(beam_height_min, beam_height_max)
        
        add_beam(cur_x, beam_length, mid_y, beam_height)
        
        # Place goal in the middle of beam
        goals[2 * i + 1] = [cur_x + beam_length // 2, mid_y]

        cur_x += beam_length + m_to_idx(step_spacing)
        
        # Add staggered steps
        for j in range(3):  # Adding 3 steps successively
            step_height = random.uniform(step_height_min, step_height_max)
            step_y = mid_y + (2 * j - 3) * m_to_idx(step_width)  # Alternating step position
            
            add_step(cur_x, step_y, step_height)

            # Place goal at the last step
            if j == 2:
                goals[2 * i + 2] = [cur_x + m_to_idx(step_length) // 2, step_y + m_to_idx(step_width) // 2]

            cur_x += m_to_idx(step_spacing + step_length)

    # Add final goal behind the last step
    height_field[cur_x:, :] = 0
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    return height_field, goals