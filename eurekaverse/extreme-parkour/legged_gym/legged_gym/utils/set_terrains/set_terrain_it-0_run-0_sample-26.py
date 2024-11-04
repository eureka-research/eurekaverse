import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Narrow passages and low walls for the robot to navigate and climb over."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Convert to quantized indices
    course_length = m_to_idx(length)
    course_width = m_to_idx(width)
    half_width = course_width // 2
    wall_height_min = 0.1 * difficulty
    wall_height_max = 0.3 * difficulty

    def add_wall(start_x, end_x, y_position, height):
        """Adds a wall along the y-axis at a given x range and height."""
        height_field[start_x:end_x, y_position:y_position + m_to_idx(0.05)] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Set first goal at the end of the spawn
    goals[0] = [m_to_idx(1), half_width]

    cur_x = spawn_length
    obstacles = ['narrow_passage', 'wall']
    goal_idx = 1

    while cur_x < course_length - m_to_idx(1):
        obstacle_type = random.choice(obstacles)

        if obstacle_type == 'narrow_passage':
            passage_width = m_to_idx(0.5 + 0.5 * (1 - difficulty))  # Width decreases with difficulty
            passage_left = half_width - passage_width // 2
            passage_right = half_width + passage_width // 2
            height_field[cur_x:cur_x + m_to_idx(2), 0:passage_left] = -0.5
            height_field[cur_x:cur_x + m_to_idx(2), passage_right:] = -0.5
            goals[goal_idx] = [cur_x + m_to_idx(1), half_width]
            cur_x += m_to_idx(3)  # Move beyond the narrow passage
        elif obstacle_type == 'wall':
            wall_height = np.random.uniform(wall_height_min, wall_height_max)
            x_range = m_to_idx(2)
            y_positions = [half_width - m_to_idx(1), half_width + m_to_idx(0.5)]
            for y in y_positions:
                add_wall(cur_x, cur_x + x_range, y, wall_height)
            goals[goal_idx] = [cur_x + x_range // 2, half_width]
            cur_x += x_range + m_to_idx(1)  # Move beyond the wall
        
        goal_idx += 1
        if goal_idx >= 8:
            break

    goals[-1] = [course_length - m_to_idx(1), half_width]
    
    return height_field, goals