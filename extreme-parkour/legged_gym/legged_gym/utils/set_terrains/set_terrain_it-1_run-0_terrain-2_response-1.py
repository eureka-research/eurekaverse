import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Complex stepping stones and swinging bridges to test the robot's balance, agility, and navigation skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]
    
    def add_platform(x_start, x_end, y_mid, height):
        half_width = platform_width // 2
        y_min = y_mid - half_width
        y_max = y_mid + half_width
        height_field[x_start:x_end, y_min:y_max] = height

    def add_ramp(x_start, x_end, y_mid, height_start, height_end, direction=1):
        half_width = ramp_width // 2
        y_min = y_mid - half_width
        y_max = y_mid + half_width
        height_gradient = np.linspace(height_start, height_end, x_end - x_start)
        if direction == -1: height_gradient = height_gradient[::-1]
        for x idx, height in enumerate(height_gradient):
            height_field[x_start+idx, y_min:y_max] = height

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Obstacle dimensions and spacing
    platform_length = 1.0 - 0.3 * difficulty
    platform_length = m_to_idx(platform_length)
    platform_width = np.random.uniform(0.4, 0.5)  # Narrow platforms
    platform_width = m_to_idx(platform_width)
    platform_height_min, platform_height_max = 0.2, 0.4 * difficulty

    ramp_width = platform_width  # Same for simplicity
    ramp_length = 1.0  # Fixed length for ramps
    ramp_length = m_to_idx(ramp_length)

    swing_length = 2.0  # Swinging bridge length
    swing_length = m_to_idx(swing_length)
    
    gap_length = 0.1 + 0.5 * difficulty  # Gaps to step over
    gap_length = m_to_idx(gap_length)
    
    mid_y = m_to_idx(width / 2)  # Centerline of the course

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # First goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Variable height and gapped platforms
    cur_x = spawn_length
    for idx in range(6):
        height = np.random.uniform(platform_height_min, platform_height_max)
        add_platform(cur_x, cur_x + platform_length, mid_y, height)
        
        goals[idx + 1] = [cur_x + platform_length // 2, mid_y]

        # Increment x for next platform
        cur_x += platform_length + gap_length

    # Introduce moving ramps
    for _ in range(2):
        height_start = np.random.uniform(platform_height_min, platform_height_max)
        height_end = np.random.uniform(platform_height_min, platform_height_max)
        direction = random.choice([-1, 1])
        add_ramp(cur_x, cur_x + ramp_length, mid_y, height_start, height_end, direction)
        
        cur_x += ramp_length + gap_length

    # Final section should have a swinging bridge
    height_bridge = np.random.uniform(platform_height_min, platform_height_max)
    add_platform(cur_x, cur_x + swing_length, mid_y, height_bridge)
    goals[-1] = [cur_x + swing_length // 2, mid_y]

    return height_field, goals