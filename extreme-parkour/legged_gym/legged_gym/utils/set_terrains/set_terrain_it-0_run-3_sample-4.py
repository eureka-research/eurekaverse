import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Slalom course with narrow gaps and barriers to test the robot’s steering and flexibility."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up pillar dimensions
    pillar_diameter = 0.4  # Fixed diameter of each pillar
    pillar_diameter_idx = m_to_idx(pillar_diameter)
    gap_width = 0.6 + (1 - difficulty) * 0.8  # Gap width decreases with increased difficulty
    gap_width_idx = m_to_idx(gap_width)

    mid_y = m_to_idx(width) // 2

    def add_pillar(center_x, center_y):
        half_diameter = pillar_diameter_idx // 2
        x1, x2 = center_x - half_diameter, center_x + half_diameter
        y1, y2 = center_y - half_diameter, center_y + half_diameter
        height_field[x1:x2, y1:y2] = np.random.uniform(0.3, 0.5) * difficulty  # Height of the pillars is proportional to the difficulty

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]
    
    cur_x = spawn_length
    goal_idx = 1
    while cur_x < m_to_idx(length) - m_to_idx(2):  # Continue placing pillars and goals till near the end of the terrain
        # Determine center positions for the slalom
        next_pillar_x = cur_x + gap_width_idx
        next_goal_x = cur_x + gap_width_idx // 2

        # Alternate pillar positions on left and right of center line
        if goal_idx % 2 == 0:
            next_pillar_y = mid_y + m_to_idx(1.0)  # Place pillar 1 meter right of center
        else:
            next_pillar_y = mid_y - m_to_idx(1.0)  # Place pillar 1 meter left of center

        add_pillar(next_pillar_x, next_pillar_y)

        # Place goal near the mid of the current gap 
        if goal_idx < 8:
            goals[goal_idx] = [next_goal_x, mid_y]  # Center goals laterally
            goal_idx += 1
        
        cur_x = next_pillar_x + pillar_diameter_idx // 2

    # Ensure the final goal is placed at the end of the terrain
    goals[-1] = [m_to_idx(length) - m_to_idx(0.5), mid_y]

    return height_field, goals