import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """A challenging course with stepped platforms and ramps, emphasizing stability, control, and adaptive traversal."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length_range = (1.0 - 0.3 * difficulty, 1.5 - 0.5 * difficulty)
    platform_width = m_to_idx(np.random.uniform(1.0, 1.6))
    platform_height_range = (0.0 + 0.2 * difficulty, 0.3 + 0.5 * difficulty)
    gap_length_range = (0.2 + 0.5 * difficulty, 0.6 + 0.7 * difficulty)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = m_to_idx((-0.3, 0.3))
    dy_min, dy_max = m_to_idx((-0.4, 0.4))

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at spawn

    # Set remaining area to be a pit to force jumping/climbing
    height_field[spawn_length:, :] = -1.0

    cur_x = spawn_length
    for i in range(7):  # Set up 7 obstacles, varying platforms and ramps
        platform_length = m_to_idx(np.random.uniform(*platform_length_range))
        gap_length = m_to_idx(np.random.uniform(*gap_length_range))
        platform_height = np.random.uniform(*platform_height_range)

        ob_type = np.random.choice(["platform", "ramp_down", "ramp_up"], p=[0.5, 0.25, 0.25])  # Adding variability in obstacle types
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        start_x = cur_x + gap_length
        end_x = start_x + platform_length

        if ob_type == "platform":
            add_platform(start_x, end_x, mid_y + dy, platform_height)
        elif ob_type == "ramp_down":
            height_step = np.linspace(0, platform_height, num=(end_x - start_x))
            height_field[start_x:end_x, (mid_y - platform_width // 2):(mid_y + platform_width // 2)] = height_step[:, None]
        elif ob_type == "ramp_up":
            height_step = np.linspace(platform_height, 0, num=(end_x - start_x))
            height_field[start_x:end_x, (mid_y - platform_width // 2):(mid_y + platform_width // 2)] = height_step[:, None]

        goals[i + 1] = [(start_x + end_x) / 2, mid_y + dy]

        cur_x = end_x

    # Add final goal behind the last obstacle, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals