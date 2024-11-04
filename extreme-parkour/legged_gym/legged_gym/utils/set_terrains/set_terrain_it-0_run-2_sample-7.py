import numpy as np
import random

def set_terrain(length, width, field_resolution, difficulty):
    """Low-clearance tunnels for the quadruped to navigate through."""
    
    def m_to_idx(m):
        """Converts meters to quantized indices."""
        return np.round(m / field_resolution).astype(np.int16) if not (isinstance(m, list) or isinstance(m, tuple)) else [round(i / field_resolution) for i in m]

    height_field = np.zeros((m_to_idx(length), m_to_idx(width)))
    goals = np.zeros((8, 2))

    # Define tunnel parameters
    tunnel_height = m_to_idx(0.4 * (1 - difficulty))  # Tunnel clearance
    tunnel_width = m_to_idx(1.0 + difficulty)  # Tunnel width flexible with difficulty
    tunnel_length = m_to_idx(1.5 + 0.5 * difficulty)  # Tunnel length
    wall_height = tunnel_height * 2
    
    mid_y = m_to_idx(width) // 2
    spawn_length = m_to_idx(2)
    
    def add_tunnel(start_x, end_x, mid_y):
        half_tunnel_width = tunnel_width // 2
        x1, x2 = start_x, end_x
        y1, y2 = mid_y - half_tunnel_width, mid_y + half_tunnel_width
        
        # Raise the ground outside the tunnel area
        height_field[x1:x2, :y1] = wall_height
        height_field[x1:x2, y2:] = wall_height

    # Set spawn area to flat ground
    height_field[0:spawn_length, :] = 0
    # Put first goal at spawn
    goals[0] = [spawn_length - m_to_idx(0.5), mid_y]
    
    cur_x = spawn_length

    for i in range(6):  # Six tunnels
        dx = m_to_idx(0.3 + 0.4 * difficulty)  # Spacing between tunnels
        add_tunnel(cur_x, cur_x + tunnel_length, mid_y)

        # Set goal in the center of the tunnel
        goals[i+1] = [cur_x + (tunnel_length / 2), mid_y]

        # Move to next starting position
        cur_x += tunnel_length + dx

    # Add final goal beyond the last tunnel, fill the remaining gap
    goals[-1] = [cur_x + m_to_idx(0.5), mid_y]
    height_field[cur_x:, mid_y - tunnel_width//2 : mid_y + tunnel_width//2] = 0

    return height_field, goals