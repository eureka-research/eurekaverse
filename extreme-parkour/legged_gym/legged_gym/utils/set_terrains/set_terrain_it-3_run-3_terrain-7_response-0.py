import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Complex course with alternating narrow beams, variable height platforms, and challenging gaps for advanced navigation and jumping."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Course parameters
    platform_length = m_to_idx(1.2 - 0.2 * difficulty)
    platform_width_variation = [m_to_idx(0.4), m_to_idx(1.2)]
    platform_height_min, platform_height_max = 0.05 * difficulty, 0.3 + 0.3 * difficulty
    gap_length = m_to_idx(0.3 + 0.5 * difficulty)

    mid_y = m_to_idx(width / 2)

    def add_platform(start_x, end_x, mid_y):
        platform_width = np.random.uniform(platform_width_variation[0], platform_width_variation[1])
        half_width = platform_width // 2
        y1, y2 = mid_y - half_width, mid_y + half_width
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[start_x:end_x, y1:y2] = platform_height

    def add_beam(start_x, end_x, mid_y):
        beam_width = m_to_idx(0.4 - 0.2 * difficulty)
        half_width = beam_width // 2
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[start_x:end_x, y1:y2] = np.random.uniform(0.1 * difficulty, 0.4 * difficulty)

    def add_ramp(start_x, end_x, mid_y, direction):
        ramp_width = np.random.uniform(platform_width_variation[0], platform_width_variation[1])
        half_width = ramp_width // 2
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.random.uniform(platform_height_min, platform_height_max)
        slant = np.linspace(0, ramp_height, num=end_x - start_x)[::direction]  # Create gradient
        height_field[start_x:end_x, y1:y2] = slant[:, None]

    dx_min, dx_max = -0.1, 0.2
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(7):
        obstacle_choice = random.choice(['platform', 'beam', 'ramp'])
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max) * ((-1) ** i)  # Alternating y-offset

        if obstacle_choice == 'platform':
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        elif obstacle_choice == 'beam':
            add_beam(cur_x, cur_x + platform_length + dx, mid_y + dy)
            goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        elif obstacle_choice == 'ramp':
            direction = 1 if random.random() > 0.5 else -1  # Randomize ramp direction
            add_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, direction)
            goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        cur_x += platform_length + dx + gap_length

    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals