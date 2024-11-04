import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Varied platforms and narrow bridges for the quadruped to climb and navigate.”

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Parameters for platforms and gaps
    platform_height_min, platform_height_max = 0.15 * difficulty, 0.35 * difficulty
    platform_length_min, platform_length_max = 0.5, 1.2 - 0.5 * difficulty
    platform_width_min, platform_width_max = 0.6 - 0.4 * difficulty, 1.2 - 0.2 * difficulty
    gap_min, gap_max = 0.15, 0.6 * difficulty

    mid_y = m_to_idx(width / 2)

    def add_platform(start_x, end_x, mid_y, height):
        """Adds a platform at the specified indies with specified height."""
        half_width = m_to_idx(np.random.uniform(platform_width_min, platform_width_max)) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_narrow_bridge(start_x, length, mid_y):
        """Creates a narrow bridge of specified length at the specified position."""
        bridge_width = m_to_idx(0.2)
        height_field[start_x:start_x+length, mid_y-bridge_width : mid_y+bridge_width] = 0.05 * difficulty + np.random.uniform(0, 0.05)

    # Set initial flat ground and first goal
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Create obstacle course
    cur_x = spawn_length
    for i in range(1, 8):
        platform_length = m_to_idx(np.random.uniform(platform_length_min, platform_length_max))
        gap_length = m_to_idx(np.random.uniform(gap_min, gap_max))

        # Determine type of obstacle: platform or bridge, based on difficulty
        if difficulty > 0.5 and i % 2 == 0:
            # Add narrow bridge
            bridge_length = platform_length
            add_narrow_bridge(cur_x, bridge_length, mid_y)
            goals[i] = [cur_x + bridge_length // 2, mid_y]
            cur_x += bridge_length + gap_length
        else:
            # Add platform
            platform_height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)
            goals[i] = [cur_x + platform_length // 2, mid_y]
            cur_x += platform_length + gap_length

    # Ensure the last few meters are flat for a safe finish
    final_goal_x = cur_x
    final_length = m_to_idx(2)
    height_field[final_goal_x:final_goal_x+final_length, :] = 0
    goals[-1] = [final_goal_x + final_length // 2, mid_y]

    return height_field, goals