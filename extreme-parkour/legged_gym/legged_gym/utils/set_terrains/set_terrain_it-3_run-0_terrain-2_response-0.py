import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Combines varied-height platforms, angled ramps, and small jumps to test balance, climbing, and jumping abilities."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Setup parameters for the platform and gap dimensions
    platform_length_min = 0.8 - 0.2 * difficulty
    platform_length_max = 1.2 - 0.1 * difficulty
    platform_width = np.random.uniform(0.4, 0.6)  # Narrower platforms
    platform_height_min, platform_height_max = 0.1 + 0.3 * difficulty, 0.2 + 0.4 * difficulty
    gap_length_min = 0.3 + 0.3 * difficulty
    gap_length_max = 0.5 + 0.5 * difficulty

    platform_length_min, platform_length_max = m_to_idx([platform_length_min, platform_length_max])
    platform_width = m_to_idx(platform_width)
    gap_length_min, gap_length_max = m_to_idx([gap_length_min, gap_length_max])
    mid_y = m_to_idx(width) // 2
    
    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_ramp(start_x, end_x, mid_y, height, direction):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slant = np.linspace(0, height, num=x2 - x1)[::direction]
        for i in range(y1, y2):
            height_field[x1:x2, i] = slant

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at the spawn point

    cur_x = spawn_length

    for i in range(5):  # We are going to set up 5 platforms and 2 angled ramps
        platform_length = np.random.randint(platform_length_min, platform_length_max)
        platform_height = np.random.uniform(platform_height_min, platform_height_max)

        # Create Platform
        add_platform(cur_x, cur_x + platform_length, mid_y, platform_height)
        goals[i+1] = [cur_x + platform_length // 2, mid_y]

        # Add gap before the next platform
        cur_x += platform_length + np.random.randint(gap_length_min, gap_length_max)

    # Add ramps to increase complexity
    for i in range(5, 7):
        ramp_length = np.random.randint(platform_length_min, platform_length_max)
        ramp_height = np.random.uniform(platform_height_min, platform_height_max)

        # Alternating ramps
        direction = -1 if i % 2 == 0 else 1
        add_ramp(cur_x, cur_x + ramp_length, mid_y, ramp_height, direction)
        goals[i+1] = [cur_x + ramp_length // 2, mid_y]

        cur_x += ramp_length + np.random.randint(gap_length_min, gap_length_max)

    # Final goal just behind the last ramp/platform
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0  # Ensure flat ground after the last obstacle

    return height_field, goals