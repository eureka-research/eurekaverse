import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Series of tilted platforms and narrow beams for balance and control training."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    
    # Platform and beam specifications
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_height_min, platform_height_max = 0.1 + 0.1 * difficulty, 0.3 + 0.2 * difficulty
    
    beam_width_min, beam_width_max = 0.3 / (1 + difficulty), 0.4 / (1 + difficulty)
    beam_length = 1.5 - 0.5 * difficulty  # make beams longer as difficulty increases
    beam_length = m_to_idx(beam_length)
    
    gap_length = 0.3 + 0.4 * difficulty
    gap_length = m_to_idx(gap_length)
    
    mid_y = m_to_idx(width) // 2
    
    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[start_x:end_x, y1:y2] = height
        
    def add_beam(start_x, start_y, length, height=0):
        end_x = start_x + length
        y1, y2 = start_y - beam_width_min // 2, start_y + beam_width_min // 2
        height_field[start_x:end_x, y1:y2] = height
        return end_x
    
    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]
    
    current_x = spawn_length
    
    # Add a sequence of tilted platforms and narrow beams
    for i in range(3):
        # Add tilted platforms
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        half_width = m_to_idx(np.random.uniform(0.4, 1.0))
        x1, x2 = current_x, current_x + platform_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = platform_height
        
        # Goal in the center of the platform
        goals[2 * i + 1] = [current_x + platform_length // 2, mid_y]
        current_x += platform_length + gap_length

        # Add narrow beam
        current_x = add_beam(current_x, mid_y, beam_length, platform_height)
        goals[2 * i + 2] = [current_x - beam_length // 2, mid_y]
        current_x += gap_length
    
    # Add final platform goal
    platform_height = np.random.uniform(platform_height_min, platform_height_max)
    x1, x2 = current_x, current_x + platform_length
    half_width = m_to_idx(np.random.uniform(0.4, 1.0))
    y1, y2 = mid_y - half_width, mid_y + half_width
    height_field[x1:x2, y1:y2] = platform_height
    goals[-1] = [x1 + platform_length // 2, mid_y]
    
    return height_field, goals