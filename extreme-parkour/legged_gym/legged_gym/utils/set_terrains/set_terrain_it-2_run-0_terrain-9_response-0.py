import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Series of raising platforms, moving steps, and narrow beams to enhance balance, agility, and coordination."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and obstacle parameters
    platform_length = 0.8 + 0.2 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 0.4 + 0.2 * difficulty
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.1, 0.4 * difficulty
    gap_length = 0.4 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)
    
    moving_step_length = 0.3 + 0.1 * difficulty
    moving_step_length = m_to_idx(moving_step_length)
    moving_step_height = 0.1 + 0.3 * difficulty
    
    beam_length = 1.0 + 0.5 * difficulty
    beam_width = 0.2 + 0.2 * difficulty
    beam_height = 0.15 + 0.25 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, height):
        """Adds a platform with specified start and end x coordinates and height."""
        half_width = platform_width // 2
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[start_x:end_x, y1:y2] = height

    def add_moving_step(start_x, end_x, height, direction):
        """Adds multiple moving steps with alternating heights."""
        step_range = end_x - start_x
        step_positions = np.linspace(0, step_range, num=(step_range // moving_step_length))
        for pos in step_positions.astype(int):
            add_platform(start_x + pos, start_x + pos + moving_step_length, height + direction * moving_step_height)
            direction = -direction

    def add_beam(start_x, end_x):
        """Adds a narrow beam for balance challenge."""
        height = np.random.uniform(beam_height, beam_height + 0.1)
        half_width = beam_width // 2
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[start_x:end_x, y1:y2] = height

    dx_min, dx_max = m_to_idx(-0.1), m_to_idx(0.1)
    dy_min, dy_max = m_to_idx(-0.2), m_to_idx(0.2)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Set first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    # Add various obstacles in the course
    for i in range(2):
        # Alternating platforms
        height = np.random.uniform(platform_height_min, platform_height_max)
        dx = np.random.randint(dx_min, dx_max)
        add_platform(cur_x, cur_x + platform_length + dx, height)
        goals[i+1] = [cur_x + (platform_length + dx) // 2, mid_y]
        cur_x += platform_length + dx + gap_length

    for i in range(2, 4):
        # Adding moving steps
        height = np.random.uniform(platform_height_min, platform_height_max)
        dy = np.random.randint(dy_min, dy_max)
        add_moving_step(cur_x, cur_x + platform_length + dx, height, 1 if i % 2 == 0 else -1)
        goals[i+1] = [cur_x + (platform_length + dx) // 2, mid_y + dy]
        cur_x += platform_length + dx + gap_length

    for i in range(4, 6):
        # Adding narrow beam
        dy = np.random.randint(dy_min, dy_max)
        add_beam(cur_x, cur_x + beam_length)
        goals[i+1] = [cur_x + beam_length // 2, mid_y + dy]
        cur_x += beam_length + gap_length

    # Set remaining area to flat ground
    height_field[cur_x:, :] = 0
    goals[7] = [cur_x + m_to_idx(0.5), mid_y]

    return height_field, goals