import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Higher platforms, wider gaps, and lateral transitions to test robot's balance and navigation abilities."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set dimensions and positions for platforms and gaps
    platform_size = 1.0 - 0.3 * difficulty  # Platforms become smaller with difficulty
    platform_size_idx = m_to_idx(platform_size)
    platform_width = np.random.uniform(0.9, 1.2)
    platform_width_idx = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.15 * difficulty, 0.3 * difficulty  # Higher platforms
    gap_length = 0.3 + 0.5 * difficulty  # Wider gaps with difficulty
    gap_length_idx = m_to_idx(gap_length)

    mid_y = m_to_idx(width / 2)

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width_idx // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_beam(start_x, end_x, mid_y):
        beam_width = 0.4  # Narrow beam width
        beam_width_idx = m_to_idx(beam_width)
        half_width = beam_width_idx // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        beam_height = platform_height_max  # Consistent height for review
        height_field[x1:x2, y1:y2] = beam_height
        
    def add_ramp(start_x, end_x, mid_y, direction):
        """Adds a sloped ramp for the robot to ascend or descend."""
        half_width = platform_width_idx // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(platform_height_min, platform_height_max)
        slant = np.linspace(0, ramp_height, num=y2-y1)[::direction]
        slant = slant[None, :]
        height_field[x1:x2, y1:y2] = slant

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = m_to_idx(2)
    
    # First platform to get started
    add_platform(cur_x, cur_x + platform_size_idx, mid_y)
    goals[1] = [cur_x + platform_size_idx // 2, mid_y]
    
    cur_x += platform_size_idx + gap_length_idx

    for i in range(2, 8, 2):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        # Add a beam obstacle
        add_beam(cur_x, cur_x + platform_size_idx + dx, mid_y + dy)
        goals[i] = [cur_x + (platform_size_idx + dx) // 2, mid_y + dy]
        cur_x += platform_size_idx + dx + gap_length_idx
        
        # Add a sideways-facing ramp
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        direction = (-1) ** i
        dy = dy * direction

        add_ramp(cur_x, cur_x + platform_size_idx + dx, mid_y + dy, direction)
        goals[i + 1] = [cur_x + (platform_size_idx + dx) // 2, mid_y + dy]
        cur_x += platform_size_idx + dx + gap_length_idx

    # Final flat area to end the course
    goals[7] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals