import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Complex elevated terrain with varied obstacles to enhance difficulty, testing balance, stability, and jumping abilities."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Platform and obstacle dimensions variables
    base_platform_length = 1.0 - 0.2 * difficulty
    platform_length = m_to_idx(base_platform_length)
    platform_width_low, platform_width_high = 0.8, 1.2
    platform_height_min, platform_height_max = 0.2 + 0.3 * difficulty, 0.5 + 0.5 * difficulty
    gap_length = 0.3 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, center_y, height, width):
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = center_y - half_width, center_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_inclined_platform(start_x, end_x, mid_y, direction):
        width = np.random.uniform(platform_width_low, platform_width_high)
        width = m_to_idx(width)
        ramp_height = np.random.uniform(platform_height_min, platform_height_max)
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        slope = np.linspace(0, ramp_height, x2 - x1)[:, None]
        if direction == "up":
            height_field[x1:x2, y1:y2] = slope
        else:  # "down"
            height_field[x1:x2, y1:y2] = slope[::-1]

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    last_x = spawn_length
    for i in range(6):
        if i % 2 == 0:
            obstacle_length = platform_length
            width = np.random.uniform(platform_width_low, platform_width_high)
            width = m_to_idx(width)
            height = np.random.uniform(platform_height_min, platform_height_max)
            dx = np.random.randint(dx_min, dx_max)
            dy = np.random.randint(dy_min, dy_max)
            add_platform(last_x + gap_length, last_x + gap_length + obstacle_length + dx, mid_y + dy, height, width)
            last_x += gap_length + obstacle_length + dx
        else:
            obstacle_length = platform_length * 2  # Slightly longer ramps
            add_inclined_platform(last_x + gap_length, last_x + gap_length + obstacle_length, mid_y, "up" if i % 3 else "down")
            last_x += gap_length + obstacle_length

        goals[i+1] = [last_x - (obstacle_length / 2), mid_y + dy if i % 2 == 0 else mid_y]
        
    # Add final goal behind the last platform, fill in the remaining gap
    goals[-1] = [last_x + m_to_idx(0.5), mid_y]
    height_field[last_x:, :] = 0

    return height_field, goals