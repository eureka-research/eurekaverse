import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Rolling hills and slopes to test the quadruped's balance and adaptability to uneven terrain."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        if isinstance(m, (list, tuple)):
            return [round(i / field_resolution) for i in m]
        else:
            return np.round(m / field_resolution).astype(np.int16)

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    length_idx = m_to_idx(length)
    width_idx = m_to_idx(width)

    hill_height_min = 0.1 * difficulty
    hill_height_max = 0.5 * difficulty

    slope_gradient_min = 0.02 * difficulty
    slope_gradient_max = 0.1 * difficulty

    slope_width_min = 1.0
    slope_width_max = 3.0

    def add_hill(height_field, center_x, center_y, radius_idx, height):
        """Adds a hill to the height field."""
        for x in range(center_x - radius_idx, center_x + radius_idx):
            for y in range(center_y - radius_idx, center_y + radius_idx):
                if 0 <= x < length_idx and 0 <= y < width_idx:
                    distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
                    if distance <= radius_idx:
                        height_field[x, y] += height * (1 - (distance / radius_idx))

    def add_slope(height_field, start_x, end_x, start_y, end_y, gradient):
        """Adds a slope to the height field."""
        delta_x = end_x - start_x
        delta_y = end_y - start_y
        distance = np.sqrt(delta_x**2 + delta_y**2)
        num_steps = int(distance)
        for step in range(num_steps):
            x = int(start_x + step * delta_x / num_steps)
            y = int(start_y + step * delta_y / num_steps)
            if 0 <= x < length_idx and 0 <= y < width_idx:
                height_field[x, y] += step * gradient

    # Initial flat area where the quadruped starts
    spawn_length_idx = m_to_idx(2)
    height_field[0:spawn_length_idx, :] = 0
    goals[0] = [spawn_length_idx - m_to_idx(0.5), width_idx // 2]  # First goal at spawn

    # Define goals and obstacles
    current_x = spawn_length_idx
    for i in range(1, 8):
        if i % 2 == 1:
            # Add hill
            hill_radius = m_to_idx(np.random.uniform(0.5, 1.0))
            hill_height = np.random.uniform(hill_height_min, hill_height_max)
            center_y = np.random.randint(m_to_idx(1.0), width_idx - m_to_idx(1.0))
            add_hill(height_field, current_x + hill_radius, center_y, hill_radius, hill_height)
            goals[i] = [current_x + hill_radius, center_y]
            current_x += 2 * hill_radius
        else:
            # Add slope
            slope_width = np.random.uniform(slope_width_min, slope_width_max)
            slope_gradient = np.random.uniform(slope_gradient_min, slope_gradient_max)
            end_x = current_x + m_to_idx(slope_width)
            end_y = np.random.randint(m_to_idx(1.0), width_idx - m_to_idx(1.0))
            add_slope(height_field, current_x, end_x, width_idx // 2, end_y, slope_gradient)
            goals[i] = [end_x, end_y]
            current_x = end_x

    # Ensure final goal is reachable
    goals[-1] = [min(current_x + m_to_idx(1.0), length_idx - 1), width_idx // 2]
    height_field[int(goals[-1, 0]):, :] = 0

    return height_field, goals