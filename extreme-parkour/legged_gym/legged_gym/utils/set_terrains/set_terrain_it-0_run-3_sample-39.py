import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Staggered stepping stones and narrow beams across a canyon for the robot to navigate and balance on."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define the dimensions of stepping stones and narrow beams
    stone_length = 0.4
    stone_width = 0.4
    stone_length = m_to_idx(stone_length)
    stone_width = m_to_idx(stone_width)
    beam_length_min = 1.0 - 0.2 * difficulty
    beam_length_max = 1.5 - 0.5 * difficulty
    beam_width = 0.4
    beam_length_min = m_to_idx(beam_length_min)
    beam_length_max = m_to_idx(beam_length_max)
    beam_width = m_to_idx(beam_width)
    stone_height_min, stone_height_max = 0.1 + 0.1 * difficulty, 0.15 + 0.3 * difficulty

    canyon_width = m_to_idx(2)
    mid_y = m_to_idx(width) // 2

    def add_stepping_stone(x, y):
        x1, x2 = x, x + stone_length
        y1, y2 = y, y + stone_width
        stone_height = np.random.uniform(stone_height_min, stone_height_max)
        height_field[x1:x2, y1:y2] = stone_height

    def add_narrow_beam(start_x, end_x, y_center):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = y_center - half_width, y_center + half_width
        height_field[x1:x2, y1:y2] = 0.15

    # Set the start area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Create a canyon by lowering terrain
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    for i in range(3):  # Set up 3 stepping stones and 3 narrow beams
        # Stepping stone
        dy = np.random.uniform(-canyon_width / 2, canyon_width / 2)
        add_stepping_stone(cur_x, mid_y + dy)

        # Goal in the center of the stepping stone
        goals[2*i + 1] = [cur_x + stone_length / 2, mid_y + dy]

        # Add gap before beam
        cur_x += stone_length + m_to_idx(0.2)

        # Narrow beam
        beam_length = np.random.randint(beam_length_min, beam_length_max)
        dy = np.random.uniform(-canyon_width / 3, canyon_width / 3)
        add_narrow_beam(cur_x, cur_x + beam_length, mid_y + dy)

        # Goal in the center of the beam
        goals[2*i + 2] = [cur_x + beam_length / 2, mid_y + dy]

        # Add gap after beam
        cur_x += beam_length + m_to_idx(0.2)

    # Add final goal at the end of the terrain
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals