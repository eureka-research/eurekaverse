import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Combination of narrow beams, jumps and varying height platforms for the robot to navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    mid_y = m_to_idx(width / 2)
    spawn_length = m_to_idx(2)

    # Set spawn area to flat ground
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]
    
    cur_x = spawn_length
    cur_y = mid_y
    obstacle_count = 1

    # Parameters for various obstacles
    def add_narrow_beam(start_x, end_x, mid_y):
        y1, y2 = mid_y - m_to_idx(0.1), mid_y + m_to_idx(0.1)
        beam_height = random.uniform(0.2, 0.5) * difficulty
        height_field[start_x:end_x, y1:y2] = beam_height

    def add_jumping_gap(start_x, width_gap):
        end_x = start_x + width_gap
        height_field[start_x:end_x, :] = -1.0
        return end_x

    def add_platform(start_x, platform_length, platform_width, height):
        end_x = start_x + platform_length
        y1, y2 = mid_y - m_to_idx(platform_width / 2), mid_y + m_to_idx(platform_width / 2)
        height_field[start_x:end_x, y1:y2] = height

    # Create obstacles
    while obstacle_count < 8:
        # Choose an obstacle type
        obstacle_type = random.choice(['beam', 'gap', 'platform'])
        
        if obstacle_type == 'beam':
            beam_length = random.uniform(1.0, 1.5)
            beam_length = m_to_idx(beam_length)
            add_narrow_beam(cur_x, cur_x + beam_length, cur_y)
            goals[obstacle_count] = [(cur_x + cur_x + beam_length) / 2, cur_y]
            cur_x += beam_length
        elif obstacle_type == 'gap':
            gap_length = random.uniform(0.5, 1.0) * difficulty
            gap_length = m_to_idx(gap_length)
            cur_x = add_jumping_gap(cur_x, gap_length)
            goals[obstacle_count] = [cur_x - gap_length / 2, cur_y]
        elif obstacle_type == 'platform':
            platform_length = random.uniform(1.0, 1.5)
            platform_length = m_to_idx(platform_length)
            platform_width = random.uniform(0.4, 1.0)
            platform_height = random.uniform(0.2, 0.5) * difficulty
            add_platform(cur_x, platform_length, platform_width, platform_height)
            goals[obstacle_count] = [cur_x + platform_length / 2, cur_y]
            cur_x += platform_length
        
        # Add a gap or flat terrain after every obstacle
        cur_x += m_to_idx(0.2)
        obstacle_count += 1

    # Adding final goal behind the last obstacle
    final_gap = m_to_idx(1.0)
    goals[-1] = [cur_x + final_gap, mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals