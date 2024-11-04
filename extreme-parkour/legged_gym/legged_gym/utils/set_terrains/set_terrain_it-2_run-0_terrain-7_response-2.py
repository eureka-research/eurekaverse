import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Combination of pits, narrow bridges and staggered narrow beams for enhanced navigation and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]
    
    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    
    def add_pit(start_x, end_x):
        """Creates a pit with terrain height of -1.0 meters."""
        height_field[start_x:end_x, :] = -1.0
    
    def add_bridge(start_x, end_x, mid_y):
        """Creates a narrow bridge."""
        bridge_length = end_x - start_x
        bridge_width = max(m_to_idx(0.4) - int(0.3 * difficulty), m_to_idx(0.4))  # Narrower as difficulty increases
        height_field[start_x:end_x, mid_y - bridge_width // 2: mid_y + bridge_width // 2] = np.random.uniform(0.1, 0.3)
    
    def add_staggered_narrow_beam(start_x, end_x, mid_y, direction):
        """Creates a staggered narrow beam, alternating left and right."""
        beam_length = m_to_idx(1.0 - 0.3 * difficulty)
        beam_width = m_to_idx(0.45)
        for i in range(start_x, end_x, beam_length):
            offset_y = m_to_idx(np.random.uniform(0.1, 0.4) * direction)
            y1, y2 = mid_y + offset_y - beam_width // 2, mid_y + offset_y + beam_width // 2
            height_field[i:i + beam_length, y1:y2] = np.random.uniform(0.3, 0.6)
            direction *= -1  # Alternate left and right offsets
    
    spawn_length = m_to_idx(2)
    mid_y = m_to_idx(width) // 2
    cur_x = spawn_length

    # Intial flat ground area
    height_field[:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Start creating pits and bridges
    num_obstacles = min(7, max(4, int(3 + 5 * difficulty)))  # Dynamic obstacle counts according to difficulty
    for i in range(num_obstacles):
        if i % 3 == 0:
            # Add pit
            pit_length = m_to_idx(np.random.uniform(1.0, 1.5))
            add_pit(cur_x, cur_x + pit_length)
            cur_x += pit_length + m_to_idx(0.5)  # Gap after pit
        elif i % 3 == 1:
            # Add bridge
            bridge_length = m_to_idx(np.random.uniform(1.0, 1.5))
            add_bridge(cur_x, cur_x + bridge_length, mid_y)
            goals[i] = [cur_x + bridge_length / 2, mid_y]
            cur_x += bridge_length + m_to_idx(0.5)  # Gap after bridge
        else:
            # Add staggered narrow beams
            beam_length = m_to_idx(np.random.uniform(1.0, 1.5))
            add_staggered_narrow_beam(cur_x, cur_x + beam_length, mid_y, 1)
            goals[i] = [cur_x + beam_length / 2, mid_y]
            cur_x += beam_length + m_to_idx(0.5)  # Gap after beams

    # Set the final goals and fill rest of height_field with flat ground
    goals[7] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0
    
    return height_field, goals