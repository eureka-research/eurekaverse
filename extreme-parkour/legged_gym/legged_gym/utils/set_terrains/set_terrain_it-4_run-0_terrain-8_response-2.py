import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Zig-Zag Pathways with Staggered Blocks for balance and precise movement tests."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up block dimensions
    block_length = 0.6 + 0.2 * difficulty  # Length based on difficulty
    block_length = m_to_idx(block_length)
    block_width = 0.2 + 0.4 * difficulty  # Width based on difficulty
    block_width = m_to_idx(block_width)
    block_height_min, block_height_max = 0.1 * difficulty, 0.3 * difficulty  # Variable height based on difficulty
    pathway_width = m_to_idx(0.6)  # Slightly wider pathway for breathing room

    mid_y = m_to_idx(width) // 2

    def add_block(start_x, end_x, start_y, height):
        height_field[start_x:end_x, start_y:start_y + block_width] = height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_offset = m_to_idx(0.6)  # Zig-zag offset

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(7):  # Set up 7 blocks
        dx = np.random.randint(dx_min, dx_max)
        dy = dy_offset if i % 2 == 0 else -dy_offset  # Alternate sideways direction
        height = np.random.uniform(block_height_min, block_height_max)

        add_block(cur_x, cur_x + block_length + dx, mid_y + dy, height)

        # Put goal in the center of the block
        goals[i + 1] = [cur_x + (block_length + dx) / 2, mid_y + dy + block_width // 2]

        cur_x += block_length + dx + pathway_width
    
    # Final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals