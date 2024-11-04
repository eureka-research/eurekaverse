import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Ramps and narrow beams for the robot to balance on and navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define ramp parameters
    ramp_length = 1.5 - 0.5 * difficulty  # Ramp length decreases with difficulty
    ramp_length_idx = m_to_idx(ramp_length)
    ramp_height = 0.3 + 0.2 * difficulty  # Ramp height increases with difficulty
    beam_width = 0.4  # Fixed narrow beam width
    beam_width_idx = m_to_idx(beam_width)
    mid_y = m_to_idx(width) // 2

    def add_ramp(start_x, length, height, mid_y):
        """Add a ramp by tilting the height gradually."""
        for x in range(m_to_idx(start_x), m_to_idx(start_x + length)):
            progress = (x - m_to_idx(start_x)) / m_to_idx(length)
            platform_height = progress * height
            height_field[x, mid_y] = platform_height

    def add_beam(start_x, length, mid_y):
        """Add a narrow beam."""
        half_width = beam_width_idx // 2
        y1, y2 = mid_y - half_width, mid_y + half_width
        for x in range(m_to_idx(start_x), m_to_idx(start_x + length)):
            height_field[x, y1:y2] = ramp_height  # Beam height equals final ramp height

    # Set initial flat ground for the spawning area
    spawn_length = m_to_idx(2)
    height_field[:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Add 4 ramps and 4 beams in an alternating pattern
    cur_x = spawn_length
    for i in range(4):
        # Add a ramp
        ramp_start = cur_x
        add_ramp(ramp_start, ramp_length, ramp_height, mid_y)

        # Place the goal at the end of the ramp
        goals[i * 2 + 1] = [ramp_start + ramp_length_idx / 2, mid_y]

        # Move the x position forward past the ramp
        cur_x += ramp_length_idx

        # Adding a gap between ramp and beam
        gap_length = 0.2 + 0.3 * difficulty
        cur_x += m_to_idx(gap_length)

        # Add a beam after the ramp
        beam_start = cur_x
        add_beam(beam_start, ramp_length, mid_y)

        # Place the goal in the middle of the beam
        goals[i * 2 + 2] = [beam_start + ramp_length_idx / 2, mid_y]

        # Move the x position forward past the beam
        cur_x += ramp_length_idx

    # Set the final goal at the end of the last beam
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    
    return height_field, goals