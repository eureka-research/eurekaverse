"""
A simple flat terrain.
"""

import numpy as np
import random

def set_terrain(terrain, variation, difficulty):
    terrain_fns = [
        set_terrain_flat,
    ]
    idx = int(variation * len(terrain_fns))
    height_field, goals = terrain_fns[idx](terrain.width * terrain.horizontal_scale, terrain.length * terrain.horizontal_scale, terrain.horizontal_scale, difficulty)
    terrain.height_field_raw = (height_field / terrain.vertical_scale).astype(np.int16)
    terrain.goals = goals * terrain.horizontal_scale

    if terrain_fns[idx] == set_terrain_flat:
        return -1
    return idx

def set_terrain_flat(length, width, field_resolution, difficulty):
    """Flat terrain with no obstacles."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    goals[:, 0] = np.linspace(m_to_idx(2), m_to_idx(length - 2), 8)
    goals[:, 1] = m_to_idx(width) // 2
    goals[:, 1] += np.random.randint(m_to_idx(-1.0), m_to_idx(1.0), size=(8))
    return height_field, goals