import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Multiple narrow bridges, stepping stones and asymmetric ramps traversal to test balance, precision, and climbing."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define obstacle dimensions
    bridge_length = 1.2 - 0.4 * difficulty  # Length of each bridge
    bridge_length = m_to_idx(bridge_length)
    bridge_width = np.random.uniform(0.4, 0.6)  # Narrow bridges
    bridge_width = m_to_idx(bridge_width)
    bridge_height_min, bridge_height_max = 0.1, 0.35 * difficulty

    stepping_stone_length = np.random.uniform(0.4, 0.6)  # Stepping stones
    stepping_stone_length = m_to_idx(stepping_stone_length)
    stepping_stone_width = np.random.uniform(0.4, 0.5)
    stepping_stone_width = m_to_idx(stepping_stone_width)
    stepping_stone_height_min, stepping_stone_height_max = 0.1, 0.35 * difficulty

    ramp_length = 1.0  # Ramp length is fixed
    ramp_length = m_to_idx(ramp_length)
    ramp_height_min, ramp_height_max = 0.0 + 0.4 * difficulty, 0.05 + 0.45 * difficulty

    gap_length = 0.2 + 0.5 * difficulty  # Gap lengths
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width / 2)

    def add_bridge(x_start, x_end, y_mid):
        half_width = bridge_width // 2
        y1, y2 = y_mid - half_width, y_mid + half_width
        bridge_height = np.random.uniform(bridge_height_min, bridge_height_max)
        height_field[x_start:x_end, y1:y2] = bridge_height

    def add_stepping_stone(x_start, x_end, y_mid):
        half_width = stepping_stone_width // 2
        y1, y2 = y_mid - half_width, y_mid + half_width
        stepping_stone_height = np.random.uniform(stepping_stone_height_min, stepping_stone_height_max)
        height_field[x_start:x_end, y1:y2] = stepping_stone_height

    def add_ramp(x_start, x_end, y_mid, slant_direction):
        half_width = bridge_width // 2
        y1, y2 = y_mid - half_width, y_mid + half_width
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        slant = np.linspace(0, ramp_height, num=y2-y1)[::slant_direction]
        height_field[x_start:x_end, y1:y2] = slant[np.newaxis, :]  # Add a dimension for broadcasting
    
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at spawn

    obstacle_count = 0
    cur_x = spawn_length

    while obstacle_count < 6:
        obstacle_type = np.random.choice(["bridge", "stepping_stone", "ramp"])

        if obstacle_type == "bridge":
            add_bridge(cur_x, cur_x + bridge_length, mid_y)
            goals[obstacle_count + 1] = [cur_x + bridge_length / 2, mid_y]
            cur_x += bridge_length + gap_length

        elif obstacle_type == "stepping_stone":
            add_stepping_stone(cur_x, cur_x + stepping_stone_length, mid_y)
            goals[obstacle_count + 1] = [cur_x + stepping_stone_length / 2, mid_y]
            cur_x += stepping_stone_length + gap_length

        elif obstacle_type == "ramp":
            slant_direction = np.random.choice([1, -1])
            add_ramp(cur_x, cur_x + ramp_length, mid_y, slant_direction)
            goals[obstacle_count + 1] = [cur_x + ramp_length / 2, mid_y]
            cur_x += ramp_length + gap_length

        obstacle_count += 1

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals