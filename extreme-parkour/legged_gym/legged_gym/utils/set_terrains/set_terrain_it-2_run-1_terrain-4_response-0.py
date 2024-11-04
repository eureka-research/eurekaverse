import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Mixed narrow beams and varied-height steps for precision foot placement and stability."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    
    # Set up platform and step dimensions
    platform_length = 0.6 + 0.2 * difficulty  # Longer for easier course, shorter for harder
    platform_length = m_to_idx(platform_length)
    platform_width = 0.4 + 0.2 * difficulty  # Wide platforms for easier and narrow for harder
    platform_width = m_to_idx(platform_width)

    step_height_min = 0.05 * difficulty
    step_height_max = 0.25 * difficulty
    gap_length = 0.2 + 0.3 * difficulty  # Smaller gaps for easier course, larger gaps for harder
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        """Adds a platform to the height field."""
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_step(start_x, end_x, mid_y, height):
        """Adds steps of varying heights to the terrain."""
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = m_to_idx(-0.1), m_to_idx(0.1)
    dy_min, dy_max = m_to_idx(-0.2), m_to_idx(0.2)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal near the spawn area
    
    cur_x = spawn_length
    for i in range(6):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        height = np.random.uniform(step_height_min, step_height_max)
        
        if i % 2 == 0:  # Even - add platform
            add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, height)
        else:  # Odd - add step
            add_step(cur_x, cur_x + platform_length + dx, mid_y + dy, height)
        
        goals[i+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += platform_length + dx + gap_length

    # Add final goal after the last platform/step
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals