import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Series of narrow beams and steps where the robot needs to balance and climb."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Setup parameters for the obstacle course
    beam_length_min = m_to_idx(1.0)
    beam_length_max = m_to_idx(2.0)
    beam_width = m_to_idx(0.5)
    beam_height = m_to_idx(0.1 + 0.4 * difficulty)
    step_height_min = m_to_idx(0.05)
    step_height_max = m_to_idx(0.3)
    step_length = m_to_idx(0.6)
    step_width = m_to_idx(1.0)

    # Middle Y coordinate for the beams and steps
    mid_y = m_to_idx(width / 2)
    
    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length

    for i in range(4):
        # Alternating between beams and steps
        if i % 2 == 0:
            # Beam generation
            beam_length = np.random.randint(beam_length_min, beam_length_max)
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)
            
            x1, x2 = cur_x, cur_x + beam_length
            y1, y2 = mid_y + dy - beam_width // 2, mid_y + dy + beam_width // 2
            
            height_field[x1:x2, y1:y2] = beam_height
            goals[i+1] = [x1 + beam_length / 2, mid_y + dy]
            cur_x += beam_length + m_to_idx(0.2)

        else:
            # Step generation
            num_steps = np.random.randint(2, 4)
            for j in range(num_steps):
                step_height = np.random.uniform(step_height_min, step_height_max)
                x1, x2 = cur_x, cur_x + step_length
                y1, y2 = mid_y - step_width // 2, mid_y + step_width // 2
                height_field[x1:x2, y1:y2] = step_height * (j+1)
                cur_x += step_length

            goals[i+1] = [cur_x - step_length / 2, mid_y]

    # Final goal after the last obstacle
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals