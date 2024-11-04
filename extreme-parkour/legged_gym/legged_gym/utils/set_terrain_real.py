"""
A collection of simple terrains to experiment with.
"""

import numpy as np
import random

def set_terrain(terrain, variation, difficulty):
    terrain_fns = [
        set_terrain_course,
    ]
    idx = int(variation * len(terrain_fns))
    height_field, goals = terrain_fns[idx](terrain.width * terrain.horizontal_scale, terrain.length * terrain.horizontal_scale, terrain.horizontal_scale, difficulty)
    terrain.height_field_raw = (height_field / terrain.vertical_scale).astype(np.int16)
    terrain.goals = goals * terrain.horizontal_scale

    return idx

def set_terrain_course(length, width, field_resolution, difficulty):
    """Flat terrain with no obstacles."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    platform_width, platform_length, platform_height = m_to_idx(0.508), m_to_idx(0.4572), 0.4064
    

    def add_platform(start_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, start_x + platform_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        for delta in range(x2 - x1):
            height_field[x1 + delta, y1:y2] = platform_height    

    goals = np.zeros((8, 2))
    start_x = m_to_idx(3)

    height_field[start_x:start_x+platform_length*4 + m_to_idx(0.6), :] = -1

    for i in range(3):
        add_platform(start_x, m_to_idx(width) // 2  + platform_width // 2)
        add_platform(start_x, m_to_idx(width) // 2  - platform_width // 2)
        start_x += platform_length
    start_x += m_to_idx(0.6)
    add_platform(start_x, m_to_idx(width) // 2  + platform_width // 2)
    add_platform(start_x, m_to_idx(width) // 2  - platform_width // 2)
    start_x += platform_length

    platform_width, platform_length, platform_height = m_to_idx(0.4064), m_to_idx(0.3556), 0.3048
    for i in range(2):
        add_platform(start_x, m_to_idx(width) // 2)
        add_platform(start_x, m_to_idx(width) // 2  + platform_width)
        add_platform(start_x, m_to_idx(width) // 2  - platform_width)
        start_x += platform_length

    start_x += platform_length * 3

    goals[:, 0] = np.linspace(start_x, start_x + m_to_idx(0.5), 8)
    goals[:, 1] = m_to_idx(width) // 2
    # goals[:, 1] += np.random.randint(m_to_idx(-1.0), m_to_idx(1.0), size=(8))
    return height_field, goals
