import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Terrain with narrow pathways and pits to test robot's balancing and jumping skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    length_idx = m_to_idx(length)
    width_idx = m_to_idx(width)
    height_field = np.zeros((length_idx, width_idx))
    goals = np.zeros((8, 2))

    # Constants defining pathway and pit design based on difficulty
    min_path_width = 0.4  # Minimum width narrow pathway
    max_path_width = 1.0  # Maximum width narrow pathway
    pit_length_min = 0.2   # Minimum length of pits
    pit_length_max = 1.0   # Maximum length of pits (varies based on difficulty)

    # Create pathways and pits
    cur_x = m_to_idx(2)
    step_count = 0

    # Set up path and goals
    height_field[:cur_x, :] = 0  # Initial flat area
    mid_y = width_idx // 2

    for goal_idx in range(8):
        path_width = min_path_width + (max_path_width - min_path_width) * (1 - difficulty)
        path_width = m_to_idx(path_width)
        half_path_width = path_width // 2

        # Calculate indices for current path
        start_x = cur_x
        end_x = start_x + m_to_idx(1.0)
        
        height_min = 0.0
        height_max = 0.2 + 0.3 * difficulty
        path_height = np.random.uniform(height_min, height_max)
        height_field[start_x:end_x, mid_y - half_path_width:mid_y + half_path_width] = path_height

        # Save the goal at the center of each pathway
        goals[goal_idx] = [start_x + m_to_idx(0.5), mid_y]

        # Calculate indices for the next pit (gap)
        pit_length = pit_length_min + (pit_length_max - pit_length_min) * difficulty
        pit_length = m_to_idx(pit_length)
        
        cur_x = end_x + pit_length
        if cur_x >= length_idx - m_to_idx(1):  # Ensure we stay in bounds
            break

        step_count += 1

    # Fill any remaining area after the last pathway as flat ground (goal area)
    height_field[cur_x:, :] = 0

    # Ensure that we have exactly 8 goals
    if step_count < 7:
        for i in range(step_count+1, 8):
            goals[i] = [cur_x - m_to_idx(0.5), mid_y]

    return height_field, goals