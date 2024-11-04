import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Narrow bridges of varying heights to test balance and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]
    
    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set bridge dimensions
    bridge_length = 1.0 - 0.1 * difficulty  # Bridge length varies slightly with difficulty
    bridge_length = m_to_idx(bridge_length)
    bridge_width = 0.4 + 0.2 * difficulty  # Narrower bridges with increasing difficulty
    bridge_width = m_to_idx(bridge_width)
    bridge_height_min, bridge_height_max = 0.1 + 0.1 * difficulty, 0.4 + 0.4 * difficulty  # Variable heights
    gap_length = 0.2 + 0.5 * difficulty  # Gaps are wider with increasing difficulty
    gap_length = m_to_idx(gap_length)
    
    mid_y = m_to_idx(width) // 2

    def add_bridge(start_x, end_x, mid_y):
        half_width = bridge_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        bridge_height = np.random.uniform(bridge_height_min, bridge_height_max)
        height_field[x1:x2, y1:y2] = bridge_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)

    # Make sure spawn area is flat and set the first goal
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [m_to_idx(1), mid_y]  # Place the first goal in the middle of spawn area

    cur_x = spawn_length
    for i in range(6):  # Build 6 bridges
        dx = np.random.randint(dx_min, dx_max)
        add_bridge(cur_x, cur_x + bridge_length + dx, mid_y)

        # Place goals on or slightly past the center of each bridge
        goals[i+1] = [cur_x + (bridge_length + dx) / 2, mid_y]

        # Add a gap
        cur_x += bridge_length + dx + gap_length
        height_field[cur_x:cur_x + gap_length, :] = -0.2  # Introduce a slight dip for the gap

    # Add the final goal behind the last bridge and fill in the remaining gap to zero
    goals[-1] = [cur_x + gap_length + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals