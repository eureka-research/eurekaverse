import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Narrow bridges and small gaps for the robot to navigate for balancing and precise movement."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define bridge and gap dimensions relative to difficulty
    bridge_length_min, bridge_length_max = 1.0, 2.0  # length in meters
    bridge_length_min = m_to_idx(bridge_length_min)
    bridge_length_max = m_to_idx(bridge_length_max)
    
    bridge_width = np.clip(0.5 - 0.3 * difficulty, 0.4, 0.5)  # width in meters
    bridge_width = m_to_idx(bridge_width)
    
    pit_depth = 0.5 + 0.5 * difficulty  # depth in meters
    pit_depth = -pit_depth  # negative because pits go below ground level

    gap_length = 0.2 + 0.8 * difficulty  # gap length in meters
    gap_length = m_to_idx(gap_length)
    mid_y = m_to_idx(width) // 2

    def add_bridge(start_x, end_x, mid_y):
        half_width = bridge_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = 0
    
    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # Put the first goal near the spawn area
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    for i in range(6):  # Set up 6 bridges
        bridge_length = np.random.randint(bridge_length_min, bridge_length_max)
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        # Add the bridge
        add_bridge(cur_x, cur_x + bridge_length, mid_y + dy)

        # Place a goal in the center of the bridge
        goals[i+1] = [cur_x + bridge_length / 2, mid_y + dy]

        # Add a gap after the bridge
        cur_x += bridge_length
        if cur_x + gap_length < height_field.shape[0]:
            height_field[cur_x:cur_x + gap_length, :] = pit_depth
            cur_x += gap_length

    # Add the final goal after the last bridge
    if cur_x < height_field.shape[0]:
        goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
        height_field[cur_x:, :] = 0

    return height_field, goals