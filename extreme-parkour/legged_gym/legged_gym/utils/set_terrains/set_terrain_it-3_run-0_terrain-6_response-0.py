import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Complex obstacle course combining sideways-facing ramps and staggered beams for the quadruped to navigate and balance across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and ramp dimensions
    platform_length = m_to_idx(1.0 - 0.2 * difficulty)
    narrow_beam_length = m_to_idx(0.6)  # Objective: Add narrow beams to increase challenge
    platform_width_min, platform_width_max = 0.8, 1.2
    platform_height_min, platform_height_max = 0.1, 0.2 * difficulty + 0.2
    ramp_height_min, ramp_height_max = 0.2 * difficulty, 0.4 * difficulty + 0.1
    gap_length_min, gap_length_max = 0.2, 0.7 * difficulty
    gap_length_min, gap_length_max = m_to_idx(gap_length_min), m_to_idx(gap_length_max)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, center_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = center_y - half_width, center_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_narrow_beam(start_x, end_x, center_y, height):
        x1, x2 = start_x, end_x
        y1, y2 = center_y - m_to_idx(0.15), center_y + m_to_idx(0.15)  # Narrow beams
        height_field[x1:x2, y1:y2] = height

    def add_ramp(start_x, end_x, center_y, direction):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = center_y - half_width, center_y + half_width
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        slant = np.linspace(0, ramp_height, num=(y2-y1))[::direction]
        height_field[x1:x2, y1:y2] = slant[None, :]

    # Ensuring initial area is flat
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    direction = 1  # Initially left to right

    # Add combination of platforms, ramps, and beams
    for i in range(7):
        gap_length = np.random.randint(gap_length_min, gap_length_max)
        platform_length = m_to_idx(np.random.uniform(0.6, 1.0 - 0.2 * difficulty))
        narrow_beam_length = m_to_idx(np.random.uniform(0.4, 0.6))
        platform_width = np.random.uniform(platform_width_min, platform_width_max)
        platform_width = m_to_idx(platform_width)
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)

        if i % 3 == 0:  # Add ramp every 3rd interval
            add_ramp(cur_x, cur_x + platform_length + gap_length, mid_y, direction)
        elif i % 3 == 1:  # Add narrow beam every alternate interval
            add_narrow_beam(cur_x, cur_x + narrow_beam_length + gap_length, mid_y, platform_height)
        else:
            add_platform(cur_x, cur_x + platform_length + gap_length, mid_y, platform_height)

        goals[i+1] = [cur_x + platform_length / 2, mid_y]  # Set goal at the end of the obstacle
        
        # Switch direction and prepare for next obstacle
        direction *= -1
        cur_x += platform_length + gap_length

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]    # Set final goal after the last obstacle
    height_field[cur_x:, :] = 0

    return height_field, goals