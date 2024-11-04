import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Maze-like course with walls for the quadruped to navigate, simulating urban obstacles."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Calibration for obstacle height and width based on difficulty
    wall_height_min, wall_height_max = 0.2 * difficulty, 0.4 + 0.5 * difficulty
    wall_width_min, wall_width_max = 0.1, 0.4

    # Define obstacle positions and goals
    obstacles_centers = [
        (2.5, 1),  # (x, y) in meters
        (5, 2.5),
        (7.5, 1),
        (10, 3),
        (9, 0.5)
    ]

    # Place goals approximately at starts of each section, ensuring indices fit the terrain
    goals_in_meters = [
        (1.0, width / 2),  # Spawn goal
        (3.5, 1),  # Near each obstacle
        (6, 2.5),
        (8.5, 1), 
        (10, 3),
        (11, 2.5),  # Final goal to make a turning path
        (11.5, 2.5),  # Continue straight to end
        (11.9, 2.7)  # Close to the end
    ]

    goals = np.array([m_to_idx(g) for g in goals_in_meters])

    def add_wall(center_x, center_y):
        """Adds a wall obstacle centered at (center_x, center_y)"""
        half_width = np.random.uniform(m_to_idx(wall_width_min), m_to_idx(wall_width_max)) // 2
        height = np.random.uniform(wall_height_min, wall_height_max)
        x1, x2 = m_to_idx(center_x) - half_width, m_to_idx(center_x) + half_width
        y1, y2 = m_to_idx(center_y) - half_width, m_to_idx(center_y) + half_width
        height_field[x1:x2, y1:y2] = height

    # Generating walls in defined positions
    for (cx, cy) in obstacles_centers:
        add_wall(cx, cy)

    # Making the spawn area flat
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    return height_field, goals