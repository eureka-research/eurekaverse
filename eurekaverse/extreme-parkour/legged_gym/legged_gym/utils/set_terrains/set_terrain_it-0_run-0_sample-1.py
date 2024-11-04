import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Narrow bridges and sharp turns for the robot to navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Basic obstacle sizes and properties
    bridge_width = max(0.4, 0.8 * (1 - difficulty))  # Bridge width decreases with difficulty
    bridge_width = m_to_idx(bridge_width)
    bridge_length_min = 2.0
    bridge_length_max = 3.0
    bridge_length_min = m_to_idx(bridge_length_min)
    bridge_length_max = m_to_idx(bridge_length_max)
    bridge_height = 0.05 + 0.25 * difficulty  # Increase height with difficulty
    pit_depth = -1.0  # Depth of the pit around bridges
  
    spawn_x_idx = m_to_idx(2)
    height_field[0:spawn_x_idx, :] = 0  # Spawn area flat ground
    mid_y_idx = m_to_idx(width / 2)

    # Set the initial goal at spawn area
    goals[0] = [spawn_x_idx - m_to_idx(0.5), mid_y_idx]

    def add_bridge(start_x_idx, start_y_idx, length):
        half_width = bridge_width // 2
        x1, x2 = start_x_idx, start_x_idx + length
        y1, y2 = start_y_idx - half_width, start_y_idx + half_width
        height_field[x1:x2, y1:y2] = bridge_height

    cur_x = spawn_x_idx

    for i in range(7):  # Set up 7 bridges
        bridge_length = np.random.randint(bridge_length_min, bridge_length_max)
        offset_y = np.random.uniform(-1.0, 1.0)
        offset_y = m_to_idx(offset_y)
        
        add_bridge(cur_x, mid_y_idx + offset_y, bridge_length)
        goals[i+1] = [cur_x + bridge_length // 2, mid_y_idx + offset_y]  # Goal in the center of the bridge

        # Add space (pit) before the next bridge
        pit_length = np.random.uniform(0.4, 0.6)
        pit_length = m_to_idx(pit_length)
        cur_x += bridge_length + pit_length

    # Fill in the remaining area after the last bridge with flat ground
    height_field[cur_x:, :] = 0
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y_idx]  # Final goal just after last bridge

    return height_field, goals