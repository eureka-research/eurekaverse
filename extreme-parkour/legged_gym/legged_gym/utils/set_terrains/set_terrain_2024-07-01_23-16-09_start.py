
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
    """A series of hurdles of varying heights for the robot to jump over and navigate around."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Helper function to add a hurdle
    def add_hurdle(start_x, start_y, length, width, height):
        x1, x2 = start_x, start_x + length
        y1, y2 = start_y, start_y + width
        height_field[x1:x2, y1:y2] = height

    # Dimensions and attributes for hurdles based on difficulty
    hurdle_height_min = 0.1 + 0.2 * difficulty
    hurdle_height_max = 0.2 + 0.3 * difficulty
    hurdle_length = m_to_idx(0.3 + 0.2 * difficulty)
    hurdle_width = m_to_idx(1.0)

    mid_y = m_to_idx(width) // 2

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    hurdle_spacing = m_to_idx(0.8 + 0.4 * difficulty)
    for i in range(6):  # Set up 6 hurdles
        hurdle_height = np.random.uniform(hurdle_height_min, hurdle_height_max)
        add_hurdle(cur_x, mid_y - hurdle_width // 2, hurdle_length, hurdle_width, hurdle_height)

        # Place a goal just after each hurdle
        goals[i+1] = [cur_x + hurdle_length / 2, mid_y]

        # Move to the next position
        cur_x += hurdle_length + hurdle_spacing
    
    # Add the final 7th and 8th goals after the last hurdle
    goals[7] = [cur_x + m_to_idx(0.5), mid_y]

    return height_field, goals


def set_terrain_1(length, width, field_resolution, difficulty):
    """Robot traverses a series of staggered, narrow beams requiring balance and precision."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Beam dimensions
    beam_length = 1.0 - 0.3 * difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = 0.4 + 0.2 * difficulty
    beam_width = m_to_idx(beam_width)
    beam_height_min, beam_height_max = 0.1 + 0.3 * difficulty, 0.3 + 0.4 * difficulty
    gap_length = 0.2 + 0.5 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, y_pos):
        x1, x2 = start_x, end_x
        y1, y2 = y_pos - beam_width // 2, y_pos + beam_width // 2
        beam_height = np.random.uniform(beam_height_min, beam_height_max)
        height_field[x1:x2, y1:y2] = beam_height

    dy_range = [-0.8, 0.8]
    dy_min, dy_max = m_to_idx(dy_range[0]), m_to_idx(dy_range[1])

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Add beams in a staggered manner
    cur_x = spawn_length
    for i in range(7):  # Set up 7 beams
        dx = random.randint(0, beam_length)
        dy = random.randint(dy_min, dy_max)
        add_beam(cur_x, cur_x + beam_length + dx, mid_y + dy)

        # Put goal in the center of the beam
        goals[i + 1] = [cur_x + (beam_length + dx) // 2, mid_y + dy]

        # Add gap
        cur_x += beam_length + dx + gap_length

    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_2(length, width, field_resolution, difficulty):
    """Series of hurdles and narrow pathways for the robot to navigate and jump over."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up hurdle dimensions
    hurdle_height_min = 0.2 * difficulty
    hurdle_height_max = 0.5 * difficulty
    hurdle_width_min = m_to_idx(0.4)  # narrowest possible width
    hurdle_width_max = m_to_idx(1.0)  # widest possible width

    # Pathway dimensions
    pathway_width_min = m_to_idx(0.4)
    pathway_width_max = m_to_idx(1.0)

    def add_hurdle(start_x, end_x, mid_y):
        half_width = np.random.randint(hurdle_width_min, hurdle_width_max) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        hurdle_height = np.random.uniform(hurdle_height_min, hurdle_height_max)
        height_field[x1:x2, y1:y2] = hurdle_height

    def add_pathway(start_x, end_x, mid_y):
        half_width = np.random.randint(pathway_width_min, pathway_width_max) // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        pathway_height = 0
        height_field[x1:x2, y1:y2] = pathway_height

    mid_y = m_to_idx(width) // 2

    dx_min, dx_max = m_to_idx(0.5), m_to_idx(1.5)
    dy_min, dy_max = m_to_idx(-0.5), m_to_idx(0.5)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    is_hurdle = True  # Start with hurdle

    for i in range(6):  # Create a mix of 6 hurdles and pathways
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        
        if is_hurdle:
            add_hurdle(cur_x, cur_x + dx, mid_y + dy)
            # Place goal after the hurdle
            goals[i+1] = [cur_x + dx / 2, mid_y + dy]
        else:
            add_pathway(cur_x, cur_x + dx, mid_y + dy)
            # Place goal in the middle of the path
            goals[i+1] = [cur_x + dx / 2, mid_y + dy]

        is_hurdle = not is_hurdle
        cur_x += dx
    
    # Add final goal at the end
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    
    # Make sure the end of the course is flat ground for the final goal
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_3(length, width, field_resolution, difficulty):
    """Narrow passages with sharp turns to test navigation and turning skills."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))
    
    # Define the dimensions for the narrow passages
    passage_width_min = 0.4  # Narrow but passable
    passage_width_max = 0.6  # Some variability gives more challenge
    alley_length = 1.5  # Average length of each passage segment
    alley_length = m_to_idx(alley_length)
    passage_width_min = m_to_idx(passage_width_min)
    passage_width_max = m_to_idx(passage_width_max)
    
    # Set starting area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    
    # First goal at the start point
    goals[0] = [spawn_length - m_to_idx(0.5), m_to_idx(width) // 2]
    
    cur_x = spawn_length
    cur_y = m_to_idx(width) // 2
    
    def add_alley(x, y, length, width, direction):
        """Add lateral or vertical alley starting from x, y position."""
        if direction == 'horizontal':
            y1, y2 = y - width // 2, y + width // 2
            height_field[x:x+length, y1:y2] = 0.05 * difficulty  # add very small height for boundaries
        else:  # vertical
            x1, x2 = x - width // 2, x + width // 2
            height_field[x1:x2, y:y+length] = 0.05 * difficulty  # add very small height for boundaries

    for i in range(7):  # 7 passages
        passage_width = random.randint(passage_width_min, passage_width_max)
        direction = 'horizontal' if i % 2 == 0 else 'vertical'
        
        if direction == 'horizontal':
            add_alley(cur_x, cur_y, alley_length, passage_width, direction)
            goals[i+1] = [cur_x + alley_length // 2, cur_y]
            cur_x += alley_length  # move right for the next segment
        else:
            add_alley(cur_x, cur_y, alley_length, passage_width, direction)
            goals[i+1] = [cur_x, cur_y + alley_length // 2]
            cur_y += alley_length  # move up for the next segment
    
    # Final goal behind the last alley segment
    final_segment_length = m_to_idx(12) - cur_x
    height_field[cur_x:cur_x + final_segment_length, :] = 0
    goals[-1] = [cur_x + final_segment_length - m_to_idx(0.5), cur_y]
    
    return height_field, goals

def set_terrain_4(length, width, field_resolution, difficulty):
    """
    Series of narrow bridges and a balancing beam that the quadruped must navigate.
    """

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Terrain parameters
    bridge_length = 1.5 - 0.8 * difficulty
    bridge_length = m_to_idx(bridge_length)
    bridge_width = 0.4 + 0.2 * difficulty
    bridge_width = m_to_idx(bridge_width)
    balance_beam_length = 2.0 - 1.0 * difficulty
    balance_beam_length = m_to_idx(balance_beam_length)
    balance_beam_width = 0.4
    balance_beam_width = m_to_idx(balance_beam_width)
    
    bridge_height = 0.15 + 0.3 * difficulty
    gap_length = 0.2 + 0.6 * difficulty
    gap_length = m_to_idx(gap_length)

    mid_y = m_to_idx(width) // 2

    def add_bridge(start_x, end_x, mid_y, bridge_height, width):
        half_width = width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = bridge_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]  

    cur_x = spawn_length
    bridge_count = 4

    for i in range(bridge_count):  # Set up 4 bridges
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        add_bridge(cur_x, cur_x + bridge_length + dx, mid_y + dy, bridge_height, bridge_width)

        # Put goal in the center of the bridge
        goals[i+1] = [cur_x + (bridge_length + dx) / 2, mid_y + dy]

        # Add gap
        cur_x += bridge_length + dx + gap_length
    
    # Add a balancing beam at the end
    cur_x += gap_length
    add_bridge(cur_x, cur_x + balance_beam_length, mid_y, bridge_height, balance_beam_width)
    goals[bridge_count + 1] = [cur_x + balance_beam_length / 2, mid_y]

    # Add final flat ground after the beam
    cur_x += balance_beam_length
    height_field[cur_x:, :] = 0
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]

    # Fill remaining goals with valid default 
    for i in range(bridge_count + 2, 8):
        goals[i] = [cur_x + m_to_idx(1), mid_y]

    return height_field, goals

def set_terrain_5(length, width, field_resolution, difficulty):
    """Narrow beams at varying heights that challenge the robot's balance and jumping ability."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Set up beam dimensions
    beam_length = 0.6 * (1 + difficulty)  # Beams get longer with difficulty
    beam_length = m_to_idx(beam_length)
    beam_width = 0.4 if difficulty < 0.5 else 0.3  # Narrower beams at higher difficulty
    beam_width = m_to_idx(beam_width)
    mid_y = m_to_idx(width) // 2

    def add_beam(start_x, end_x, mid_y, height):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_width, mid_y + half_width
        height_field[x1:x2, y1:y2] = height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.4, 0.4
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Heights of beams will vary
    height_min = 0.2 * difficulty
    height_max = 0.6 * difficulty

    cur_x = spawn_length

    for i in range(6):
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        beam_height = np.random.uniform(height_min, height_max)
        add_beam(cur_x, cur_x + beam_length + dx, mid_y + dy, beam_height)

        # Put goal in the center of the beam
        goals[i+1] = [cur_x + (beam_length + dx) / 2, mid_y + dy]

        # Add gap
        gap_length = 0.4 + 0.3 * difficulty
        gap_length = m_to_idx(gap_length)
        cur_x += beam_length + dx + gap_length
    
    # Add final goal behind the last beam, fill in the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_6(length, width, field_resolution, difficulty):
    """Stepping stones followed by narrow balance beams for the robot to navigate."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Spacing and dimensions
    stone_diameter = 0.6 - 0.2 * difficulty  # Smaller stones for higher difficulty
    stone_diameter = m_to_idx(stone_diameter)
    stone_height = 0.05 + 0.25 * difficulty  # Taller stones for higher difficulty
    beam_width = 0.4  # Narrow balance beam
    beam_width = m_to_idx(beam_width)
    beam_height = 0.2 + 0.3 * difficulty  # Taller for higher difficulty
    step_distance = 0.4 + 0.6 * difficulty  # Longer distances for higher difficulty
    step_distance = m_to_idx(step_distance)
    
    mid_y = m_to_idx(width) // 2

    def add_stepping_stone(center_x, center_y):
        x1, x2 = center_x - stone_diameter // 2, center_x + stone_diameter // 2
        y1, y2 = center_y - stone_diameter // 2, center_y + stone_diameter // 2
        height_field[x1:x2 + 1, y1:y2 + 1] = stone_height

    def add_balance_beam(start_x, end_x, center_y):
        half_width = beam_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = center_y - half_width, center_y + half_width
        height_field[x1:x2 + 1, y1:y2 + 1] = beam_height

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    # Stage: Stepping stones
    cur_x = spawn_length + m_to_idx(0.5)
    for i in range(3):  # 3 stepping stones
        cur_y = mid_y + np.random.randint(-m_to_idx(0.5), m_to_idx(0.5))
        add_stepping_stone(cur_x, cur_y)
        goals[i + 1] = [cur_x, cur_y]
        cur_x += stone_diameter + step_distance

    # Stage: Balance beams
    for i in range(4):
        start_x = cur_x
        end_x = cur_x + m_to_idx(1.5)  # Length of balance beam
        cur_y = mid_y + np.random.randint(-m_to_idx(0.5), m_to_idx(0.5))
        add_balance_beam(start_x, end_x, cur_y)
        goals[i + 4] = [start_x + m_to_idx(0.75), cur_y]
        cur_x = end_x + step_distance

    # Add final goal behind the last obstacle
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_7(length, width, field_resolution, difficulty):
    """Stepping stones and a narrow bridge for quadruped balance and precision."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define the stepping stone parameters
    stone_diameter = 0.4 + 0.3 * difficulty  # Steps get larger as difficulty increases
    stone_gap = 0.3 + 0.5 * difficulty  # Gaps also increase with difficulty
    stone_height_min, stone_height_max = 0.1, 0.2  # Heights remain same for balance precision
    
    stone_diameter = m_to_idx(stone_diameter)
    stone_gap = m_to_idx(stone_gap)
    mid_y = m_to_idx(width) // 2

    def add_stone(center_x, center_y):
        half_dia = stone_diameter // 2
        x1, x2 = center_x - half_dia, center_x + half_dia
        y1, y2 = center_y - half_dia, center_y + half_dia
        stone_height = np.random.uniform(stone_height_min, stone_height_max)
        height_field[x1:x2, y1:y2] = stone_height

    dx_min, dx_max = -0.1, 0.1
    dx_min, dx_max = m_to_idx(dx_min), m_to_idx(dx_max)
    dy_min, dy_max = -0.2, 0.2
    dy_min, dy_max = m_to_idx(dy_min), m_to_idx(dy_max)

    # Set spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length

    # Add stepping stones
    for i in range(4):  # Create 4 stepping stones
        dx = np.random.randint(dx_min, dx_max)
        dy = np.random.randint(dy_min, dy_max)
        cur_x += stone_gap
        add_stone(cur_x + dx, mid_y + dy)

        # Center goal on top of each stepping stone
        goals[i + 1] = [cur_x + dx, mid_y + dy]

        cur_x += stone_diameter

    # Define parameters for the narrow bridge
    bridge_length = 3
    bridge_length = m_to_idx(bridge_length)
    bridge_width = 0.4  # A narrow bridge
    bridge_width = m_to_idx(bridge_width)

    def add_bridge(start_x, end_x, center_y):
        half_width = bridge_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = center_y - half_width, center_y + half_width
        bridge_height = 0.15 
        height_field[x1:x2, y1:y2] = bridge_height

    # Position the bridge after the stepping stones
    cur_x += stone_gap
    add_bridge(cur_x, cur_x + bridge_length, mid_y)

    # Set goals along the narrow bridge
    goals[5] = [cur_x + bridge_length * 0.25, mid_y]
    goals[6] = [cur_x + bridge_length * 0.75, mid_y]

    # Add final goal behind the bridge
    cur_x += bridge_length
    goals[7] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, :] = 0

    return height_field, goals

def set_terrain_8(length, width, field_resolution, difficulty):
    """Walled corridors requiring precision in navigation and turning."""

    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    wall_height_min, wall_height_max = 0.2 * difficulty, 0.5 * difficulty + 0.2
    corridor_width = 0.4 + 0.4 * (1 - difficulty)
    corridor_width = m_to_idx(corridor_width)

    def add_walls(start_x, end_x, start_y, end_y):
        """Add walls around the corridor area defined by start and end points."""
        wall_height = np.random.uniform(wall_height_min, wall_height_max)
        height_field[start_x:end_x, start_y:start_y + 1] = wall_height
        height_field[start_x:end_x, end_y:end_y + 1] = wall_height

    # Convert spawn area to flat ground
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # Set first goal at the spawn area
    mid_y = m_to_idx(width) // 2
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]

    cur_x = spawn_length
    cur_y = mid_y

    for i in range(7):  # Set up 7 corridors with turns
        dx = m_to_idx(1.5 + 2.0 * random.random())  # 1.5 to 3.5 meters
        dy = m_to_idx(0.4 * (np.random.randint(0, 3) - 1))  # {-0.4, 0, 0.4} meters

        add_walls(cur_x, cur_x + dx, cur_y - corridor_width // 2, cur_y + corridor_width // 2)
        
        cur_x += dx
        cur_y += dy

        # Ensure x and y are within bounds
        cur_x = min(cur_x, m_to_idx(length) - 1)
        cur_y = min(max(cur_y, corridor_width // 2), m_to_idx(width) - corridor_width // 2 - 1)

        goals[i + 1] = [cur_x, cur_y]

    # Fill in the goal area to flat ground
    end_length = min(m_to_idx(2), m_to_idx(length) - cur_x)
    height_field[cur_x:cur_x + end_length, :] = 0
    goals[-1] = [cur_x + end_length - m_to_idx(0.5), cur_y]

    return height_field, goals

def set_terrain_9(length, width, field_resolution, difficulty):
    """Urban exploration course with stepping stones, narrow paths, and inclines."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    mid_y = m_to_idx(width / 2)

    # Parameters based on difficulty
    stepping_stone_size = m_to_idx(0.3 - 0.1 * difficulty)
    stepping_stone_height = np.random.uniform(0.05, 0.15) * difficulty
    path_width = m_to_idx(1.0 - 0.4 * difficulty)
    incline_height = np.random.uniform(0.1, 0.3) * difficulty

    def add_stepping_stone(x, y, size, height):
        """Adds a stepping stone at (x, y) with determined size and height."""
        height_field[x:x+size, y:y+size] = height

    def add_narrow_path(start_x, end_x, y, width):
        """Adds a narrow path from start_x to end_x centered at y with given width."""
        half_width = width // 2
        height_field[start_x:end_x, y-half_width:y+half_width] = 0.05 * difficulty

    def add_incline(start_x, end_x, y, width, height):
        """Adds an incline from start_x to end_x centered at y with given width and height."""
        half_width = width // 2
        height_field[start_x:end_x, y-half_width:y+half_width] = np.linspace(0, height, end_x - start_x).reshape(-1, 1)

    # Set spawn area
    spawn_length = m_to_idx(2)
    height_field[0:spawn_length, :] = 0

    # First goal at spawning point
    goals[0] = [spawn_length - 1, mid_y]

    # Stepping Stones Section
    for i in range(3):
        x = spawn_length + i * m_to_idx(0.6 + 0.4 * difficulty)
        y = mid_y + m_to_idx(random.uniform(-0.4, 0.4))
        add_stepping_stone(x, y, stepping_stone_size, stepping_stone_height)
        goals[i+1] = [x + stepping_stone_size//2, y + stepping_stone_size//2]

    # Narrow Path Section
    last_stone_x = spawn_length + 3 * m_to_idx(0.6 + 0.4 * difficulty)
    path_start_x = last_stone_x + m_to_idx(0.5)
    path_end_x = path_start_x + m_to_idx(2.5)
    add_narrow_path(path_start_x, path_end_x, mid_y, path_width)
    goals[4] = [(path_start_x + path_end_x) // 2, mid_y]

    # Incline Section
    incline_start_x = path_end_x + m_to_idx(0.5)
    incline_end_x = incline_start_x + m_to_idx(2)
    add_incline(incline_start_x, incline_end_x, mid_y, path_width, incline_height)
    goals[5] = [(incline_start_x + incline_end_x) // 2, mid_y]

    # Final goal
    final_x = incline_end_x + m_to_idx(1)
    goals[6] = [final_x - 1, mid_y]
    goals[7] = [final_x, mid_y]

    # Ensure the final area is flat to provide a stop point
    height_field[incline_end_x:final_x + spawn_length, :] = 0

    return height_field, goals

# INSERT TERRAIN FUNCTION DEFINITIONS HERE