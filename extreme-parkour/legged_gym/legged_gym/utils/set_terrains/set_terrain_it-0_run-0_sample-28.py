import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Obstacle course with a combination of narrow balance beams, steps, and small pits to test balance and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Dimensions
    beam_length = 2.0  # length of the balance beam
    beam_width = 0.4   # width of the balance beam
    beam_height = 0.05 + 0.2 * difficulty  # height of the balance beam relative to difficulty level
    step_width = 0.4  # width of each step (narrow path)
    step_height = 0.1 + 0.3 * difficulty  # height of each step
    pit_depth = -0.2 - 0.5 * difficulty  # depth of pit

    beam_length = m_to_idx(beam_length)
    beam_width = m_to_idx(beam_width)
    step_width = m_to_idx(step_width)
    pit_depth = m_to_idx(pit_depth)

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, mid_y):
        """Adds a narrow balance beam centered at (start_x, mid_y)."""
        half_width = beam_width // 2
        x1, x2 = start_x, start_x + beam_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = beam_height

    def add_steps(start_x, mid_y):
        """Adds a series of steps centered at (start_x, mid_y)."""
        steps = 4
        step_length = m_to_idx(1.0) // steps
        height = 0
        for i in range(steps):
            height += step_height
            x1, x2 = start_x + i * step_length, start_x + (i + 1) * step_length
            y1, y2 = mid_y - step_width // 2, mid_y + step_width // 2
            height_field[x1:x2, y1:y2] = height

    def add_pit(start_x, mid_y, pit_length):
        """Adds a pit centered at (start_x, mid_y)."""
        x1, x2 = start_x, start_x + m_to_idx(pit_length)
        y1, y2 = mid_y - step_width // 2, mid_y + step_width // 2
        height_field[x1:x2, y1:y2] = pit_depth

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Create the obstacle course layout
    cur_x = spawn_length
    pit_interval = 0.1 + 0.3 * difficulty  # interval in meters between pits
    pit_interval = m_to_idx(pit_interval)

    obstacles = ['beam', 'steps', 'pit']  # possible obstacles
    num_obstacles = 7  # At least 7 obstacles to fit between start and end points

    for i in range(num_obstacles):
        obstacle = random.choice(obstacles)
        
        if obstacle == 'beam':
            add_beam(cur_x, mid_y)
        elif obstacle == 'steps':
            add_steps(cur_x, mid_y)
        elif obstacle == 'pit':
            pit_length = 1.0 + 1.0 * difficulty
            add_pit(cur_x, mid_y, pit_length)
        
        goals[i+1] = [cur_x + beam_length / 2, mid_y]
        cur_x += max(beam_length, step_width, pit_interval)

    goals[-1] = [cur_x - m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals