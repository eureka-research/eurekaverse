
import numpy as np
import random

def set_terrain(terrain, variation, difficulty):
    terrain_fns = [
        set_terrain_0,
        set_terrain_1,
        set_terrain_2,
        set_terrain_3,
        set_terrain_4,
        set_terrain_5,
        set_terrain_6,
        set_terrain_7,
        set_terrain_8,
        set_terrain_9,
        # INSERT TERRAIN FUNCTIONS HERE
    ]
    idx = int(variation * len(terrain_fns))
    height_field, goals = terrain_fns[idx](terrain.width * terrain.horizontal_scale, terrain.length * terrain.horizontal_scale, terrain.horizontal_scale, difficulty)
    terrain.height_field_raw = (height_field / terrain.vertical_scale).astype(np.int16)
    terrain.goals = goals
    return idx

def set_terrain_0(length, width, field_resolution, difficulty):
    """Stepping stones terrain for the robot to navigate over discontinuous and varying height obstacles."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up stepping stones dimensions
    stone_length_min, stone_length_max = 0.4, 0.7  # Minimum and maximum size of stepping stones
    stone_width_min, stone_width_max = 0.4, 0.7  # Minimum and maximum width of stepping stones
    stone_height_min, stone_height_max = 0.1 * difficulty, 0.5 * difficulty  # Minimum and maximum height of stepping stones
    gap_length_min, gap_length_max = 0.4 + (1 - difficulty) * 0.1, 0.6 + (1 - difficulty) * 0.2  # Minimum and maximum gaps between stepping stones

    mid_y = m_to_idx(width) // 2

    def add_stone(center_x, center_y):
        half_length = m_to_idx(random.uniform(stone_length_min, stone_length_max) / 2)
        half_width = m_to_idx(random.uniform(stone_width_min, stone_width_max) / 2)
        height = random.uniform(stone_height_min, stone_height_max)
        x1, x2 = center_x - half_length, center_x + half_length
        y1, y2 = center_y - half_width, center_y + half_width
        height_field[x1:x2, y1:y2] = height

        return (x1 + x2) / 2, (y1 + y2) / 2  # Return center coordinates for goal placement

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at spawn

    # Create stepping stones with increasing complexity
    cur_x = spawn_length
    num_stones = 7  # Number of stepping stones to place
    cur_y = mid_y

    for i in range(num_stones):
        gap_length = m_to_idx(random.uniform(gap_length_min, gap_length_max))
        cur_x += gap_length

        # Randomly shift stone in y-direction for more challenge
        cur_y += m_to_idx(random.uniform(-0.5, 0.5))

        stone_center_x, stone_center_y = add_stone(cur_x, cur_y)
        
        goals[i+1] = [stone_center_x, stone_center_y]

    # Final goal at the end of the course
    goals[-1] = [m_to_idx(length) - m_to_idx(0.5), mid_y]

    return height_field, goals

def set_terrain_1(length, width, field_resolution, difficulty):
    """Elevated beams for the robot to balance on and navigate across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Beam dimensions
    beam_width = np.random.uniform(0.4, 0.6)
    beam_width_idx = m_to_idx(beam_width)
    beam_height_min = 0.1 * difficulty
    beam_height_max = 0.15 + 0.3 * difficulty
    beam_length = 1.5
    beam_length_idx = m_to_idx(beam_length)

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, mid_y):
        half_width = beam_width_idx // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        beam_height = np.random.uniform(beam_height_min, beam_height_max)
        height_field[x1:x2, y1:y2] = beam_height

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
    for i in range(6):  # Add 6 beams
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_beam(cur_x, cur_x + beam_length_idx + dx, mid_y + dy)

        # Put goal in the center of the beam
        goals[i+1] = [cur_x + (beam_length_idx + dx) / 2, mid_y + dy]

        # Add gap between beams
        gap_length = 0.2 + 0.5 * difficulty
        gap_length_idx = m_to_idx(gap_length)
        cur_x += beam_length_idx + dx + gap_length_idx
    
    # Add final goal after the last beam
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_2(length, width, field_resolution, difficulty):
    """Narrow and uneven stepping stones traversing the terrain for the robot to balance and navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up stepping stones dimensions
    stone_length = np.random.uniform(0.4, 0.6)
    stone_length = m_to_idx(stone_length)
    stone_width = np.random.uniform(0.4, 0.6)
    stone_width = m_to_idx(stone_width)

    stone_height_min, stone_height_max = 0.1 + 0.2 * difficulty, 0.15 + 0.3 * difficulty
    gap_length_min, gap_length_max = 0.4, 0.6
    gap_length_min = m_to_idx(gap_length_min)
    gap_length_max = m_to_idx(gap_length_max)

    mid_y = m_to_idx(width) // 2

    def add_stone(x, y, length, width, height):
        half_length = length // 2
        half_width = width // 2
        x1, x2 = x - half_length, x + half_length
        y1, y2 = y - half_width, y + half_width
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = 0.4, 0.6
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.1, 0.1
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(6):  # Set up 6 stepping stones in a straight line with gaps
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        stone_height = np.random.uniform(stone_height_min, stone_height_max)
        add_stone(cur_x + dx, mid_y + dy, stone_length, stone_width, stone_height)

        # Put goal in the center of the stone
        goals[i+1] = [cur_x + dx, mid_y + dy]

        # Add gap
        cur_x += stone_length + gap_length_max
    
    # Add final goal behind the last stone, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_3(length, width, field_resolution, difficulty):
    """A winding path of blocks for the robot to walk, jump, and navigate turns through."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Parameters
    block_length = m_to_idx(0.8 - 0.2 * difficulty)  # Block length decreases with difficulty
    block_width = m_to_idx(1.5 + 0.5 * difficulty)  # Block width increases with difficulty
    block_height = np.linspace(0.1, 0.4, num=8) * difficulty  # Block height varies with difficulty
    gap_length = m_to_idx(0.1 + 0.3 * difficulty)  # Gap length increases with difficulty

    spawn_length = m_to_idx(2)

    # Set spawn area to flat ground
    height_field[:spawn_length, :] = 0

    # Initialization
    mid_y = m_to_idx(width / 2)
    cur_x = spawn_length
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at spawn

    # Winding path of blocks
    for i in range(7):
        # Choose a random offset within bounds for variety
        dy_min = -0.5 * difficulty
        dy_max = 0.5 * difficulty
        dy = np.random.uniform(dy_min, dy_max)
        cur_y = mid_y + m_to_idx(dy)

        # Ensure blocks fit within width bounds
        cur_y = max(block_width // 2, min(cur_y, m_to_idx(width) - block_width // 2))

        # Define block coordinates
        x1, x2 = cur_x, cur_x + block_length
        y1, y2 = cur_y - block_width // 2, cur_y + block_width // 2
        block_h = block_height[i % len(block_height)]

        # Place the block
        height_field[x1:x2, y1:y2] = block_h

        # Set the goal on the block
        goals[i + 1] = [(x1 + x2) // 2, (y1 + y2) // 2]

        # Add gap for next block
        cur_x += block_length + gap_length

    # Final goal after last block
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    # Put the remaining area to flat ground to end the course
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_4(length, width, field_resolution, difficulty):
    """Varied-height hurdles for the robot to navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Dimensions and characteristics of hurdles
    min_hurdle_height = 0.1  # Minimum hurdle height in meters
    max_hurdle_height = 0.4  # Maximum hurdle height in meters, scaled by difficulty
    hurdle_height_adjustment = difficulty * (max_hurdle_height - min_hurdle_height)
    hurdle_height_min, hurdle_height_max = min_hurdle_height, min_hurdle_height + hurdle_height_adjustment

    hurdle_length = 0.4  # Hurdle thickness in meters
    hurdle_length_quant = m_to_idx(hurdle_length)
    
    gap_min_length = 0.2  # Minimum gap in meters between hurdles
    gap_max_length = 1.0  # Maximum gap in meters between hurdles
    gap_length_adjustment = difficulty * (gap_max_length - gap_min_length)
    gap_length_min, gap_length_max = m_to_idx(gap_min_length), m_to_idx(gap_max_length)

    mid_y = m_to_idx(width / 2)

    def add_hurdle(start_x, hurdle_height):
        """Add a hurdle of a specified height to the height_field."""
        x1, x2 = start_x, start_x + hurdle_length_quant
        y1, y2 = mid_y - m_to_idx(0.5), mid_y + m_to_idx(0.5)
        height_field[x1:x2, y1:y2] = hurdle_height

    # Set the spawn area flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(7):  # Create 7 varied-height hurdles for a total of 8 goals
        hurdle_height = np.random.uniform(hurdle_height_min, hurdle_height_max)
        add_hurdle(cur_x, hurdle_height)
        
        # Place the goal just ahead of the hurdle
        goals[i + 1] = [cur_x + m_to_idx(0.2), mid_y]
        
        # Calculate the gap for the next hurdle based on minimum and maximum gap lengths
        gap_length = np.random.randint(gap_length_min, gap_length_max)
        cur_x += hurdle_length_quant + gap_length

    return height_field, goals

def set_terrain_5(length, width, field_resolution, difficulty):
    """Varied height stepping stones and narrow bridges requiring precise balance and agility."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    mid_y = m_to_idx(width) // 2

    # Set up spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Place the first goal at the end of the spawn area
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    def add_stepping_stones(start_x, end_x, y, height, width):
        y1, y2 = y - width // 2, y + width // 2
        height_field[start_x:end_x, y1:y2] = height

    def add_narrow_bridge(start_x, end_x, y, height):
        y1, y2 = y - m_to_idx(0.2), y + m_to_idx(0.2)  # Narrow bridge, 0.4 meters wide
        height_field[start_x:end_x, y1:y2] = height

    current_x = spawn_length
    stone_height = np.random.uniform(0.1, 0.3) * difficulty  # Height varies with difficulty

    for i in range(3):
        stone_width = m_to_idx(1 + 0.2 * difficulty)
        stone_length = m_to_idx(0.5 + 0.3 * difficulty)
        gap_between_stones = m_to_idx(0.5 + 0.5 * difficulty)

        # Add first stepping stone
        add_stepping_stones(current_x, current_x + stone_length, mid_y, stone_height, stone_width)
        goals[i + 1] = [current_x + stone_length / 2, mid_y]
        current_x += stone_length + gap_between_stones

        # Add second stepping stone
        add_stepping_stones(current_x, current_x + stone_length, mid_y, stone_height, stone_width)
        goals[i + 2] = [current_x + stone_length / 2, mid_y]
        current_x += stone_length + gap_between_stones

        # Reset for next pair of stones
        stone_height = np.random.uniform(0.1, 0.3) * difficulty

    # Add narrow bridges
    for i in range(3, 6):
        bridge_length = m_to_idx(1.0 + 0.5 * difficulty)
        bridge_height = np.random.uniform(0.05, 0.2) * difficulty
        current_x += m_to_idx(0.5)  # Adding a small gap before the bridge
        add_narrow_bridge(current_x, current_x + bridge_length, mid_y, bridge_height)
        goals[i + 1] = [current_x + bridge_length / 2, mid_y]
        current_x += bridge_length + m_to_idx(0.5)  # Adding gap after the bridge

    # Final goal position after the last bridge
    current_x += m_to_idx(0.5)
    goals[-1] = [current_x, mid_y]

    return height_field, goals

def set_terrain_6(length, width, field_resolution, difficulty):
    """Series of steps and elevated walkways for climbing and balancing."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define obstacle specifications based on difficulty
    step_height_min, step_height_max = 0.1 * difficulty, 0.4 * difficulty
    walkway_height = 0.2 + 0.5 * difficulty
    walkway_width_min = 0.4  # minimum width, ensuring it is passable
    walkway_width_max = 1.0 + 0.5 * difficulty

    # Initialize terrain with flat ground for the spawning area
    spawn_length = m_to_idx(2.0)
    height_field[:spawn_length, :] = 0
    mid_y = m_to_idx(width) // 2

    # Set first goal at the end of the spawn area
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Define a helper function for adding a step
    def add_step(x_start, x_end, y_center, height):
        half_width = m_to_idx(walkway_width_max) // 2
        y_start = max(0, y_center - half_width)
        y_end = min(m_to_idx(width), y_center + half_width)
        height_field[x_start:x_end, y_start:y_end] = height

    # Define a helper function for adding a walkway
    def add_walkway(x_start, x_end, y_center, width, height):
        half_width = m_to_idx(width) // 2
        y_start = max(0, y_center - half_width)
        y_end = min(m_to_idx(width), y_center + half_width)
        height_field[x_start:x_end, y_start:y_end] = height

    current_x = spawn_length
    height_increase = (step_height_max - step_height_min) / 6
    current_height = step_height_min

    # Create 6 steps and elevated walkways
    for i in range(6):
        step_length = m_to_idx(0.6)
        add_step(current_x, current_x + step_length, mid_y, current_height)
        
        # Set goals at each step
        goals[i + 1] = [current_x + step_length / 2, mid_y]
        
        current_x += step_length

        walkway_length = m_to_idx(0.8)
        walkway_width = random.uniform(walkway_width_min, walkway_width_max)
        add_walkway(current_x, current_x + walkway_length, mid_y, walkway_width, current_height + walkway_height)

        # Set goals at each walkway
        goals[i + 2] = [current_x + walkway_length / 2, mid_y]
        
        current_x += walkway_length
        current_height += height_increase

    # Place the final goal at the end of the elevated walkway
    final_goal_x = min(m_to_idx(length) - 1, current_x)
    goals[-1] = [final_goal_x, mid_y]
  
    # Ensure the terrain is flat after the last obstacle, if there is remaining space
    if final_goal_x < m_to_idx(length):
        height_field[final_goal_x:, :] = 0

    return height_field, goals

def set_terrain_7(length, width, field_resolution, difficulty):
    """Series of narrow bridges for the robot to balance and walk across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up bridge dimensions
    bridge_length = 1.0 - 0.3 * difficulty
    bridge_length = m_to_idx(bridge_length)
    bridge_width = np.random.uniform(0.4, 0.6)
    bridge_width = m_to_idx(bridge_width)
    bridge_height_min, bridge_height_max = 0.1 + 0.2 * difficulty, 0.15 + 0.25 * difficulty
    gap_length = 0.1 + 0.7 * difficulty
    gap_length = m_to_idx(gap_length)

    perf_gap_length = 0.8  # Increased length gap to raise difficulty 

    mid_y = m_to_idx(width) // 2

    def add_bridge(start_x, end_x, mid_y):
        half_width = bridge_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        bridge_height = np.random.uniform(bridge_height_min, bridge_height_max)
        height_field[x1:x2, y1:y2] = bridge_height

    dx_min, dx_max = -0.05, 0.05  # Smaller randomness to prevent excessive overlap or gaps
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    for i in range(6):  # Set up 6 bridges
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_bridge(cur_x, cur_x + bridge_length + dx, mid_y + dy)

        # Put goal in the center of the bridge
        goals[i+1] = [cur_x + (bridge_length + dx) / 2, mid_y + dy]

        # Add a variable gap between bridges
        if random.random() < 0.5:
            gap_len = gap_length
        else:
            gap_len = m_to_idx(perf_gap_length)
        
        cur_x += bridge_length + dx + gap_len
    
    # Add final goal behind the last bridge, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_8(length, width, field_resolution, difficulty):
    """Narrow paths with varying elevations and slight curves for the robot to navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    path_width_min = 0.4
    path_width_max = 0.6 + 0.4 * difficulty
    path_height_min, path_height_max = 0.0, 0.20 + 0.20 * difficulty

    mid_y = m_to_idx(width) // 2
    cur_x = m_to_idx(2)  # Starting point for the first path segment

    def add_path_segment(start_x, end_x, width, height, mid_y):
        half_width = width // 2
        y1, y2 = mid_y - half_width, mid_y + half_width
        x1, x2 = start_x, end_x
        height_field[x1:x2, y1:y2] = height

    # Initialize the flat ground for the spawn area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    dx_min, dx_max = 1, 2
    dy_min, dy_max = -1, 1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    for i in range(7):  # Create 7 path segments for the robot to navigate
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        path_length = dx
        path_width = np.random.randint(m_to_idx(path_width_min), m_to_idx(path_width_max))
        path_height = np.random.uniform(path_height_min, path_height_max)

        add_path_segment(cur_x, cur_x + path_length, path_width, path_height, mid_y + dy)

        # Place the goals on the center position of each path segment
        goals[i+1] = [cur_x + path_length // 2, mid_y + dy]

        # Update the current position based on the path length and apply the small deviation
        cur_x += path_length

    # Add final goal after last path segment
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_9(length, width, field_resolution, difficulty):
    """Series of hurdles for the quadruped to jump over while navigating through the terrain."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up hurdle dimensions
    # Hurdle height increases with difficulty and their lengths are constant
    hurdle_height_min, hurdle_height_max = 0.1 * difficulty, 0.3 * difficulty
    hurdle_length = 0.4  # consistent short hurdles
    hurdle_length = m_to_idx(hurdle_length)
    hurdle_width = 3.5 / 2  # make the hurdle span the width of the course, minus small margins
    hurdle_width = m_to_idx(hurdle_width)

    mid_y = m_to_idx(width) // 2

    def add_hurdle(start_x, mid_y):
        half_width = hurdle_width // 2
        x = start_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        hurdle_height = np.random.uniform(hurdle_height_min, hurdle_height_max)
        height_field[x:x+hurdle_length, y1:y2] = hurdle_height

    dx_min, dx_max = 1.2, 1.5  # spacing between hurdles, to ensure there is enough room to jump
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(1.5)
    height_field[0:spawn_length, :] = 0
    # Set first goal at spawn area
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y] 
import numpy as np
import random

def set_terrain(terrain, variation, difficulty):
    terrain_fns = [
        set_terrain_0,
        set_terrain_1,
        set_terrain_2,
        set_terrain_3,
        set_terrain_4,
        set_terrain_5,
        set_terrain_6,
        set_terrain_7,
        set_terrain_8,
        set_terrain_9,
        # INSERT TERRAIN FUNCTIONS HERE
    ]
    idx = int(variation * len(terrain_fns))
    height_field, goals = terrain_fns[idx](terrain.width * terrain.horizontal_scale, terrain.length * terrain.horizontal_scale, terrain.horizontal_scale, difficulty)
    terrain.height_field_raw = (height_field / terrain.vertical_scale).astype(np.int16)
    terrain.goals = goals
    return idx

def set_terrain_0(length, width, field_resolution, difficulty):
    """Stepping stones terrain for the robot to navigate over discontinuous and varying height obstacles."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up stepping stones dimensions
    stone_length_min, stone_length_max = 0.4, 0.7  # Minimum and maximum size of stepping stones
    stone_width_min, stone_width_max = 0.4, 0.7  # Minimum and maximum width of stepping stones
    stone_height_min, stone_height_max = 0.1 * difficulty, 0.5 * difficulty  # Minimum and maximum height of stepping stones
    gap_length_min, gap_length_max = 0.4 + (1 - difficulty) * 0.1, 0.6 + (1 - difficulty) * 0.2  # Minimum and maximum gaps between stepping stones

    mid_y = m_to_idx(width) // 2

    def add_stone(center_x, center_y):
        half_length = m_to_idx(random.uniform(stone_length_min, stone_length_max) / 2)
        half_width = m_to_idx(random.uniform(stone_width_min, stone_width_max) / 2)
        height = random.uniform(stone_height_min, stone_height_max)
        x1, x2 = center_x - half_length, center_x + half_length
        y1, y2 = center_y - half_width, center_y + half_width
        height_field[x1:x2, y1:y2] = height

        return (x1 + x2) / 2, (y1 + y2) / 2  # Return center coordinates for goal placement

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at spawn

    # Create stepping stones with increasing complexity
    cur_x = spawn_length
    num_stones = 7  # Number of stepping stones to place
    cur_y = mid_y

    for i in range(num_stones):
        gap_length = m_to_idx(random.uniform(gap_length_min, gap_length_max))
        cur_x += gap_length

        # Randomly shift stone in y-direction for more challenge
        cur_y += m_to_idx(random.uniform(-0.5, 0.5))

        stone_center_x, stone_center_y = add_stone(cur_x, cur_y)
        
        goals[i+1] = [stone_center_x, stone_center_y]

    # Final goal at the end of the course
    goals[-1] = [m_to_idx(length) - m_to_idx(0.5), mid_y]

    return height_field, goals

def set_terrain_1(length, width, field_resolution, difficulty):
    """Elevated beams for the robot to balance on and navigate across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Beam dimensions
    beam_width = np.random.uniform(0.4, 0.6)
    beam_width_idx = m_to_idx(beam_width)
    beam_height_min = 0.1 * difficulty
    beam_height_max = 0.15 + 0.3 * difficulty
    beam_length = 1.5
    beam_length_idx = m_to_idx(beam_length)

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, mid_y):
        half_width = beam_width_idx // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        beam_height = np.random.uniform(beam_height_min, beam_height_max)
        height_field[x1:x2, y1:y2] = beam_height

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
    for i in range(6):  # Add 6 beams
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_beam(cur_x, cur_x + beam_length_idx + dx, mid_y + dy)

        # Put goal in the center of the beam
        goals[i+1] = [cur_x + (beam_length_idx + dx) / 2, mid_y + dy]

        # Add gap between beams
        gap_length = 0.2 + 0.5 * difficulty
        gap_length_idx = m_to_idx(gap_length)
        cur_x += beam_length_idx + dx + gap_length_idx
    
    # Add final goal after the last beam
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_2(length, width, field_resolution, difficulty):
    """Narrow and uneven stepping stones traversing the terrain for the robot to balance and navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up stepping stones dimensions
    stone_length = np.random.uniform(0.4, 0.6)
    stone_length = m_to_idx(stone_length)
    stone_width = np.random.uniform(0.4, 0.6)
    stone_width = m_to_idx(stone_width)

    stone_height_min, stone_height_max = 0.1 + 0.2 * difficulty, 0.15 + 0.3 * difficulty
    gap_length_min, gap_length_max = 0.4, 0.6
    gap_length_min = m_to_idx(gap_length_min)
    gap_length_max = m_to_idx(gap_length_max)

    mid_y = m_to_idx(width) // 2

    def add_stone(x, y, length, width, height):
        half_length = length // 2
        half_width = width // 2
        x1, x2 = x - half_length, x + half_length
        y1, y2 = y - half_width, y + half_width
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = 0.4, 0.6
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.1, 0.1
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(6):  # Set up 6 stepping stones in a straight line with gaps
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        stone_height = np.random.uniform(stone_height_min, stone_height_max)
        add_stone(cur_x + dx, mid_y + dy, stone_length, stone_width, stone_height)

        # Put goal in the center of the stone
        goals[i+1] = [cur_x + dx, mid_y + dy]

        # Add gap
        cur_x += stone_length + gap_length_max
    
    # Add final goal behind the last stone, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_3(length, width, field_resolution, difficulty):
    """A winding path of blocks for the robot to walk, jump, and navigate turns through."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Parameters
    block_length = m_to_idx(0.8 - 0.2 * difficulty)  # Block length decreases with difficulty
    block_width = m_to_idx(1.5 + 0.5 * difficulty)  # Block width increases with difficulty
    block_height = np.linspace(0.1, 0.4, num=8) * difficulty  # Block height varies with difficulty
    gap_length = m_to_idx(0.1 + 0.3 * difficulty)  # Gap length increases with difficulty

    spawn_length = m_to_idx(2)

    # Set spawn area to flat ground
    height_field[:spawn_length, :] = 0

    # Initialization
    mid_y = m_to_idx(width / 2)
    cur_x = spawn_length
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  # First goal at spawn

    # Winding path of blocks
    for i in range(7):
        # Choose a random offset within bounds for variety
        dy_min = -0.5 * difficulty
        dy_max = 0.5 * difficulty
        dy = np.random.uniform(dy_min, dy_max)
        cur_y = mid_y + m_to_idx(dy)

        # Ensure blocks fit within width bounds
        cur_y = max(block_width // 2, min(cur_y, m_to_idx(width) - block_width // 2))

        # Define block coordinates
        x1, x2 = cur_x, cur_x + block_length
        y1, y2 = cur_y - block_width // 2, cur_y + block_width // 2
        block_h = block_height[i % len(block_height)]

        # Place the block
        height_field[x1:x2, y1:y2] = block_h

        # Set the goal on the block
        goals[i + 1] = [(x1 + x2) // 2, (y1 + y2) // 2]

        # Add gap for next block
        cur_x += block_length + gap_length

    # Final goal after last block
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    # Put the remaining area to flat ground to end the course
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_4(length, width, field_resolution, difficulty):
    """Varied-height hurdles for the robot to navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Dimensions and characteristics of hurdles
    min_hurdle_height = 0.1  # Minimum hurdle height in meters
    max_hurdle_height = 0.4  # Maximum hurdle height in meters, scaled by difficulty
    hurdle_height_adjustment = difficulty * (max_hurdle_height - min_hurdle_height)
    hurdle_height_min, hurdle_height_max = min_hurdle_height, min_hurdle_height + hurdle_height_adjustment

    hurdle_length = 0.4  # Hurdle thickness in meters
    hurdle_length_quant = m_to_idx(hurdle_length)
    
    gap_min_length = 0.2  # Minimum gap in meters between hurdles
    gap_max_length = 1.0  # Maximum gap in meters between hurdles
    gap_length_adjustment = difficulty * (gap_max_length - gap_min_length)
    gap_length_min, gap_length_max = m_to_idx(gap_min_length), m_to_idx(gap_max_length)

    mid_y = m_to_idx(width / 2)

    def add_hurdle(start_x, hurdle_height):
        """Add a hurdle of a specified height to the height_field."""
        x1, x2 = start_x, start_x + hurdle_length_quant
        y1, y2 = mid_y - m_to_idx(0.5), mid_y + m_to_idx(0.5)
        height_field[x1:x2, y1:y2] = hurdle_height

    # Set the spawn area flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    for i in range(7):  # Create 7 varied-height hurdles for a total of 8 goals
        hurdle_height = np.random.uniform(hurdle_height_min, hurdle_height_max)
        add_hurdle(cur_x, hurdle_height)
        
        # Place the goal just ahead of the hurdle
        goals[i + 1] = [cur_x + m_to_idx(0.2), mid_y]
        
        # Calculate the gap for the next hurdle based on minimum and maximum gap lengths
        gap_length = np.random.randint(gap_length_min, gap_length_max)
        cur_x += hurdle_length_quant + gap_length

    return height_field, goals

def set_terrain_5(length, width, field_resolution, difficulty):
    """Varied height stepping stones and narrow bridges requiring precise balance and agility."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    mid_y = m_to_idx(width) // 2

    # Set up spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Place the first goal at the end of the spawn area
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    def add_stepping_stones(start_x, end_x, y, height, width):
        y1, y2 = y - width // 2, y + width // 2
        height_field[start_x:end_x, y1:y2] = height

    def add_narrow_bridge(start_x, end_x, y, height):
        y1, y2 = y - m_to_idx(0.2), y + m_to_idx(0.2)  # Narrow bridge, 0.4 meters wide
        height_field[start_x:end_x, y1:y2] = height

    current_x = spawn_length
    stone_height = np.random.uniform(0.1, 0.3) * difficulty  # Height varies with difficulty

    for i in range(3):
        stone_width = m_to_idx(1 + 0.2 * difficulty)
        stone_length = m_to_idx(0.5 + 0.3 * difficulty)
        gap_between_stones = m_to_idx(0.5 + 0.5 * difficulty)

        # Add first stepping stone
        add_stepping_stones(current_x, current_x + stone_length, mid_y, stone_height, stone_width)
        goals[i + 1] = [current_x + stone_length / 2, mid_y]
        current_x += stone_length + gap_between_stones

        # Add second stepping stone
        add_stepping_stones(current_x, current_x + stone_length, mid_y, stone_height, stone_width)
        goals[i + 2] = [current_x + stone_length / 2, mid_y]
        current_x += stone_length + gap_between_stones

        # Reset for next pair of stones
        stone_height = np.random.uniform(0.1, 0.3) * difficulty

    # Add narrow bridges
    for i in range(3, 6):
        bridge_length = m_to_idx(1.0 + 0.5 * difficulty)
        bridge_height = np.random.uniform(0.05, 0.2) * difficulty
        current_x += m_to_idx(0.5)  # Adding a small gap before the bridge
        add_narrow_bridge(current_x, current_x + bridge_length, mid_y, bridge_height)
        goals[i + 1] = [current_x + bridge_length / 2, mid_y]
        current_x += bridge_length + m_to_idx(0.5)  # Adding gap after the bridge

    # Final goal position after the last bridge
    current_x += m_to_idx(0.5)
    goals[-1] = [current_x, mid_y]

    return height_field, goals

def set_terrain_6(length, width, field_resolution, difficulty):
    """Series of steps and elevated walkways for climbing and balancing."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define obstacle specifications based on difficulty
    step_height_min, step_height_max = 0.1 * difficulty, 0.4 * difficulty
    walkway_height = 0.2 + 0.5 * difficulty
    walkway_width_min = 0.4  # minimum width, ensuring it is passable
    walkway_width_max = 1.0 + 0.5 * difficulty

    # Initialize terrain with flat ground for the spawning area
    spawn_length = m_to_idx(2.0)
    height_field[:spawn_length, :] = 0
    mid_y = m_to_idx(width) // 2

    # Set first goal at the end of the spawn area
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Define a helper function for adding a step
    def add_step(x_start, x_end, y_center, height):
        half_width = m_to_idx(walkway_width_max) // 2
        y_start = max(0, y_center - half_width)
        y_end = min(m_to_idx(width), y_center + half_width)
        height_field[x_start:x_end, y_start:y_end] = height

    # Define a helper function for adding a walkway
    def add_walkway(x_start, x_end, y_center, width, height):
        half_width = m_to_idx(width) // 2
        y_start = max(0, y_center - half_width)
        y_end = min(m_to_idx(width), y_center + half_width)
        height_field[x_start:x_end, y_start:y_end] = height

    current_x = spawn_length
    height_increase = (step_height_max - step_height_min) / 6
    current_height = step_height_min

    # Create 6 steps and elevated walkways
    for i in range(6):
        step_length = m_to_idx(0.6)
        add_step(current_x, current_x + step_length, mid_y, current_height)
        
        # Set goals at each step
        goals[i + 1] = [current_x + step_length / 2, mid_y]
        
        current_x += step_length

        walkway_length = m_to_idx(0.8)
        walkway_width = random.uniform(walkway_width_min, walkway_width_max)
        add_walkway(current_x, current_x + walkway_length, mid_y, walkway_width, current_height + walkway_height)

        # Set goals at each walkway
        goals[i + 2] = [current_x + walkway_length / 2, mid_y]
        
        current_x += walkway_length
        current_height += height_increase

    # Place the final goal at the end of the elevated walkway
    final_goal_x = min(m_to_idx(length) - 1, current_x)
    goals[-1] = [final_goal_x, mid_y]
  
    # Ensure the terrain is flat after the last obstacle, if there is remaining space
    if final_goal_x < m_to_idx(length):
        height_field[final_goal_x:, :] = 0

    return height_field, goals

def set_terrain_7(length, width, field_resolution, difficulty):
    """Series of narrow bridges for the robot to balance and walk across."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up bridge dimensions
    bridge_length = 1.0 - 0.3 * difficulty
    bridge_length = m_to_idx(bridge_length)
    bridge_width = np.random.uniform(0.4, 0.6)
    bridge_width = m_to_idx(bridge_width)
    bridge_height_min, bridge_height_max = 0.1 + 0.2 * difficulty, 0.15 + 0.25 * difficulty
    gap_length = 0.1 + 0.7 * difficulty
    gap_length = m_to_idx(gap_length)

    perf_gap_length = 0.8  # Increased length gap to raise difficulty 

    mid_y = m_to_idx(width) // 2

    def add_bridge(start_x, end_x, mid_y):
        half_width = bridge_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        bridge_height = np.random.uniform(bridge_height_min, bridge_height_max)
        height_field[x1:x2, y1:y2] = bridge_height

    dx_min, dx_max = -0.05, 0.05  # Smaller randomness to prevent excessive overlap or gaps
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    for i in range(6):  # Set up 6 bridges
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_bridge(cur_x, cur_x + bridge_length + dx, mid_y + dy)

        # Put goal in the center of the bridge
        goals[i+1] = [cur_x + (bridge_length + dx) / 2, mid_y + dy]

        # Add a variable gap between bridges
        if random.random() < 0.5:
            gap_len = gap_length
        else:
            gap_len = m_to_idx(perf_gap_length)
        
        cur_x += bridge_length + dx + gap_len
    
    # Add final goal behind the last bridge, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_8(length, width, field_resolution, difficulty):
    """Narrow paths with varying elevations and slight curves for the robot to navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    path_width_min = 0.4
    path_width_max = 0.6 + 0.4 * difficulty
    path_height_min, path_height_max = 0.0, 0.20 + 0.20 * difficulty

    mid_y = m_to_idx(width) // 2
    cur_x = m_to_idx(2)  # Starting point for the first path segment

    def add_path_segment(start_x, end_x, width, height, mid_y):
        half_width = width // 2
        y1, y2 = mid_y - half_width, mid_y + half_width
        x1, x2 = start_x, end_x
        height_field[x1:x2, y1:y2] = height

    # Initialize the flat ground for the spawn area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    dx_min, dx_max = 1, 2
    dy_min, dy_max = -1, 1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    for i in range(7):  # Create 7 path segments for the robot to navigate
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        path_length = dx
        path_width = np.random.randint(m_to_idx(path_width_min), m_to_idx(path_width_max))
        path_height = np.random.uniform(path_height_min, path_height_max)

        add_path_segment(cur_x, cur_x + path_length, path_width, path_height, mid_y + dy)

        # Place the goals on the center position of each path segment
        goals[i+1] = [cur_x + path_length // 2, mid_y + dy]

        # Update the current position based on the path length and apply the small deviation
        cur_x += path_length

    # Add final goal after last path segment
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_9(length, width, field_resolution, difficulty):
    """Series of hurdles for the quadruped to jump over while navigating through the terrain."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up hurdle dimensions
    # Hurdle height increases with difficulty and their lengths are constant
    hurdle_height_min, hurdle_height_max = 0.1 * difficulty, 0.3 * difficulty
    hurdle_length = 0.4  # consistent short hurdles
    hurdle_length = m_to_idx(hurdle_length)
    hurdle_width = 3.5 / 2  # make the hurdle span the width of the course, minus small margins
    hurdle_width = m_to_idx(hurdle_width)

    mid_y = m_to_idx(width) // 2

    def add_hurdle(start_x, mid_y):
        half_width = hurdle_width // 2
        x = start_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        hurdle_height = np.random.uniform(hurdle_height_min, hurdle_height_max)
        height_field[x:x+hurdle_length, y1:y2] = hurdle_height

    dx_min, dx_max = 1.2, 1.5  # spacing between hurdles, to ensure there is enough room to jump
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(1.5)
    height_field[0:spawn_length, :] = 0
    # Set first goal at spawn area
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    for i in range(6):  # Set up 6 hurdles along the path
        add_hurdle(cur_x, mid_y)

        # Put a goal right after each hurdle to force a straight-line progression
        goals[i+1] = [cur_x + hurdle_length + m_to_idx(0.2), mid_y]

        # Add spacing between hurdles
        cur_x += hurdle_length + np.random.randint(dx_min, dx_max)

    # Add the final goal at the end of the terrain
    final_gap = m_to_idx(0.5)
    goals[-1] = [cur_x + final_gap, mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

# INSERT TERRAIN FUNCTION DEFINITIONS HERE
 

    cur_x = spawn_length
    for i in range(6):  # Set up 6 hurdles along the path
        add_hurdle(cur_x, mid_y)

        # Put a goal right after each hurdle to force a straight-line progression
        goals[i+1] = [cur_x + hurdle_length + m_to_idx(0.2), mid_y]

        # Add spacing between hurdles
        cur_x += hurdle_length + np.random.randint(dx_min, dx_max)

    # Add the final goal at the end of the terrain
    final_gap = m_to_idx(0.5)
    goals[-1] = [cur_x + final_gap, mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

# INSERT TERRAIN FUNCTION DEFINITIONS HERE
