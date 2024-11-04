import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Series of stepping stones and undulating terrains to challenge the robot's balance and agility."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Setup stepping stone and undulating terrain dimensions
    stone_length = 0.6 - 0.2 * difficulty
    stone_length = m_to_idx(stone_length)
    stone_width = 0.6 - 0.2 * difficulty
    stone_width = m_to_idx(stone_width)
    stone_height_min, stone_height_max = 0.05 + 0.15 * difficulty, 0.15 + 0.3 * difficulty
    undulation_amplitude = 0.05 + 0.15 * difficulty
    
    gap_length_min = 0.3 + 0.4 * difficulty
    gap_length_min = m_to_idx(gap_length_min)
    gap_length_max = 0.5 + 0.6 * difficulty
    gap_length_max = m_to_idx(gap_length_max)
    
    mid_y = m_to_idx(width) // 2

    def add_stepping_stone(start_x, mid_y):
        half_length = stone_length // 2
        half_width = stone_width // 2
        x1, x2 = start_x - half_length, start_x + half_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        stone_height = np.random.uniform(stone_height_min, stone_height_max)
        height_field[x1:x2, y1:y2] = stone_height

    def add_undulation(start_x, end_x):
        x1, x2 = start_x, end_x
        y_indices = np.arange(0, m_to_idx(width))
        undulation_heights = undulation_amplitude * np.sin(np.linspace(0, 4 * np.pi, y_indices.size))
        height_field[x1:x2, :] += undulation_heights[np.newaxis, :]
    
    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    
    for i in range(3):  # Set up 3 stepping stones
        cur_x += np.random.randint(gap_length_min, gap_length_max)
        add_stepping_stone(cur_x, mid_y)

        # Put goal in the center of the stepping stone
        goals[i+1] = [cur_x, mid_y]
    
    cur_x += np.random.randint(gap_length_min, gap_length_max)
    segment_length = int(m_to_idx(12) // 3)
    
    for i in range(4, 7):  # Set up undulating terrain between stones
        add_undulation(cur_x, cur_x + segment_length)
        mid_y_shift = (-1)**i * m_to_idx(0.8)  # Alternate shifts to the undulating path
        cur_x = cur_x + segment_length
        goals[i] = [cur_x - segment_length // 2, mid_y + mid_y_shift]

    # Add final flat area
    final_length = m_to_idx(2)
    height_field[cur_x:cur_x + final_length, :] = 0
    # Set final goal
    goals[-1] = [cur_x + final_length - m_to_idx(0.5), mid_y]

    return height_field, goals