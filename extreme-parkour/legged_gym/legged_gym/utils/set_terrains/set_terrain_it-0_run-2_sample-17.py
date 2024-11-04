import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Mixed terrain with raised platforms, narrow beams, and a water pit for the quadruped to navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    def add_rectangular_obstacle(start_x, start_y, length, width, height):
        """Adds a rectangular obstacle to the height field."""
        height_field[start_x:start_x + m_to_idx(length),
                     start_y:start_y + m_to_idx(width)] = height

    def add_water_pit(start_x, start_y, length, width):
        """Adds a water pit (negative height) to the height field."""
        height_field[start_x:start_x + m_to_idx(length),
                     start_y:start_y + m_to_idx(width)] = -0.5

    mid_y = m_to_idx(width / 2)

    # Set the starting flat area for the robot to spawn
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at the spawn

    # Set up obstacles based on difficulty
    platform_height = 0.2 + 0.2 * difficulty
    beam_width = 0.4  # Narrower beams
    pit_length = 1.0 + 1.0 * difficulty

    cur_x = spawn_length

    # First obstacle: a raised platform
    add_rectangular_obstacle(cur_x, mid_y - m_to_idx(1.0), 1.5, 2.0, platform_height)
    cur_x += m_to_idx(1.5)
    goals[1] = [cur_x - m_to_idx(0.75), mid_y]

    # Second obstacle: crossing a narrow beam
    cur_x += m_to_idx(0.5)
    add_rectangular_obstacle(cur_x, mid_y - m_to_idx(beam_width / 2), 2.0, beam_width, 0)
    cur_x += m_to_idx(2.0)
    goals[2] = [cur_x - m_to_idx(1.0), mid_y]

    # Third obstacle: another raised platform
    cur_x += m_to_idx(0.5)
    add_rectangular_obstacle(cur_x, mid_y - m_to_idx(1.0), 1.5, 2.0, platform_height)
    cur_x += m_to_idx(1.5)
    goals[3] = [cur_x - m_to_idx(0.75), mid_y]

    # Fourth obstacle: a water pit to jump over
    cur_x += m_to_idx(1.0)
    add_water_pit(cur_x, mid_y - m_to_idx(1.5), 1.0, 3.0)
    cur_x += m_to_idx(1.0)
    goals[4] = [cur_x + m_to_idx(0.5), mid_y]

    # Fifth obstacle: another narrow beam
    cur_x += m_to_idx(0.8)
    add_rectangular_obstacle(cur_x, mid_y - m_to_idx(beam_width / 2), 2.0, beam_width, 0)
    cur_x += m_to_idx(2.0)
    goals[5] = [cur_x - m_to_idx(1.0), mid_y]

    # Sixth obstacle: a larger raised platform
    cur_x += m_to_idx(1.0)
    add_rectangular_obstacle(cur_x, mid_y - m_to_idx(1.5), 2.0, 3.0, platform_height)
    cur_x += m_to_idx(2.0)
    goals[6] = [cur_x - m_to_idx(1.0), mid_y]

    # Final goal: flat ground area after the last platform
    cur_x += m_to_idx(1.0)
    height_field[cur_x:, :] = 0
    goals[7] = [cur_x + m_to_idx(0.5), mid_y]

    return height_field, goals