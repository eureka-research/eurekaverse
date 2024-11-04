import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Series of sequential hurdles for the robot to jump over, testing its jumping capabilities."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up hurdle dimensions based on difficulty
    hurdle_height_min = 0.1 + 0.2 * difficulty  # Minimum height of hurdles from 0.1 to 0.3 meters
    hurdle_height_max = 0.3 + 0.4 * difficulty  # Maximum height of hurdles from 0.3 to 0.7 meters
    hurdle_width = 1.0                          # Constant width for hurdles to ensure stability
    hurdle_width_idx = m_to_idx(hurdle_width)
    hurdle_spacing = 1.5 + 1.5 * difficulty     # Increase spacing between hurdles with difficulty
    hurdle_spacing_idx = m_to_idx(hurdle_spacing)
    
    mid_y = m_to_idx(width / 2)  # Midpoint along the width of the terrain

    def add_hurdle(start_x, mid_y):
        """Adds a hurdle to the height_field at the given position."""
        half_width = hurdle_width_idx // 2
        x1, x2 = start_x, start_x + m_to_idx(0.2)  # Hurdle spans 0.2 meters in the x-direction
        y1, y2 = mid_y - half_width, mid_y + half_width
        hurdle_height = np.random.uniform(hurdle_height_min, hurdle_height_max)
        height_field[x1:x2, y1:y2] = hurdle_height

    # Spawn area
    spawn_length = m_to_idx(2)
    height_field[:spawn_length, :] = 0
    goals[0] = [1, mid_y]

    current_x = spawn_length
    for i in range(1, 8):
        add_hurdle(current_x, mid_y)
        goals[i] = [current_x + m_to_idx(0.1), mid_y]  # Place goal just beyond the hurdle
        current_x += hurdle_spacing_idx
    
    # Ensure last bit of terrain is flat
    height_field[current_x:, :] = 0

    return height_field, goals