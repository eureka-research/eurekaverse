import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Balancing beams with turns and varying widths for the robot to navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up beam dimensions and spacing based on difficulty
    beam_length = 1.0 - 0.3 * difficulty
    beam_length = m_to_idx(beam_length)
    beam_width_min = 0.4 / (1 + difficulty)  # narrower beams with higher difficulty
    beam_width_max = 0.8 / (1 + difficulty)  # upper limit for beam width
    beam_height_min, beam_height_max = 0.1 + 0.1 * difficulty, 0.4 + 0.3 * difficulty
    space_between_beams = 0.5 + difficulty  # space increases with difficulty
    space_between_beams = m_to_idx(space_between_beams)

    def add_beam(start_x, start_y, length, width, height):
        x1, x2 = start_x, start_x + length
        y1, y2 = start_y - width // 2, start_y + width // 2
        height_field[x1:x2, y1:y2] = height

    mid_y = m_to_idx(width) // 2  # center line of the field

    # Set initial flat area for spawning
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0.0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    start_x = spawn_length

    # Create the obstacle course with turns and varying widths
    for i in range(6):  # Create 6 beams with turns
        beam_width = np.random.uniform(beam_width_min, beam_width_max)
        beam_width = m_to_idx(beam_width)
        beam_height = np.random.uniform(beam_height_min, beam_height_max)

        # Add main beam
        add_beam(start_x, mid_y, beam_length, beam_width, beam_height)

        # Place goal at the center of the beam
        goals[i + 1] = [start_x + beam_length // 2, mid_y]

        # Decide on the direction of the turn: left or right
        turn_direction = np.random.choice([-1, 1])
        turn_length = m_to_idx(0.5)
        start_y = mid_y + turn_direction * (beam_width_max // 2 + space_between_beams // 2)
        add_beam(start_x + beam_length, start_y, turn_length, beam_width_min, beam_height)

        # Update the start position for the next beam
        start_x += beam_length + space_between_beams + turn_length
        mid_y = start_y  # Update the mid_y for the next beam

    # Add final goal behind the last beam, fill in the remaining gap
    goals[-1] = [start_x + m_to_idx(0.5), mid_y]
    height_field[start_x:, :] = 0.0

    return height_field, goals