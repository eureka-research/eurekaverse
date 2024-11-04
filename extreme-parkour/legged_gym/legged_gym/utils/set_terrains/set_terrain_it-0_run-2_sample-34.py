import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Narrow bridges over pits to test the robot's balance and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Conversion functions and parameters
    width_idx = m_to_idx(width)
    length_idx = m_to_idx(length)

    bridge_length = 2.0  # length of each bridge in meters
    bridge_width = 0.4 + 0.6 * (1 - difficulty)  # bridge width decreases with difficulty
    bridge_height = 0.2  # height of the bridge above the pit
    pit_depth = -0.5  # depth of the pits
    gap_between_bridges = 1.0  # gap between two bridges in meters
    n_bridges = 6  # number of bridges

    bridge_length_idx = m_to_idx(bridge_length)
    bridge_width_idx = m_to_idx(bridge_width)
    gap_between_bridges_idx = m_to_idx(gap_between_bridges)

    mid_y_idx = width_idx // 2  # center line in y direction

    def add_bridge(start_x, end_x, mid_y):
        half_width = bridge_width_idx // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = bridge_height

    cur_x_idx = m_to_idx(2)  # Leave the start area flat
    spawn_end = cur_x_idx
    height_field[0:spawn_end, :] = 0
    # Set first goal at the edge of the spawn area
    goals[0] = [spawn_end - m_to_idx(0.5), mid_y_idx]

    for i in range(n_bridges):
        # Ensure the robot spawns off of the flat area, then enters the first bridge
        add_bridge(cur_x_idx, cur_x_idx + bridge_length_idx, mid_y_idx)
        goals[i + 1] = [cur_x_idx + bridge_length_idx // 2, mid_y_idx]
        cur_x_idx += bridge_length_idx + gap_between_bridges_idx
        height_field[cur_x_idx - gap_between_bridges_idx // 2 : cur_x_idx, :] = pit_depth  # Create the pit
    
    # Ensure the final goal is reachable
    height_field[cur_x_idx:, :] = 0
    goals[-1] = [cur_x_idx + m_to_idx(0.5), mid_y_idx]

    return height_field, goals