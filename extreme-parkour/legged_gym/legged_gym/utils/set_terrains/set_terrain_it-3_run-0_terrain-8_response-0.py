import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Tilted platforms and uneven terrain with wider gaps for the robot to traverse and balance."""
   
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define obstacle parameters
    platform_length = m_to_idx(0.8 - 0.2 * difficulty)
    platform_width = m_to_idx(1.0)
    tilt_angle = 10.0 + 10.0 * difficulty  # Increase tilt angle with difficulty
    max_step_height = 0.1 + 0.15 * difficulty  # Increase step height with difficulty
    gap_length = m_to_idx(0.1 + 0.6 * difficulty)  # Increase gap length with difficulty

    mid_y = m_to_idx(width) // 2

    def add_tilted_platform(start_x, end_x, mid_y, angle):
        """Add a tilted platform to height_field."""
        width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - width, mid_y + width
        slope = (np.tan(np.radians(angle)) * (x2 - x1)) / (y2 - y1)
        height_field[x1:x2, y1:y2] = slope * np.arange(y2 - y1)[None, :]

    def add_step(start_x, end_x, mid_y, height):
        """Add a step with specified height to height_field."""
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = m_to_idx(-0.1), m_to_idx(0.1)
    dy_min, dy_max = m_to_idx(-0.4), m_to_idx(0.4)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    current_x = spawn_length

    for i in range(3):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)

        # Add tilted platform
        if i % 2 == 0:
            add_tilted_platform(current_x, current_x + platform_length + dx, mid_y + dy, tilt_angle)
            goals[i + 1] = [current_x + (platform_length + dx) / 2, mid_y + dy]
        # Add staggered steps
        else:
            step_height = np.random.uniform(0.2, max_step_height)
            add_step(current_x, current_x + platform_length + dx, mid_y + dy, step_height)
            goals[i + 1] = [current_x + (platform_length + dx) / 2, mid_y + dy]

        # Add gap
        current_x += platform_length + dx + gap_length

    # Add final goal behind the last obstacle
    goals[-1] = [current_x + m_to_idx(0.5), mid_y]
    height_field[current_x:, :] = 0

    return height_field, goals