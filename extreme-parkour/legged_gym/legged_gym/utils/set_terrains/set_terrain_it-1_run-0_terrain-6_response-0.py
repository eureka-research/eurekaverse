import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Mixed terrain with platforms, ramps, and narrow beams to challenge navigation and precision skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Dimension variables for various obstacles.
    platform_length = m_to_idx(0.8 - 0.3 * difficulty)
    platform_width = m_to_idx(random.uniform(0.4, 0.7))
    platform_height_min, platform_height_max = 0.2, 0.5 + 0.5 * difficulty
    gap_length = m_to_idx(0.1 + 0.5 * difficulty)
    ramp_length = m_to_idx(1.0)
    narrow_beam_width = m_to_idx(0.2)
    narrow_beam_length = m_to_idx(1.2)
    mid_y = m_to_idx(width / 2)
    
    def add_platform(start_x, end_x, y_start, y_end):
        platform_height = np.random.uniform(platform_height_min, platform_height_max)
        height_field[start_x:end_x, y_start:y_end] = platform_height

    def add_ramp(start_x, end_x, mid_y, height_start, height_end, direction=1):
        half_width = platform_width // 2
        y1, y2 = mid_y - half_width, mid_y + half_width
        ramp_height = np.linspace(height_start, height_end, end_x - start_x) * direction
        for i in range(start_x, end_x):
            height_field[i, y1:y2] = ramp_height[i - start_x]

    def add_narrow_beam(start_x, end_x, y_start, y_end):
        beam_height = np.random.uniform(0.3, 0.5 + 0.3 * difficulty)
        height_field[start_x:end_x, y_start:y_end] = beam_height
    
    def add_goal(x, y):
        goals[len(goals[goals != 0]) // 2] = [x, y]

    # Set the starting flat ground area.
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # Position of the first goal
    add_goal(spawn_length - m_to_idx(1), mid_y)
    
    current_x = spawn_length

    for i in range(6):
        obstacle_choice = random.choice(['platform', 'ramp', 'narrow_beam'])
        if obstacle_choice == 'platform':
            end_x = current_x + platform_length
            y1, y2 = mid_y - platform_width // 2, mid_y + platform_width // 2
            add_platform(current_x, end_x, y1, y2)
            add_goal((current_x + end_x) // 2, mid_y)
            current_x = end_x + gap_length

        elif obstacle_choice == 'ramp':
            end_x = current_x + ramp_length
            direction = random.choice([1, -1])
            add_ramp(current_x, end_x, mid_y, 0.2, 0.5 + 0.3 * difficulty, direction)
            add_goal((current_x + end_x) // 2, mid_y)
            current_x = end_x + gap_length

        elif obstacle_choice == 'narrow_beam':
            end_x = current_x + narrow_beam_length
            y1, y2 = mid_y - narrow_beam_width // 2, mid_y + narrow_beam_width // 2
            add_narrow_beam(current_x, end_x, y1, y2)
            add_goal((current_x + end_x) // 2, mid_y)
            current_x = end_x + gap_length

    # Add the final platform and the last goal.
    final_platform_length = m_to_idx(1.5)
    final_platform_height = np.random.uniform(platform_height_min, platform_height_max)
    y1, y2 = mid_y - platform_width // 2, mid_y + platform_width // 2
    height_field[current_x:current_x + final_platform_length, y1:y2] = final_platform_height
    add_goal(current_x + final_platform_length // 2, mid_y)

    height_field[current_x + final_platform_length:, :] = 0

    return height_field, goals