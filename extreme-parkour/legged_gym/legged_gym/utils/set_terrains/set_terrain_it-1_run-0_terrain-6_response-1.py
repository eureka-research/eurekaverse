import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Advanced obstacle course with narrow pathways, varied-height platforms, and stairs to challenge the quadruped's agility and balance."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Dimensions and spacing calculations based on difficulty
    pathway_width = np.random.uniform(0.4, 0.55) - 0.1 * difficulty  # Narrow pathways
    pathway_width = m_to_idx(pathway_width)
    platform_length = 1.0 - 0.2 * difficulty  # Length of platforms
    platform_length = m_to_idx(platform_length)
    platform_height_min, platform_height_max = 0.1, 0.4 * difficulty  # Platform height variation
    stair_steps = int(4 + 4 * difficulty)  # Increase number of steps based on difficulty
    stair_height = 0.05 + 0.3 * difficulty  # Step height
    stair_height = m_to_idx(stair_height)
    stair_length = 0.2 + 0.3 * difficulty
    stair_length = m_to_idx(stair_length)

    mid_y = m_to_idx(width / 2)

    def add_platform(start_x, end_x, mid_y):
        half_width = pathway_width // 2
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[start_x:end_x, mid_y - half_width:mid_y + half_width] = platform_height

    def add_staircase(start_x, steps, height, length, mid_y):
        for step in range(steps):
            x1 = start_x + step * length
            x2 = x1 + length
            y1, y2 = mid_y - pathway_width // 2, mid_y + pathway_width // 2
            height_value = height * (steps - step - 1)
            height_field[x1:x2, y1:y2] = height_value

    # Safe, flat starting area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # First goal in the center of the flat starting area
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    current_x = spawn_length
    sections = ['platform', 'narrow_pathway', 'staircase']  # Rotate challenge types

    for i in range(6):
        section_type = sections[i % len(sections)]

        if section_type == 'platform':
            add_platform(current_x, current_x + platform_length, mid_y)
            goals[i + 1] = [current_x + platform_length // 2, mid_y]

        elif section_type == 'narrow_pathway':
            width = pathway_width
            path_length = platform_length
            path_height = np.random.uniform(platform_height_min, platform_height_max) * difficulty
            height_field[current_x:current_x + path_length, mid_y - width//2:mid_y + width//2] = path_height
            goals[i + 1] = [current_x + path_length // 2, mid_y]

        elif section_type == 'staircase':
            add_staircase(current_x, stair_steps, stair_height, stair_length, mid_y)
            goals[i + 1] = [current_x + stair_steps * stair_length // 2, mid_y]

        current_x += platform_length + m_to_idx(0.1 + 0.5 * difficulty)  # Add some gap

    # Final goal marking the end of the course
    goals[-1] = [current_x + m_to_idx(0.5), mid_y]
    height_field[current_x:, :] = 0  # Flat ground at the end

    return height_field, goals