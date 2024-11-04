import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """A course with alternating step heights and staggered platforms for precise navigation and jumping."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    # Initialize height field and goals arrays
    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Terrain element dimensions based on difficulty
    platform_length = 1.2 - 0.5 * difficulty  # Adjust platform length
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.45, 0.65)  # Narrower platform width
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.15 + 0.35 * difficulty, 0.20 + 0.45 * difficulty  # Increased heights
    
    step_length = 0.7 - 0.3 * difficulty  # Shorter steps
    step_length = m_to_idx(step_length)
    step_height_min, step_height_max = 0.15 + 0.3 * difficulty, 0.2 + 0.4 * difficulty  # Increased steps
    gap_length = 0.1 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        half_width = platform_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    def add_step(start_x, end_x, mid_y, height):
        half_width = step_length // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.3, 0.3
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    for i in range(4):  # Alternating platforms and steps
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        # Add platform
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        add_platform(cur_x, cur_x + platform_length + dx, mid_y + dy, platform_height)
        # Put goal in the center of the platform
        goals[i*2+1] = [cur_x + (platform_length + dx) / 2, mid_y + dy]
        # Move x forward by adding platform length
        cur_x += platform_length + dx + gap_length

        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        # Add step
        step_height = np.random.uniform(step_height_min, step_height_max)
        add_step(cur_x, cur_x + step_length + dx, mid_y + dy, step_height)
        # Put goal in the center of the step
        goals[i*2+2] = [cur_x + (step_length + dx) / 2, mid_y + dy]
        # Move x forward by adding step length
        cur_x += step_length + dx + gap_length
    
    # Add final goal behind the last step, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals