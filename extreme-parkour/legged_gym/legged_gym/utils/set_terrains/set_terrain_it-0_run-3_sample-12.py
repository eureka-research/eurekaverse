import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Maze-like passage that tests the robot's ability to navigate corners and elevated paths."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up path dimensions based on difficulty
    path_width_min = 0.4  # Narrowest path at hardest difficulty
    path_width_max = 1.0  # Widest path at easiest difficulty
    path_height_min = 0.0  # Flat ground at minimum difficulty
    path_height_max = 0.25  # Elevated paths at hardest difficulty

    path_width = path_width_max - (path_width_max - path_width_min) * difficulty
    path_height_min = 0.0
    path_height_max = path_height_max * difficulty

    mid_y = m_to_idx(width) // 2

    def add_path(start_x, end_x, start_y, width, elevation):
        """Adds a straight elevated path between specified coordinates."""
        half_width = m_to_idx(width / 2)
        x1, x2 = start_x, end_x
        y1, y2 = start_y - half_width, start_y + half_width
        height_field[x1:x2, y1:y2] = elevation

    dx_min, dx_max = 1.0, 2.0  # Path segment length variation in meters
    dy_min, dy_max = -1.0, 1.0  # Path segment horizontal shift variation in meters

    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    cur_y = mid_y

    # Create a maze-like path
    for i in range(7):  # Create 7 segments of the path
        path_length = random.randint(dx_min, dx_max)
        lateral_shift = random.randint(dy_min, dy_max)
        path_elevation = random.uniform(path_height_min, path_height_max)

        add_path(cur_x, cur_x + path_length, cur_y + lateral_shift, path_width, path_elevation)

        # Set goal in the middle of the current path segment
        goals[i + 1] = [cur_x + path_length // 2, cur_y + lateral_shift]

        cur_x += path_length
        cur_y += lateral_shift

    # Ensure the final goal is reachable
    goals[-1] = [cur_x, cur_y]

    if cur_x < m_to_idx(length):
        # Extend the final path segment to fully utilize the terrain length
        add_path(cur_x, m_to_idx(length), cur_y, path_width, path_elevation)

    return height_field, goals