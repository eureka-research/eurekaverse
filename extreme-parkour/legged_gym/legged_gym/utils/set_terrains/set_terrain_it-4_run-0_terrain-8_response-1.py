import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Combines wide platforms, beams, ramps, and steps for a diverse navigation course"""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up dimensions
    platform_length = m_to_idx(1.2 - 0.3 * difficulty)
    platform_width = m_to_idx(np.random.uniform(1.0, 1.5))  # Wide platforms for stability
    beam_length = m_to_idx(1.2)
    beam_width = m_to_idx(0.5)  # Narrow beams for precision
    ramp_length = m_to_idx(2.0)
    step_length = m_to_idx(0.5)
    gap_length = m_to_idx(0.8 * difficulty)
    step_height = np.random.uniform(0.1, 0.3 * difficulty)

    mid_y = m_to_idx(width) // 2
    
    def add_platform(x, length, y, width, height):
        half_width = width // 2
        height_field[x:x+length, y-half_width:y+half_width] = height

    def add_beam(x, length, y, width, height):
        half_width = width // 2
        height_field[x:x+length, y-half_width:y+half_width] = height

    def add_ramp(x, length, y, width, height, direction):
        half_width = width // 2
        slant = np.linspace(0, direction * height, num=length)
        height_field[x:x+length, y-half_width:y+half_width] = slant[:, None]

    def add_step(x, length, y, width, height):
        half_width = width // 2
        height_field[x:x+length, y-half_width:y+half_width] += height

    # Set the ground and initial goal
    spawn_length = m_to_idx(2)
    height_field[:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    # Sequence of obstacles
    obstacles = [
        ("platform", platform_length, platform_width, np.random.uniform(0.2, 0.3)),
        ("beam", beam_length, beam_width, np.random.uniform(0.3, 0.4)),
        ("ramp", ramp_length, platform_width, np.random.uniform(0.15, 0.35), 1),
        ("platform", platform_length, platform_width, np.random.uniform(0.1, 0.3)),
        ("beam", beam_length, beam_width, np.random.uniform(0.2, 0.4)),
        ("ramp", ramp_length, platform_width, np.random.uniform(0.15, 0.35), -1),
        ("step", step_length, platform_width, step_height),
        ("platform", platform_length, platform_width, 0.0)  # Final flat platform
    ]

    # Placing obstacles and goals
    for i, obstacle in enumerate(obstacles):
        if obstacle[0] == "platform":
            add_platform(cur_x, obstacle[1], mid_y, obstacle[2], obstacle[3])
        elif obstacle[0] == "beam":
            add_beam(cur_x, obstacle[1], mid_y, obstacle[2], obstacle[3])
        elif obstacle[0] == "ramp":
            add_ramp(cur_x, obstacle[1], mid_y, obstacle[2], obstacle[3], obstacle[4])
        elif obstacle[0] == "step":
            add_step(cur_x, obstacle[1], mid_y, obstacle[2], obstacle[3])
        
        # Update goals
        goals[i+1] = [cur_x + obstacle[1] // 2, mid_y]
        cur_x += obstacle[1] + gap_length
    
    return height_field, goals