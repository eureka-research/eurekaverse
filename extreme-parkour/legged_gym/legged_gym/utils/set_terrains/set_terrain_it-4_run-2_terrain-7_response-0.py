import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Obstacle course with staggered platforms and narrow beams for the robot to climb and balance on."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]
    
    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and beam dimensions
    platform_width = m_to_idx(np.random.uniform(1.0, 1.2))
    platform_length = m_to_idx(1.0 - 0.4 * difficulty)
    platform_height_min, platform_height_max = 0.2 * difficulty, 0.4 + 0.3 * difficulty
    
    beam_width = m_to_idx(np.random.uniform(0.2, 0.3))
    beam_length = m_to_idx(np.random.uniform(0.8, 1.2))
    gap_length = m_to_idx(0.3 + 0.7 * difficulty)
    
    mid_y = m_to_idx(width) // 2
    
    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_beam(start_x, end_x, mid_y):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        beam_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = beam_height
    
    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]
    
    cur_x = spawn_length
    num_obstacles = 4

    for i in range(num_obstacles):
        add_platform(cur_x, cur_x + platform_length, mid_y)
        goals[i * 2 + 1] = [cur_x + platform_length // 2, mid_y]
        cur_x += platform_length + gap_length
        
        add_beam(cur_x, cur_x + beam_length, mid_y)
        goals[i * 2 + 2] = [cur_x + beam_length // 2, mid_y]
        cur_x += beam_length + gap_length
        
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals