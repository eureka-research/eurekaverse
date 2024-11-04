import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Combination of platforms, ramps, and narrow beams for increased complexity and challenge."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set necessary parameters
    platform_length = 0.8  # Platform length in meters
    platform_height_min, platform_height_max = 0.1 * difficulty, 0.35 * difficulty
    ramp_slope = 0.2 + 0.4 * difficulty  # Ramps become steeper with difficulty
    beam_width = 0.4  # Narrow beams remain consistent in width
    beam_height_min, beam_height_max = 0.1 * difficulty, 0.25 * difficulty

    # Convert parameters to indices
    platform_length_idx = m_to_idx(platform_length)
    ramp_length_idx = m_to_idx(platform_length)  # Assuming ramps have the same horizontal length as platforms
    beam_width_idx = m_to_idx(beam_width)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = m_to_idx(1.0) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_ramp(start_x, end_x, mid_y, upward=True):
        half_width = m_to_idx(1.0) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_delta = ramp_slope * (end_x - start_x)
        if not upward:
            height_delta = -height_delta
        height_field[x1:x2, y1:y2] = np.linspace(0, height_delta, x2-x1)[:, None]

    def add_narrow_beam(start_x, end_x, mid_y):
        half_width = beam_width_idx // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        beam_height = np.random.uniform(beam_height_min, beam_height_max)
        height_field[x1:x2, y1:y2] = beam_height

    # Set spawn area to flat ground
    spawn_length_idx = m_to_idx(2)
    height_field[0:spawn_length_idx, :] = 0
    goals[0] = [spawn_length_idx - m_to_idx(0.5), mid_y]

    cur_x = spawn_length_idx

    # Add a mix of platforms, ramps, and narrow beams
    for i in range(6):
        if i % 3 == 0:
            # Add platform
            add_platform(cur_x, cur_x + platform_length_idx, mid_y)
            cur_x += platform_length_idx
        elif i % 3 == 1:
            # Add ramp (alternating direction)
            add_ramp(cur_x, cur_x + ramp_length_idx, mid_y, upward=(i % 2 == 0))
            cur_x += ramp_length_idx
        else:
            # Add narrow beam
            add_narrow_beam(cur_x, cur_x + platform_length_idx, mid_y)
            cur_x += platform_length_idx
        
        # Put a goal in the middle of the obstacle
        goals[i + 1] = [cur_x - platform_length_idx // 2, mid_y]

        # Add a small gap (scaled with difficulty)
        gap_length = m_to_idx(0.2 + 0.3 * difficulty)
        height_field[cur_x:cur_x + gap_length, :] = 0
        cur_x += gap_length

    # Add final goal
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals