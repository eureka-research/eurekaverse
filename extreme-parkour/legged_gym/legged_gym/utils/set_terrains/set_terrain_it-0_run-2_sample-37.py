import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Elevated pathways and balancing beams for the robot to navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up pathway and beam dimensions
    pathway_length = 1.5 - 0.5 * difficulty  # Length decreases with difficulty
    pathway_length = m_to_idx(pathway_length)
    pathway_width = np.random.uniform(0.4, 0.7)  # Random width for variability
    pathway_width = m_to_idx(pathway_width)
    
    pathway_height_min, pathway_height_max = 0.3 + 0.2 * difficulty, 0.5 + 0.3 * difficulty
    intermediate_gap_min, intermediate_gap_max = 0.1, 0.5 * difficulty
    intermediate_gap_min = m_to_idx(intermediate_gap_min)
    intermediate_gap_max = m_to_idx(intermediate_gap_max)
    
    mid_y = m_to_idx(width) // 2

    def add_narrow_pathway(start_x, end_x, mid_y):
        half_width = pathway_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        pathway_height = np.random.uniform(pathway_height_min, pathway_height_max)
        height_field[x1:x2, y1:y2] = pathway_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_range = m_to_idx(0.5)  # Allow only small deviations to keep paths aligned

    starting_x = m_to_idx(2)
    current_x = starting_x

    # Set spawn area to flat ground and initial goal
    height_field[0:starting_x, :] = 0
    goals[0] = [starting_x - m_to_idx(0.5), mid_y]  

    for i in range(6):  # Create 6 elevated pathways
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(-dy_range, dy_range)
        add_narrow_pathway(current_x, current_x + pathway_length + dx, mid_y + dy)
        
        # Place goal in the middle of the current pathway
        goals[i+1] = [current_x + (pathway_length + dx) / 2, mid_y + dy]
        
        # Add intermediate gap
        intermediate_gap = np.random.randint(intermediate_gap_min, intermediate_gap_max)
        current_x += pathway_length + dx + intermediate_gap
    
    # Set the final goal and flatten the remaining terrain if necessary
    goals[-1] = [current_x + m_to_idx(0.5), mid_y]
    height_field[current_x:, :] = 0

    return height_field, goals