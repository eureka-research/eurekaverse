import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """A challenging course with a mix of stairs, bridges, and pits to test robot's climbing and balancing skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define various obstacle parameters scaled by difficulty
    platform_height = np.linspace(0.2, 0.5, 8) * difficulty
    step_height_incr = 0.1 * difficulty
    bridge_width = np.linspace(0.4, 0.7, 8) - 0.2 * difficulty
    pit_depth = np.linspace(0.1, 0.3, 8) * difficulty

    mid_y = m_to_idx(width) // 2
    spawn_length = m_to_idx(2)
    
    # Helper functions for generating terrain features
    def add_platform(start_x, width, height):
        half_width = width // 2
        x1, x2 = start_x, start_x + width
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_step(start_x, step_height):
        width = m_to_idx(0.8)
        height_field[start_x:start_x + width, mid_y - width // 2:mid_y + width // 2] = step_height

    def add_bridge(start_x, length, width):
        half_width = width // 2
        height = m_to_idx(0.5)  # Elevated bridge height
        x1, x2 = start_x, start_x + length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_pit(start_x, length, depth):
        x1, x2 = start_x, start_x + length
        y1, y2 = mid_y - m_to_idx(1), mid_y + m_to_idx(1)
        height_field[x1:x2, y1:y2] = -depth

    # Set flat spawn area and the first goal
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]
    
    cur_x = spawn_length
    num_obstacles = 8
    obstacle_types = ['platform', 'step', 'bridge', 'pit']
    for i in range(num_obstacles - 1):
        obstacle = random.choice(obstacle_types)
        if obstacle == 'platform':
            height = platform_height[i]
            width = m_to_idx(np.random.uniform(0.5, 1.0))
            add_platform(cur_x, width, height)
            goals[i + 1] = [cur_x + width / 2, mid_y]
            cur_x += width + m_to_idx(0.1)
        elif obstacle == 'step':
            step_height = platform_height[i]
            step_height = platform_height[i-1] + step_height_incr if i > 0 else step_height
            add_step(cur_x, step_height)
            goals[i + 1] = [cur_x + m_to_idx(0.4), mid_y]
            cur_x += m_to_idx(1.0)
        elif obstacle == 'bridge':
            length = m_to_idx(np.random.uniform(1.0, 1.5))
            width = bridge_width[i]
            add_bridge(cur_x, length, width)
            goals[i + 1] = [cur_x + length / 2, mid_y]
            cur_x += length + m_to_idx(0.1)
        elif obstacle == 'pit':
            length = m_to_idx(1.0)
            depth = pit_depth[i]
            add_pit(cur_x, length, depth)
            goals[i + 1] = [cur_x + length / 2, mid_y]
            cur_x += length + m_to_idx(0.2)

    # Add final goal behind the last obstacle, ensuring the remaining area is flat
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals