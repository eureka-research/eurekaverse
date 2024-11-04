import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """A set of steps followed by narrow beams on which the robot has to balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Step dimensions
    num_steps = 3 + int(difficulty * 5)
    step_height = 0.08 + 0.1 * difficulty
    step_height = m_to_idx(step_height)
    step_length = 1.0
    step_length = m_to_idx(step_length)
    step_width = width
    step_width = m_to_idx(step_width)

    # Beam dimensions
    num_beams = 4
    beam_length_min = 1.0 + 0.5 * difficulty
    beam_length_max = 2.5
    beam_width = 0.4  # Narrow beams (minimum allowed)
    beam_width = m_to_idx(beam_width)
    beam_height = -0.1  # Slightly below ground level to balance on
    beam_height = m_to_idx(beam_height)
    
    # Initializing background terrain to flat ground with default height 0
    height_field[:, :] = -1.0  # Pits as default terrain for more challenge

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), m_to_idx(width // 2)] 

    cur_x = spawn_length

    # Adding steps
    for i in range(num_steps):
        height_field[cur_x:cur_x + step_length, :] = (i + 1) * step_height
        cur_x += step_length

        if i < 7:  # Assign goals only to the first 7 steps as 8th will be for beams
            goals[i+1] = [cur_x - step_length // 2, m_to_idx(width // 2)] 

    # Adding narrow beams
    for i in range(num_beams):
        beam_length = random.uniform(beam_length_min, beam_length_max)
        beam_length = m_to_idx(beam_length)
        
        start_x = cur_x
        end_x = cur_x + beam_length
        start_y = m_to_idx((width - beam_width * 2) / 4)  # centered beam width with a little margin
        
        height_field[start_x:end_x, start_y:start_y + beam_width] = beam_height
        
        # Set goal in the middle of each beam
        if len([goal for goal in goals if goal[0] != 0]) < 8:
            goals[len([goal for goal in goals if goal[0] != 0])] = [(start_x + end_x) // 2, m_to_idx(width // 2)]

        cur_x = end_x

    # Adding final goal behind the last beam
    goals[-1] = [m_to_idx(length) - m_to_idx(0.5), m_to_idx(width // 2)]
    height_field[cur_x:, :] = 0

    return height_field, goals