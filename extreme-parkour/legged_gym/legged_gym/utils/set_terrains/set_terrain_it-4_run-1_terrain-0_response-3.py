import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Combination of tall platforms, narrow beams, and gaps for the robot to navigate, jump, and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform specifications
    platform_width = max(1.0, 1.5 * (1 - difficulty))
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.2 * difficulty, 0.5 * difficulty

    # Beam specifications
    beam_width = 0.4 + (0.4 * (1 - difficulty))
    beam_width = m_to_idx(beam_width)
    beam_height = 0.3 + (0.7 * difficulty)

    # Gap specifications
    gap_length = 0.2 + 0.8 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, y_center, height):
        half_width = platform_width // 2
        y_start = max(0, y_center - half_width)
        y_end = min(m_to_idx(width), y_center + half_width)
        height_field[start_x:end_x, y_start:y_end] = height

    def add_beam(start_x, end_x, y_center, height):
        half_width = beam_width // 2
        y_start = max(0, y_center - half_width)
        y_end = min(m_to_idx(width), y_center + half_width)
        height_field[start_x:end_x, y_start:y_end] = height

    # Initialize terrain with flat ground for the spawning area
    spawn_length = m_to_idx(2.0)
    height_field[:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    current_x = spawn_length
    current_height = platform_height_min

    # Add platforms, beams, and gaps
    for i in range(3):
        # Add platform
        platform_length = m_to_idx(1.0)
        add_platform(current_x, current_x + platform_length, mid_y, current_height)
        goals[i*2 + 1] = [current_x + platform_length / 2, mid_y]

        # Move to next section (gap)
        current_x += platform_length + gap_length

        # Add beam
        beam_length = m_to_idx(1.5)
        add_beam(current_x, current_x + beam_length, mid_y, beam_height)
        goals[i*2 + 2] = [current_x + beam_length / 2, mid_y]

        # Move to next section (gap)
        current_x += beam_length + gap_length

        # Increase the height for the next platform
        current_height = min(current_height + (platform_height_max - platform_height_min) / 3, platform_height_max)

    # Add the final goal on flat ground at the end of the course
    final_goal_x = min(m_to_idx(length) - 1, current_x)
    goals[7] = [final_goal_x, mid_y]

    # Ensure the terrain is flat after the last obstacle, if there is remaining space
    if final_goal_x < m_to_idx(length):
        height_field[final_goal_x:, :] = 0

    return height_field, goals