import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """A series of alternating steps and tilted platforms to test precise foot placement and balance in varied terrain."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Terrain and obstacle configurations
    step_height_base = 0.1
    step_height_var = 0.15 * difficulty
    step_length = 0.5
    platform_length = 1.2 - 0.5 * difficulty
    platform_width = 0.6 + 0.5 * difficulty
    platform_tilt_max = 0.1 + 0.3 * difficulty
    gap_length = 0.3 * difficulty

    step_length = m_to_idx(step_length)
    platform_length = m_to_idx(platform_length)
    platform_width = m_to_idx(platform_width)
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_step(start_x, height):
        width = m_to_idx(0.8)
        half_width = width // 2
        x1, x2 = start_x, start_x + step_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_tilted_platform(start_x, end_x, mid_y, tilt_angle):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        tilt = np.linspace(0, tilt_angle, y2 - y1)
        tilt = tilt[None, :]  # Add a dimension for broadcasting to x
        height_field[x1:x2, y1:y2] = tilt

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    current_x = spawn_length

    # Place alternating steps and tilted platforms
    for i in range(3):
        # Step
        step_height = step_height_base + random.uniform(-step_height_var, step_height_var)
        add_step(current_x, step_height)
        goals[i+1] = [current_x + step_length // 2, mid_y]
        current_x += step_length

        # Gap
        current_x += gap_length

        # Tilted platform
        tilt_angle = random.uniform(0, platform_tilt_max)
        add_tilted_platform(current_x, current_x + platform_length, mid_y, tilt_angle)
        goals[i+4] = [current_x + platform_length // 2, mid_y]
        current_x += platform_length

        # Gap
        current_x += gap_length

    # Add final goal at the end
    goals[-1] = [m_to_idx(11.5), mid_y]
    height_field[m_to_idx(11):, :] = 0

    return height_field, goals