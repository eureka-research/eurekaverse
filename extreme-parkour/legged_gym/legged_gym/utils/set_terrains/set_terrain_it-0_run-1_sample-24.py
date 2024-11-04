import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Slalom course with turnable narrow bridges for balance testing."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Dimensions and properties of the course based on difficulty
    bridge_length = 2.0 - difficulty  # 2.0 meters at lower difficulty, reduced by 1 meter at max difficulty
    bridge_width = 0.4  # Narrow bridge (minimum requirement)
    bridge_height = 0.2 + difficulty * 0.5  # 0.2 meters at minimum difficulty increasing to 0.7 meters
    gap_length = 0.5 + difficulty * 1.0  # Gap from 0.5 meters to 1.5 meters at hardest
    
    bridge_length_idx = m_to_idx(bridge_length)
    bridge_width_idx = m_to_idx(bridge_width)
    bridge_height_min, bridge_height_max = bridge_height * 0.8, bridge_height * 1.2
    gap_length_idx = m_to_idx(gap_length)
    mid_y = m_to_idx(width / 2)

    start_x_idx = 2 / field_resolution
    cur_x = start_x_idx

    def add_bridge(start_x, mid_y, orientation='horizontal'):
        """Add a bridge obstacle at the specified location with a given orientation."""
        length = bridge_length_idx if orientation == 'horizontal' else bridge_width_idx
        width = bridge_width_idx if orientation == 'horizontal' else bridge_length_idx

        half_width = width // 2
        x1, x2 = start_x, start_x + length
        y1, y2 = mid_y - half_width, mid_y + half_width

        bridge_height = random.uniform(bridge_height_min, bridge_height_max)
        height_field[x1:x2, y1:y2] = bridge_height

        return (x1 + x2) / 2, (y1 + y2) / 2

    # Place starting flat ground area
    height_field[:start_x_idx, :] = 0
    
    # Configure goals and place bridges with gaps
    x_offset = cur_x
    for i in range(4):
        orientation = 'horizontal' if i % 2 == 0 else 'vertical'
        goal_x, goal_y = add_bridge(x_offset, mid_y if orientation == 'horizontal' else mid_y + (-1)**i * m_to_idx(0.5), orientation=orientation)
        goals[2 * i] = [goal_x, goal_y]

        # Add a gap after the bridge
        x_offset += m_to_idx(bridge_length) if orientation == 'horizontal' else gap_length_idx
        y_offset = goal_y + gap_length_idx if orientation == 'vertical' else goal_y
        goals[2 * i + 1] = [goal_x + gap_length_idx, y_offset] if orientation == 'horizontal' else [goal_x, y_offset]

    return height_field, goals