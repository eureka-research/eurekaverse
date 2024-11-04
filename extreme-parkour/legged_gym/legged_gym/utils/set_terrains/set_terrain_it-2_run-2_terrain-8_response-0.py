import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Multiple sideways-facing ramps and balancing beams traversing pits for the robot to climb on and jump across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform, beam, and ramp dimensions
    platform_length = 0.8 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.8, 1.2)
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.05 + 0.2 * difficulty, 0.1 + 0.25 * difficulty
    
    beam_length = 1.2 - 0.4 * difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = 0.4
    beam_width = m_to_idx(beam_width)
    beam_height_min, beam_height_max = 0.05 + 0.2 * difficulty, 0.15 + 0.25 * difficulty

    ramp_height_min, ramp_height_max = 0.2 + 0.5 * difficulty, 0.3 + 0.55 * difficulty

    gap_length = 0.2 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(x, y, z_min, z_max):
        platform_height = np.random.uniform(z_min, z_max)
        height_field[x, y] = platform_height

    def add_beam(start_x, end_x, mid_y):
        half_width = beam_width // 2
        beam_height = np.random.uniform(beam_height_min, beam_height_max)
        height_field[start_x:end_x, mid_y - half_width:mid_y + half_width] = beam_height

    def add_ramp(start_x, end_x, mid_y, direction):
        half_width = platform_width // 2
        ramp_height = np.random.uniform(ramp_height_min, ramp_height_max)
        slant = np.linspace(0, ramp_height, (end_x - start_x))[::direction]
        slant = slant[:, np.newaxis]  # Add a dimension for correct broadcasting
        height_field[start_x:end_x, mid_y - half_width:mid_y + half_width] = slant

    dx_min, dx_max = -0.2, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    for i in range(3):  # Set up 3 platforms
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(np.arange(cur_x, cur_x + platform_length + dx), np.arange(mid_y - platform_width // 2, mid_y + platform_width // 2), platform_height_min, platform_height_max)
        goals[i + 1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

    for i in range(2):  # Set up 2 beams
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_beam(cur_x, cur_x + beam_length + dx, mid_y + dy)
        goals[i + 4] = [cur_x + (beam_length + dx) / 2, mid_y + dy]
        cur_x += beam_length + dx + gap_length

    for i in range(2):  # Set up 2 ramps
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        direction = 1 if i % 2 == 0 else -1  # Alternate direction
        add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, direction)
        goals[i + 6] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals