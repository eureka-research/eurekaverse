import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Stepping stones and narrow bridges challenge to test the quadruped's balance and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Stepping stone dimensions
    stone_length = 0.4
    stone_width = 0.4
    stone_gap = 0.3 + 0.4 * difficulty
    bridge_length = 1.5
    bridge_width = 0.2 + 0.6 * difficulty

    stone_length_idx = m_to_idx(stone_length)
    stone_width_idx = m_to_idx(stone_width)
    stone_gap_idx = m_to_idx(stone_gap)
    bridge_length_idx = m_to_idx(bridge_length)
    bridge_width_idx = m_to_idx(bridge_width)

    # Center line for placing obstacles
    mid_y = m_to_idx(width) // 2
    
    # Add flat spawn area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [1, mid_y]

    cur_x = spawn_length

    # Add stepping stones and bridges
    def add_stepping_stone(x, y):
        height = np.random.uniform(0.1, 0.4)
        height_field[x:x+stone_length_idx, y:y+stone_width_idx] = height

    def add_bridge(start_x, end_x, y):
        height = np.random.uniform(0.1, 0.4)
        half_width = bridge_width_idx // 2
        height_field[start_x:end_x, y-half_width:y+half_width] = height

    # Sequence: 3 stepping stones, 1 bridge, repeat
    for i in range(4):
        for j in range(3):
            dx = random.randint(-2, 2)
            dy = random.randint(-3, 3)
            add_stepping_stone(cur_x + dx, mid_y + dy)
            goals[i*2 + j] = [cur_x + stone_length_idx//2 + dx, mid_y + dy + stone_width_idx//2]
            cur_x += stone_length_idx + stone_gap_idx
            
        add_bridge(cur_x, cur_x + bridge_length_idx, mid_y)
        goals[i*2 + 3] = [cur_x + bridge_length_idx//2, mid_y]
        cur_x += bridge_length_idx + stone_gap_idx

    # Final goal position
    goals[-1] = [cur_x + 1, mid_y]

    return height_field, goals