import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Traversal of uneven terrain with varied heights to test balance and maneuverability."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Dimensions for uneven terrain
    terrain_block_length = 1.2
    terrain_block_length_idx = m_to_idx(terrain_block_length)
    terrain_block_width = np.random.uniform(1.0, 1.6)
    terrain_block_width_idx = m_to_idx(terrain_block_width)
    terrain_height_min, terrain_height_max = 0.1 * difficulty, 0.3 + 0.5 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_terrain_block(start_x, end_x, mid_y):
        half_width = terrain_block_width_idx // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        terrain_height = np.random.uniform(terrain_height_min, terrain_height_max)
        height_field[x1:x2, y1:y2] = terrain_height

    # Generate terrain blocks with height variations
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0  # Clear spawn area
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at spawn

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.5, 0.5
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    cur_x = spawn_length
    for i in range(7):  # Create blocks with varied heights
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_terrain_block(cur_x, cur_x + terrain_block_length_idx + dx, mid_y + dy)

        goals[i+1] = [cur_x + (terrain_block_length_idx + dx) / 2, mid_y + dy]

        cur_x += terrain_block_length_idx + dx

    # Final adjustments to ensure goals fit within the course boundaries
    final_goal_x = min(m_to_idx(length) - 1, cur_x + m_to_idx(1))
    goals[-1] = [final_goal_x, mid_y]

    return height_field, goals