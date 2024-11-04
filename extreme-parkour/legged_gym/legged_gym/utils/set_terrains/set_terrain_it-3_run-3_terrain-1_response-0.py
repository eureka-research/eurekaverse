import random
import numpy as np

def set_terrain(length, width, field_resolution, difficulty):
    """Combines larger gaps, angled ramps, and narrow bridges for balance, climbing and jumping."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    platform_length_min = m_to_idx(0.8 - 0.2 * difficulty)
    platform_length_max = m_to_idx(1.2 + 0.2 * difficulty)
    platform_height_min, platform_height_max = 0.1 + 0.3 * difficulty, 0.2 + 0.6 * difficulty
    bridge_width = m_to_idx(0.4 - 0.1 * difficulty)
    gap_length_min = m_to_idx(0.3 + 0.7 * difficulty)
    gap_length_max = m_to_idx(0.5 + 0.9 * difficulty)

    mid_y = m_to_idx(width) // 2

    def add_platform(start_x, end_x, mid_y, height):
        y1, y2 = mid_y - m_to_idx(0.5), mid_y + m_to_idx(0.5)
        height_field[start_x:end_x, y1:y2] = height

    def add_ramp(start_x, end_x, mid_y, direction, height):
        y1, y2 = mid_y - m_to_idx(0.5), mid_y + m_to_idx(0.5)
        ramp_height = np.linspace(0, height, y2 - y1)[::direction]
        ramp_height = ramp_height[None, :]
        height_field[start_x:end_x, y1:y2] = ramp_height

    def add_bridge(start_x, end_x, mid_y, width_idx):
        y1, y2 = mid_y - width_idx // 2, mid_y + width_idx // 2
        height_field[start_x:end_x, y1:y2] = platform_height_max

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    segment_names = ["platform", "gap", "ramp", "bridge", "ramp", "gap"]

    for i, segment in enumerate(segment_names):
        if segment == "platform":
            length = np.random.randint(platform_length_min, platform_length_max)
            height = np.random.uniform(platform_height_min, platform_height_max)
            add_platform(cur_x, cur_x + length, mid_y, height)
            goals[i + 1] = [cur_x + length // 2, mid_y]
        elif segment == "gap":
            length = np.random.randint(gap_length_min, gap_length_max)
            cur_x += length
            height_field[cur_x, :] = -1.0  # Representing the gap as a lower height
        elif segment == "ramp":
            length = np.random.randint(platform_length_min, platform_length_max)
            height = np.random.uniform(platform_height_min, platform_height_max)
            direction = 1 if i % 2 == 0 else -1  # Alternate ramps
            add_ramp(cur_x, cur_x + length, mid_y, direction, height)
            goals[i + 1] = [cur_x + length // 2, mid_y]
        else:  # bridge
            length = np.random.randint(platform_length_min, platform_length_max)
            add_bridge(cur_x, cur_x + length, mid_y, bridge_width)
            goals[i + 1] = [cur_x + length // 2, mid_y]

        # Move to the next starting x position
        cur_x += length

    # Add goal at the end
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals