import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Serpentine pathways with varying heights and narrow bridges to test the robot's turning and balance abilities."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Setup parameters for serpentine pathways and bridges
    pathway_width = 0.4 + 0.6 * (1 - difficulty)
    pathway_width = m_to_idx(pathway_width)
    pathway_height_min, pathway_height_max = 0.1 * difficulty, 0.4 * difficulty
    bridge_length = 1.0 - 0.7 * difficulty
    bridge_length = m_to_idx(bridge_length)
    bridge_height_min, bridge_height_max = 0.2 * difficulty, 0.5 * difficulty

    y_center = m_to_idx(width / 2)
    serpentine_amplitude = m_to_idx(0.5 + 1.5 * difficulty)
    serpentine_frequency = 3 + 5 * difficulty

    def add_pathway_pattern(start_x, end_x, y_center, serpentine_amplitude, serpentine_frequency):
        half_width = pathway_width // 2
        for x in range(start_x, end_x):
            offset = int(serpentine_amplitude * np.sin(serpentine_frequency * 2 * np.pi * (x - start_x) / (end_x - start_x)))
            y1, y2 = y_center + offset - half_width, y_center + offset + half_width
            pathway_height = np.random.uniform(pathway_height_min, pathway_height_max)
            height_field[x, y1:y2] = pathway_height

    def add_bridge(start_x, start_y, end_x, end_y):
        if start_x > end_x or start_y > end_y:
            return
        height_diff = np.random.uniform(bridge_height_min, bridge_height_max)
        bridge_slope = np.linspace(0, height_diff, num=end_x - start_x)
        mid_y = (start_y + end_y) // 2
        for x in range(start_x, end_x):
            height_field[x, mid_y-2:mid_y+2] = bridge_slope[x-start_x]

    dx_min, dx_max = m_to_idx(-0.05), m_to_idx(0.05)
    dy_min, dy_max = m_to_idx(-0.2), m_to_idx(0.2)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), y_center]

    # Add serpentine pathways
    cur_x = spawn_length
    section_length = m_to_idx(2)
    for i in range(4):  # Four primary sections
        next_x = cur_x + section_length
        dy = np.random.randint(dy_min, dy_max)
        add_pathway_pattern(cur_x, next_x, y_center + dy, serpentine_amplitude, serpentine_frequency)
        goals[i+1] = [cur_x + section_length // 2, y_center + dy]
        cur_x = next_x + m_to_idx(0.1)

    # Add narrow bridges connecting pathways
    for i in range(4, 7):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_bridge(cur_x, y_center + dy, cur_x + bridge_length, y_center + dy)
        goals[i+1] = [cur_x + bridge_length // 2, y_center + dy]
        cur_x += bridge_length + m_to_idx(0.1)

    # Add final goal behind the last section of serpentine pathway or bridge
    goals[-1] = [cur_x + m_to_idx(0.5), y_center]
    height_field[cur_x:, :] = 0

    return height_field, goals