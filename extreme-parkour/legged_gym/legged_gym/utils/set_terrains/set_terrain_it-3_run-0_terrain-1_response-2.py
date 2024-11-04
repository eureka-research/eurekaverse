import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Combination of stepping stones and slopes creating varied but realistic terrain for the quadruped to navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]
    
    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    mid_y = m_to_idx(width) // 2

    # Basic course setup
    stepping_stone_size = m_to_idx(0.5)
    slope_length = m_to_idx(1.0)
    gap_length = m_to_idx(0.4 + 0.4 * difficulty)  # Gaps scale with difficulty

    spawn_length = m_to_idx(2)
    max_stepping_stone_height = 0.15 + 0.2 * difficulty
    slope_height = 0.05 + 0.25 * difficulty

    def add_stepping_stone(x, y):
        height = np.random.uniform(0.05, max_stepping_stone_height)
        height_field[x:x + stepping_stone_size, y - stepping_stone_size // 2: y + stepping_stone_size // 2] = height

    def add_slope(x, y, climb=True):
        slope_height = np.linspace(0, slope_height if climb else -slope_height, slope_length * 2)
        height_field[x:x + slope_length, y - stepping_stone_size // 2: y + stepping_stone_size // 2] = slope_height[:, None]

    current_x = spawn_length

    # Start with flat terrain and place initial goal
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    for i in range(3):
        add_stepping_stone(current_x, mid_y)
        goals[i + 1] = [current_x + stepping_stone_size // 2, mid_y]
        current_x += stepping_stone_size + gap_length

    for i in range(2):
        add_slope(current_x, mid_y, climb=bool(i % 2 == 0))  # Alternating climb-up and climb-down slopes
        goals[i + 4] = [current_x + slope_length // 2, mid_y]
        current_x += slope_length + gap_length

    # Add final stretch of stepping stones to reach the final goal
    for i in range(2):
        add_stepping_stone(current_x, mid_y)
        goals[6 + i] = [current_x + stepping_stone_size // 2, mid_y]
        current_x += stepping_stone_size + gap_length

    # Final goal placed at the end
    height_field[current_x:, :] = 0
    goals[-1] = [current_x, mid_y]

    return height_field, goals