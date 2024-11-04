import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Slanted balance beams and narrow pathways testing robot's balance and coordination."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not isinstance(m, (list, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Convert critical points
    length_idx = m_to_idx(length)
    width_idx = m_to_idx(width)
    spawn_length = m_to_idx(2)
    mid_y = width_idx // 2

    # Set the spawn area
    height_field[:spawn_length, :] = 0
    goals[0] = [spawn_length // 2, mid_y]

    # Set up balance beam dimensions
    balance_beam_width = m_to_idx(0.4)
    balance_beam_length = m_to_idx(1.5) + m_to_idx(difficulty)
    beam_height_min, beam_height_max = 0.1, 0.4

    def add_balance_beam(start_x, mid_y, length, width, height):
        half_width = width // 2
        x1, x2 = start_x, start_x + length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    current_x = spawn_length
    for i in range(7):
        beam_height = random.uniform(beam_height_min * (1 + difficulty), beam_height_max * (0.5 + difficulty))
        add_balance_beam(current_x, mid_y, balance_beam_length, balance_beam_width, beam_height)

        # Place goals at the ends of each balance beam
        goals[i+1] = [current_x + balance_beam_length // 2, mid_y]

        # Update current_x to the end of current balance beam and account for small gaps
        current_x += balance_beam_length + m_to_idx(0.1 + 0.2 * difficulty)

    # Final goal at the end of the last beam
    goals[-1] = [current_x - balance_beam_length // 2, mid_y]
    
    return height_field, goals