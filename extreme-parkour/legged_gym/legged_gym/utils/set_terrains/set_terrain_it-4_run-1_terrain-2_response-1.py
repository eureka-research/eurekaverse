import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Stepped platforms and narrow beams at varying heights and widths for the quadruped to navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform and beam configurations
    platform_length = 0.5  # Shorter platforms
    platform_length = m_to_idx(platform_length)
    platform_width = 0.5  # Shorter width for complexity
    platform_width = m_to_idx(platform_width)
    beam_length = 1.0 - 0.3 * difficulty  # Slightly longer beams
    beam_length = m_to_idx(beam_length)
    beam_width_factor = 1.0 - 0.7 * difficulty  # Adjustable width
    beam_width_min = max(m_to_idx(0.1), m_to_idx(beam_width_factor * 0.28))
    beam_width_max = m_to_idx(0.4)
    gap_length = 0.2 + 0.2 * difficulty  # Adjustable gaps
    gap_length = m_to_idx(gap_length)
    platform_height_min = 0.1
    platform_height_max = 0.3 + 0.3 * difficulty  # Adjustable height ranges

    mid_y = m_to_idx(width) // 2

    def add_platform_beam(start_x, end_x, mid_y, height, use_beam=False):
        half_width = beam_width_max // 2 if use_beam else platform_width // 2
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[start_x:end_x, y1:y2] = height

    dx_min, dx_max = -0.2, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.15, 0.15
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Flat start area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Create obstacles with alternating platforms and beams
    cur_x = spawn_length
    for i in range(6):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        if i % 2 == 0:
            # Platforms
            platform_height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform_beam(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height)
            
            # Place goal in the center of the platform
            goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
            cur_x += platform_length + dx + gap_length
        else:
            # Beams
            beam_width = np.random.randint(beam_width_min, beam_width_max)
            beam_height = np.random.uniform(platform_height_min, platform_height_max)
            
            half_width = beam_width // 2
            add_platform_beam(cur_x, cur_x + beam_length + dx, mid_y + dy, beam_height, use_beam=True)

            # Place goal in the center of the beam
            goals[i+1] = [cur_x + (beam_length + dx) / 2, mid_y + dy]
            cur_x += beam_length + dx + gap_length

    # Final goal placement
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals