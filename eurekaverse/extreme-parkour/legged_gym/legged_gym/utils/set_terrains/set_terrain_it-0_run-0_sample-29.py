import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Maze-like course with narrow corridors, turns and various height variations for the robot to navigate through."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    course_length = m_to_idx(length)
    course_width = m_to_idx(width)

    # Parameters based on difficulty
    corridor_width = m_to_idx(0.4 + 0.4 * (1 - difficulty))  # Corridors get narrower with difficulty
    max_height_variation = 0.1 + 0.4 * difficulty  # Height varies more with higher difficulty
    turn_prob = 0.2 + 0.3 * difficulty  # More frequent turns at higher difficulty

    # Initialize start
    spawn_length = m_to_idx(2)
    height_field[:spawn_length, :] = 0
    mid_y = course_width // 2

    # Set initial goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    cur_y = mid_y
    goal_idx = 1

    while cur_x < course_length - m_to_idx(1):
        # Randomly select height for current corridor segment
        segment_height = np.random.uniform(-max_height_variation, max_height_variation)
        segment_length = m_to_idx(np.random.uniform(1.0, 2.0))

        # Ensure the segment fits within the course bounds
        if cur_x + segment_length >= course_length:
            segment_length = course_length - cur_x - 1
        
        # Add the straight corridor segment
        height_field[cur_x:cur_x+segment_length, cur_y-corridor_width//2:cur_y+corridor_width//2] = segment_height

        # Update current x position
        cur_x += segment_length

        # Randomly decide whether to add a turn
        if random.random() < turn_prob and cur_y + corridor_width < course_width and cur_y - corridor_width > 0:
            turn_direction = random.choice([-1, 1])
            turn_length = m_to_idx(np.random.uniform(1.0, 2.0))

            if cur_y + turn_length * turn_direction >= course_width or cur_y + turn_length * turn_direction < 0:
                turn_length = np.abs(course_width - cur_y - corridor_width) if turn_direction == 1 else np.abs(cur_y - corridor_width)

            # Add the turn
            height_field[cur_x:cur_x+turn_length, cur_y-corridor_width//2:cur_y+corridor_width//2] = segment_height
            cur_y += turn_length * turn_direction
            cur_x += turn_length

            goals[goal_idx] = [cur_x - turn_length // 2, cur_y]
            goal_idx += 1

        if goal_idx >= 8:
            break

    if goal_idx < 8:
        goals[goal_idx] = [cur_x, cur_y]

    return height_field, goals