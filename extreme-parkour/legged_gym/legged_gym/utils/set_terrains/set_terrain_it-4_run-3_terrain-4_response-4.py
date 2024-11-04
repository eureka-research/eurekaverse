import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """A series of inclined and varied platforms for the quadruped to navigate and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up platform and obstacle dimensions
    platform_length_base = 0.8 + 0.2 * difficulty
    platform_length_variation = 0.3 * difficulty
    platform_width_min, platform_width_max = 0.4, 0.8  # Narrower for more difficulty
    platform_height_min, platform_height_max = 0.1, 0.4 * difficulty
    gap_length_base = 0.2
    gap_length_variation = 0.5 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_platform_or_ramp(start_x, end_x, y_mid, height, is_ramp=False, direction=1):
        half_width = m_to_idx(np.random.uniform(platform_width_min, platform_width_max) / 2)
        x1, x2 = start_x, end_x
        y1, y2 = y_mid - half_width, y_mid + half_width
        
        if is_ramp:
            incline = np.linspace(0, height * direction, x2 - x1)[:, None]
            height_field[x1:x2, y1:y2] = incline + height_field[x1, y1:y1+1]
        else:
            height_field[x1:x2, y1:y2] = height

    def add_goal(start_x, end_x, y_mid):
        goals.append([(start_x + end_x) / 2, y_mid])

    dx_min, dx_max = -0.2, 0.2
    dy_variation = 0.4  # Max shift along y-axis

    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_variation = m_to_idx(dy_variation)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Initial platform after spawn flat area
    cur_x = spawn_length
    for i in range(6):  # Create a variety of platforms and ramps
        platform_length = m_to_idx(platform_length_base + platform_length_variation * np.random.random())
        gap_length = m_to_idx(gap_length_base + gap_length_variation * np.random.random())

        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(-dy_variation, dy_variation)
        
        is_ramp = (i % 2 == 0)  # every alternate platform is a ramp
        height = np.random.uniform(platform_height_min, platform_height_max)
        direction = (-1) ** i  # alternate inclination direction for ramp
        
        add_platform_or_ramp(cur_x, cur_x + platform_length + dx, mid_y + dy, height, is_ramp, direction)
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        cur_x += platform_length + dx + gap_length

    # Final goal past the last platform
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals