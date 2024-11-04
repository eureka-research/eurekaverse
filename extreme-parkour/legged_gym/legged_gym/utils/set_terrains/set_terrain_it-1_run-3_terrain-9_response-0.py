import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """A complex course of platforms, ramps, and narrow beams for the quadruped to navigate and balance."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]
    
    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    def add_platform(x_start, x_end, y_mid, height_min, height_max):
        y_half_width = m_to_idx(0.5)  # 1 meter wide platform
        platform_height = np.random.uniform(height_min, height_max)
        height_field[x_start:x_end, y_mid-y_half_width:y_mid+y_half_width] = platform_height

    def add_ramp(x_start, x_end, y_mid, height_min, height_max, slope_up):
        y_half_width = m_to_idx(0.5)  # 1 meter wide ramp
        ramp_height = np.random.uniform(height_min, height_max)
        slope = np.linspace(0, ramp_height, x_end-x_start) * (1 if slope_up else -1)
        slope = slope[:, None]
        height_field[x_start:x_end, y_mid-y_half_width:y_mid+y_half_width] = slope

    def add_beam(x_start, x_end, y_mid, beam_height):
        y_half_width = m_to_idx(0.2)  # 0.4 meter wide beam
        height_field[x_start:x_end, y_mid-y_half_width:y_mid+y_half_width] = beam_height

    def define_goal(x, y, index):
        goals[index] = [x, y]

    spawn_length = m_to_idx(2)
    mid_y = m_to_idx(width) // 2

    height_field[0:spawn_length, :] = 0  # Flat spawn area
    define_goal(spawn_length - m_to_idx(0.5), mid_y, 0)

    x_cursor = spawn_length
    height_min, height_max = 0.2 * difficulty, 0.5 * difficulty
    gap_min, gap_max = m_to_idx(0.2), m_to_idx(difficulty + 0.5)

    # First Platform
    platform_length = m_to_idx(1.5 + 0.3 * difficulty)
    add_platform(x_cursor, x_cursor + platform_length, mid_y, height_min, height_max)
    define_goal(x_cursor + platform_length // 2, mid_y, 1)
    x_cursor += platform_length + np.random.randint(gap_min, gap_max)
    
    # Second Beam
    beam_length = m_to_idx(1 + 0.5 * difficulty)
    add_beam(x_cursor, x_cursor + beam_length, mid_y, np.random.uniform(height_min, height_max))
    define_goal(x_cursor + beam_length // 2, mid_y, 2)
    x_cursor += beam_length + np.random.randint(gap_min, gap_max)
    
    # Third Ramp (up)
    ramp_length = m_to_idx(1.5 + 0.4 * difficulty)
    add_ramp(x_cursor, x_cursor + ramp_length, mid_y, height_min, height_max, slope_up=True)
    define_goal(x_cursor + ramp_length // 2, mid_y, 3)
    x_cursor += ramp_length + np.random.randint(gap_min, gap_max)

    # Fourth Platform
    add_platform(x_cursor, x_cursor + platform_length, mid_y, height_min, height_max)
    define_goal(x_cursor + platform_length // 2, mid_y, 4)
    x_cursor += platform_length + np.random.randint(gap_min, gap_max)
    
    # Fifth Ramp (down)
    add_ramp(x_cursor, x_cursor + ramp_length, mid_y, height_min, height_max, slope_up=False)
    define_goal(x_cursor + ramp_length // 2, mid_y, 5)
    x_cursor += ramp_length + np.random.randint(gap_min, gap_max)
    
    # Sixth Beam
    add_beam(x_cursor, x_cursor + beam_length, mid_y, np.random.uniform(height_min, height_max))
    define_goal(x_cursor + beam_length // 2, mid_y, 6)
    x_cursor += beam_length + np.random.randint(gap_min, gap_max)
    
    # Final Platform
    final_platform_length = m_to_idx(2)
    add_platform(x_cursor, x_cursor + final_platform_length, mid_y, height_min, height_max)
    define_goal(x_cursor + final_platform_length // 2, mid_y, 7)

    return height_field, goals