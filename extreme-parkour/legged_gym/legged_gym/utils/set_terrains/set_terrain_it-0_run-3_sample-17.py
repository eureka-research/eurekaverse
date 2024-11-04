import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Stepping stones and narrow walkways over water pits for the robot to navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        if isinstance(m, list) or isinstance(m, tuple):
            return [round(i / field_resolution) for i in m]
        return np.round(m / field_resolution).astype(np.int16)

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define parameters for stepping stones and walkways
    pit_depth = 0.5 + 0.5 * difficulty  # Depth of the water pits
    stone_height = pit_depth + 0.1  # Stones are above the pit
    walkway_width = 0.4 + 0.3 * difficulty

    stone_radius = 0.1 + 0.05 * difficulty
    stone_radius_idx = m_to_idx(stone_radius)
    walkway_width_idx = m_to_idx(walkway_width)

    def add_stone(center_x, center_y):
        """Add a circular stepping stone centered at (center_x, center_y)."""
        for x in range(center_x - stone_radius_idx, center_x + stone_radius_idx):
            for y in range(center_y - stone_radius_idx, center_y + stone_radius_idx):
                if (x - center_x)**2 + (y - center_y)**2 <= stone_radius_idx**2:
                    height_field[x, y] = stone_height

    def add_walkway(start_x, end_x, y_center):
        """Add a narrow walkway along y_center from start_x to end_x."""
        y_start = y_center - walkway_width_idx // 2
        y_end = y_center + walkway_width_idx // 2
        height_field[start_x:end_x, y_start:y_end] = 0

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # Place the first goal at the spawn area
    mid_y = m_to_idx(width) // 2
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Create pits with stepping stones
    x = spawn_length
    for i in range(3):
        pit_length = m_to_idx(2 + difficulty)  # Pits get longer with difficulty
        stone_gap = m_to_idx(0.8 - 0.3 * difficulty)  # Gaps get smaller with difficulty

        # Create the pit
        height_field[x:x + pit_length, :] = -pit_depth

        # Place stepping stones in the pit
        num_stones = 4
        for j in range(num_stones):
            stone_x = x + m_to_idx(j * (pit_length/num_stones) + stone_gap/2)
            stone_y = mid_y + m_to_idx(random.uniform(-1.0, 1.0) * difficulty)
            add_stone(stone_x, stone_y)
        
        # Place a goal on the last stepping stone
        goals[i + 1] = [stone_x, stone_y]

        # Move to the next pit
        x += pit_length

        # Add a narrow walkway after the pit
        walkway_length = m_to_idx(0.5 + 0.5 * difficulty)
        add_walkway(x, x + walkway_length, mid_y)
        
        # Place goal at the end of the walkway
        goals[i + 4] = [x + walkway_length // 2, mid_y]

        # Move further for the next pit
        x += walkway_length

    # Add the final goal beyond the last walkway
    goals[-1] = [x + m_to_idx(1), mid_y]
    height_field[x:, :] = 0

    return height_field, goals