import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """A combination of sideways facing ramps, narrow beams, and staggered platforms to challenge the quadruped's balance, jumping, and climbing abilities."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]
    
    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    
    # Parameters
    ramp_length = 1.0 - 0.3 * difficulty
    beam_length = 1.0 - 0.3 * difficulty
    platform_length = 1.0 - 0.3 * difficulty

    ramp_length, beam_length, platform_length = m_to_idx([ramp_length, beam_length, platform_length])
    
    ramp_width = np.random.uniform(0.4, 0.6)
    beam_width = 0.15 + 0.15 * difficulty
    platform_width = np.random.uniform(1.0, 1.2)
    
    ramp_height_min, ramp_height_max = 0.1 + 0.2 * difficulty, 0.2 + 0.3 * difficulty
    gap_length = 0.2 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)
    
    mid_y = m_to_idx(width) // 2
    
    def add_ramp(start_x, end_x, mid_y, direction):
        width = m_to_idx(ramp_width)
        slope = np.linspace(0, np.random.uniform(ramp_height_min, ramp_height_max), end_x - start_x)[::direction]
        height_field[start_x:end_x, mid_y-width//2:mid_y+width//2] = slope[:, None]
    
    def add_beam(start_x, end_x, mid_y):
        width = m_to_idx(beam_width)
        height_field[start_x:end_x, mid_y-width//2:mid_y+width//2] = np.random.uniform(ramp_height_min, ramp_height_max)
    
    def add_platform(start_x, end_x, mid_y):
        width = m_to_idx(platform_width)
        height_field[start_x:end_x, mid_y-width//2:mid_y+width//2] = np.random.uniform(ramp_height_min, ramp_height_max)
    
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]
    
    cur_x = spawn_length
    elements = []
    for i in range(3):
        elements.append(("ramp", cur_x))
        cur_x += ramp_length
        elements.append(("gap", cur_x))
        cur_x += gap_length
        elements.append(("beam", cur_x))
        cur_x += beam_length
        elements.append(("gap", cur_x))
        cur_x += gap_length
        elements.append(("platform", cur_x))
        cur_x += platform_length
        elements.append(("gap", cur_x))
        cur_x += gap_length
        
    # Adding first goal after the spawn
    goals[1] = [spawn_length + m_to_idx(2.0), mid_y]
    
    # Adding ramps, beams, and platforms
    for i, (elem, x_pos) in enumerate(elements):
        if elem == "ramp":
            add_ramp(x_pos, x_pos + ramp_length, mid_y, direction=(-1)**i)
        elif elem == "beam":
            add_beam(x_pos, x_pos + beam_length, mid_y)
        elif elem == "platform":
            add_platform(x_pos, x_pos + platform_length, mid_y)
        if i % 2 == 0:
            goals[(i // 2) + 2] = [x_pos + platform_length // 2, mid_y]  # Add goals after the elements
    
    # Add final goal behind the last platform and fill the remaining flat ground
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0
    
    return height_field, goals