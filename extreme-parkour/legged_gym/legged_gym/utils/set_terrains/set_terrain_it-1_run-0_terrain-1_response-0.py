import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """An urban-inspired terrain with stairs, ramps, and narrow beams to test the quadruped's traversal skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    mid_y = m_to_idx(width) // 2

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # Goals are strategically placed: (initially at spawn area)
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # 1. Stairs
    stair_height_min, stair_height_max = 0.05, 0.2
    stair_depth = m_to_idx(0.3)
    num_stairs = int(3 + 5 * difficulty)
    cur_x = spawn_length
    for i in range(num_stairs):
        stair_height = np.random.uniform(stair_height_min, stair_height_max)
        height_field[cur_x:cur_x+stair_depth, :] = stair_height * (i + 1)
        cur_x += stair_depth

    goals[1] = [cur_x - stair_depth / 2, mid_y] # Goal at the top of the stairs

    # 2. Ramp up
    ramp_length = m_to_idx(1.5 + 1.5 * difficulty)
    ramp_height = np.random.uniform(0.5, 0.8)
    for i in range(ramp_length):
        height_field[cur_x + i, :] = ramp_height * (i / ramp_length)
    cur_x += ramp_length

    goals[2] = [cur_x - m_to_idx(0.5), mid_y] # Goal at the top of the ramp

    # 3. Narrow beam
    beam_width = m_to_idx(np.random.uniform(0.4, 0.6 - 0.3 * difficulty))
    beam_length = m_to_idx(2 + 2 * difficulty)
    y_start = mid_y - beam_width // 2
    height_field[cur_x:cur_x+beam_length, y_start:y_start+beam_width] = ramp_height
    cur_x += beam_length

    goals[3] = [cur_x - m_to_idx(0.5), mid_y] # Goal on the beam

    # 4. Deep pit to jump across
    pit_length = m_to_idx(1 + 1 * difficulty)
    height_field[cur_x:cur_x+pit_length, :] = -0.5
    cur_x += pit_length

    goals[4] = [cur_x - m_to_idx(0.5), mid_y] # Goal after the pit

    # 5. Ramp down
    ramp_down_length = m_to_idx(1.5 + 1.5 * difficulty)
    for i in range(ramp_down_length):
        height_field[cur_x + i, :] = ramp_height * (1 - i / ramp_down_length)
    cur_x += ramp_down_length

    goals[5] = [cur_x - m_to_idx(0.5), mid_y] # Goal at the bottom of the ramp

    # 6. Another set of stairs down
    for i in range(num_stairs):
        stair_height = np.random.uniform(stair_height_min, stair_height_max)
        height_field[cur_x:cur_x+stair_depth, :] = -stair_height * (i + 1)
        cur_x += stair_depth

    goals[6] = [cur_x - stair_depth / 2, mid_y] # Goal at the bottom of the stairs

    # Final flat goal area
    height_field[cur_x:, :] = 0
    goals[7] = [cur_x + m_to_idx(2), mid_y] # Final goal

    return height_field, goals