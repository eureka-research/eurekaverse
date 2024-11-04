import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Zigzag beams for the robot to balance on and navigate around obstacles."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up beam dimensions
    beam_length = 1.4 - 0.5 * difficulty  # Beam length decreases with difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = 0.35 + 0.1 * difficulty  # Increased width to balance challenge
    beam_width = m_to_idx(beam_width)
    beam_height_min, beam_height_max = 0.2 + 0.2 * difficulty, 0.4 + 0.2 * difficulty

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, mid_y, height, angle=0):
        half_width = beam_width // 2
        end_x = start_x + beam_length
        y1, y2 = mid_y - half_width, mid_y + half_width
        if angle != 0:
            # Define angled beam by using height to form incline/decline
            for x in range(start_x, end_x):
                offset = int((x - start_x) * np.tan(angle))
                height_field[x, mid_y - half_width + offset: mid_y + half_width + offset] = height
        else:
            height_field[start_x:end_x, y1:y2] = height

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
    for i in range(6):  # Set up 6 beams
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        angle = (-1 if i % 2 == 0 else 1) * np.radians(10 + difficulty * 10)  # Alternating angles for zigzag
        beam_height = np.random.uniform(beam_height_min, beam_height_max)
        add_beam(cur_x, mid_y + dy, beam_height, angle)
        
        # Put goal in the center of each beam
        goals[i+1] = [cur_x + beam_length / 2 + dx, mid_y + dy]

        # Add gap of 0.4 meter between each beam to require maneuvering
        gap_length = m_to_idx(0.4)
        cur_x += beam_length + gap_length + dx
    
    # Add final goal in the center of the last beam, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    # Ensure the last section is on flat ground
    height_field[cur_x:, :] = 0

    return height_field, goals