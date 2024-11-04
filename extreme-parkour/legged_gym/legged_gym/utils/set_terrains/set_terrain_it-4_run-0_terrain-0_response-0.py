import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Alternating raised platforms and narrow beams to test the robot's agility and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and narrow beam dimensions
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    
    # More narrow beams and reduced width platforms
    narrow_beam_length = 1.5 * difficulty
    narrow_beam_length = m_to_idx(narrow_beam_length)

    platform_width = np.random.uniform(0.8, 1.0)
    platform_width = m_to_idx(platform_width)
    narrow_beam_width = 0.2  # Narrower than minimum platform width
    narrow_beam_width = m_to_idx(narrow_beam_width)

    platform_height_min, platform_height_max = 0.1 * difficulty, 0.3 * difficulty
    gap_length = 0.1 + 0.5 * difficulty  # Decrease gap length
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[x1:x2, y1:y2] = platform_height

    def add_narrow_beam(start_x, end_x, mid_y):
        half_width = narrow_beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = 0.2  # Fixed height for narrow beams

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.0, 0.4  # Polarity of dy will alternate instead of being random
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    # Set remaining area to be a pit
    # We do this to force the robot to jump from platform to platform
    height_field[spawn_length:, :] = -1.0

    # Add alternating platforms and narrow beams
    cur_x = spawn_length
    for i in range(3):  # Set up 3 platforms
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)

        # Put goal in the center of the platform
        goals[2*i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += platform_length + dx + gap_length + narrow_beam_length

        add_narrow_beam(cur_x, cur_x + narrow_beam_length + dx, mid_y + dy // 2)
        
        # Put goal in the center of the narrow beam
        goals[2*i+2] = [cur_x + (narrow_beam_length + dx) / 2, mid_y + dy // 2]

        # Add gap
        cur_x += narrow_beam_length + dx + gap_length
    
    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals