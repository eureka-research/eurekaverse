import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Narrow pathways with sharp turns and narrow gaps for navigation."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Terrain setup
    def add_narrow_pathway(start_x, start_y, end_x, end_y, width):
        path_height = np.random.uniform(0.1 * difficulty, 0.3 * difficulty)
        idx_start_x, idx_start_y = m_to_idx([start_x, start_y])
        idx_end_x, idx_end_y = m_to_idx([end_x, end_y])
        path_width = m_to_idx(width) // 2
        
        for i in range(idx_start_x, idx_end_x):
            for j in range(idx_start_y - path_width, idx_start_y + path_width):
                height_field[i, j] = path_height

    def add_turn(start_x, start_y, end_x, end_y, turn_type, width):
        path_height = np.random.uniform(0.1 * difficulty, 0.3 * difficulty)
        idx_start_x, idx_start_y = m_to_idx([start_x, start_y])
        idx_end_x, idx_end_y = m_to_idx([end_x, end_y])
        path_width = m_to_idx(width) // 2

        if turn_type == 'left':
            for i in range(idx_start_x, idx_end_x):
                for j in range(idx_start_y - path_width, idx_start_y + path_width):
                    height_field[i, j] = path_height
            for i in range(idx_end_x - path_width, idx_end_x + path_width):
                for j in range(idx_start_y, idx_end_y):
                    height_field[i, j] = path_height
        else:
            for i in range(idx_start_x, idx_end_x):
                for j in range(idx_start_y - path_width, idx_start_y + path_width):
                    height_field[i, j] = path_height
            for i in range(idx_end_x - path_width, idx_end_x + path_width):
                for j in range(idx_end_y, idx_start_y):
                    height_field[i, j] = path_height

    mid_y = m_to_idx(width) // 2

    # Begin the course from the spawning area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [m_to_idx(0.5), mid_y]

    # Narrow pathway specs
    pathway_width = 0.5 + 0.5 * (1 - difficulty)

    # Create pathways and assigns goals
    current_x = 2  # Start after spawn area
    current_y = mid_y * field_resolution  # Middle of the width

    for i in range(4):
        end_x = current_x + 2.5 + 1.5 * difficulty  # Varying length
        add_narrow_pathway(current_x, current_y, end_x, current_y, pathway_width)
        current_x = end_x  # Update to new end position
        goals[i * 2 + 1] = m_to_idx([current_x - 1, current_y])
        
        # Add a turn
        if i % 2 == 0:
            end_y = current_y + 1.5 if i % 4 == 0 else current_y - 1.5
            add_turn(current_x, current_y, current_x, end_y, 'right' if i % 4 == 0 else 'left', pathway_width)
            current_y = end_y  # Update to the turn end position
            goals[i * 2 + 2] = m_to_idx([current_x, current_y])

        else:
            end_y = current_y - 1.5 if i % 4 == 1 else current_y + 1.5
            add_turn(current_x, current_y, current_x, end_y, 'left' if i % 4 == 1 else 'right', pathway_width)
            current_y = end_y  # Update to the turn end position
            goals[i * 2 + 2] = m_to_idx([current_x, current_y])

    # Final goal
    final_x = length - 0.5  # Leave some margin
    goals[-1] = m_to_idx([final_x, current_y])
    height_field[m_to_idx(final_x):, :] = 0

    return height_field, goals