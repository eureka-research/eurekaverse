import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Challenging balance on narrow beams with gaps and varying heights."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Parameters (increase obstacle complexity based on difficulty)
    platform_width_min, platform_width_max = 0.3, 0.5  # Narrower beams for balance testing
    gap_width = 0.4 + 0.6 * difficulty  # Increase gap width with difficulty
    platform_height_min, platform_height_max = 0.1 + 0.2 * difficulty, 0.15 + 0.35 * difficulty

    platform_width_min, platform_width_max = m_to_idx([platform_width_min, platform_width_max])
    gap_width = m_to_idx(gap_width)
    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, length, width, height, mid_y, offset_y=0):
        half_width = width // 2
        height_field[start_x:start_x+length, mid_y - half_width + offset_y : mid_y + half_width + offset_y] = height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at the spawn point

    # Create terrain
    cur_x = spawn_length
    obstacle_count = 0

    while obstacle_count < 7:
        # Determine platform parameters
        platform_length = m_to_idx(0.8)
        platform_width = np.random.randint(platform_width_min, platform_width_max)
        platform_height = np.random.uniform(platform_height_min, platform_height_max)

        # Create platform
        add_platform(cur_x, platform_length, platform_width, platform_height, mid_y)

        # Set goal on the platform
        goals[obstacle_count+1] = [cur_x + platform_length // 2, mid_y]

        # Add gap before the next platform leading to variability in difficulty
        cur_x += platform_length + gap_width

        obstacle_count += 1

    # Provide extra challenge before the final goal
    final_platform_height = max(platform_height_min, platform_height_max)
    cur_x += gap_width
    add_platform(cur_x, platform_length, platform_width_max, final_platform_height, mid_y)
    goals[-1] = [cur_x + platform_length // 2, mid_y]

    # Fill the rest of the terrain to flat ground
    height_field[cur_x+platform_length:, :] = 0

    return height_field, goals