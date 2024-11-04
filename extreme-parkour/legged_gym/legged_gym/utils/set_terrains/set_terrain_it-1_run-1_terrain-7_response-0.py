import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Series of elevated platforms with sloped ramps and narrow bridges to test precise navigation and climbing."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and ramp dimensions
    platform_length = 1.2 - 0.4 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = 0.8 - 0.2 * difficulty
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.2 * difficulty, 0.5 * difficulty
    ramp_height = platform_height_max
    gap_length = 0.2 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)
    bridge_length = 1.0
    bridge_length = m_to_idx(bridge_length)
    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, y_center):
        half_width = platform_width // 2
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[start_x:end_x, y_center-half_width:y_center+half_width] = platform_height

    def add_ramp(start_x, end_x, y_center, direction):
        half_width = platform_width // 2
        ramp_slope = np.linspace(0, ramp_height, end_x - start_x)[::direction]
        for i in range(y_center-half_width, y_center+half_width):
            height_field[start_x:end_x, i] = ramp_slope

    def add_bridge(start_x, end_x, y_center, width):
        half_width = width // 2
        height_field[start_x:end_x, y_center-half_width:y_center+half_width] = np.random.uniform(platform_height_min, platform_height_max)

    dx_min, dx_max = -0.2, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = 0.0, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    # Add first platform
    dx = np.random.randint(dx_min, dx_max)
    dy = np.random.randint(dy_min, dy_max)
    add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
    goals[1] = [cur_x + (platform_length + dx) // 2, mid_y + dy]
    cur_x += platform_length + dx + gap_length

    # Add series of platforms with ramps and bridges
    for i in range(2, 5):
        # Decide whether to add a bridge or ramp based on difficulty
        feature_choice = np.random.choice(['ramp', 'bridge'])
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        direction = (-1)**i

        if feature_choice == 'ramp':
            add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, direction)
            goals[i] = [cur_x + (platform_length + dx) // 2, mid_y + dy]
        else:
            bridge_width = platform_width // 1.5
            add_bridge(cur_x, cur_x + bridge_length, mid_y + dy, bridge_width)
            goals[i] = [cur_x + bridge_length // 2, mid_y + dy]
            cur_x += bridge_length

        cur_x += platform_length + dx + gap_length if feature_choice == 'ramp' else 0

    # Add final platform with a slightly easier setup
    add_platform(cur_x, cur_x + platform_length, mid_y)
    goals[5] = [cur_x + platform_length // 2, mid_y]
    cur_x += platform_length

    # Ensure the last goal is placed at the end of the course
    goals[6] = [cur_x + m_to_idx(0.5), mid_y]
    goals[7] = [m_to_idx(length) - m_to_idx(1), mid_y]

    # Final stretch is flat ground
    height_field[cur_x:, :] = 0

    return height_field, goals