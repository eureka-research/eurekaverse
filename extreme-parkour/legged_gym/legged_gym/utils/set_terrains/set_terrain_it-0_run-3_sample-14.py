import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Series of ramps and slopes with varying inclines to test the quadruped's agility and stability."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Ramp and slope dimensions
    ramp_length = m_to_idx(2.0 - 0.5 * difficulty)
    ramp_height_min = 0.1 + 0.5 * difficulty
    ramp_height_max = 0.3 + 1.0 * difficulty

    total_ramps = 6
    spacing = m_to_idx(0.8)

    mid_y = m_to_idx(width / 2)

    def add_ramp(start_x, ramp_height, sign):
        end_x = start_x + ramp_length
        for x in range(start_x, end_x):
            height = ramp_height * (x - start_x) / ramp_length if sign == 1 else ramp_height * (end_x - x) / ramp_length
            height_field[x, :] = height * sign

    def add_slope(start_x, end_x, start_height, end_height):
        for x in range(start_x, end_x):
            height = start_height + (end_height - start_height) * (x - start_x) / (end_x - start_x)
            height_field[x, :] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # Initial goal

    cur_x = spawn_length
    for i in range(total_ramps):
        if i % 2 == 0:
            # Ascending ramp
            ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
            add_ramp(cur_x, ramp_height, 1)
            goals[i+1] = [cur_x + ramp_length // 2, mid_y]
            cur_x += ramp_length
        else:
            # Descending ramp
            ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
            add_ramp(cur_x, ramp_height, -1)
            goals[i+1] = [cur_x + ramp_length // 2, mid_y]
            cur_x += ramp_length
        # Add flat slope as spacing between ramps
        if i < total_ramps - 1:
            add_slope(cur_x, cur_x + spacing, ramp_height if i % 2 == 0 else 0, 0 if i % 2 == 0 else ramp_height)
            cur_x += spacing

    # Final goal at the end
    remaining_length = m_to_idx(length) - cur_x
    goals[-1] = [cur_x + remaining_length // 2, mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals