
import numpy as np
import random
from isaacgym import terrain_utils

def set_terrain(terrain, variation, difficulty):
    return make_terrain(terrain, variation, difficulty)

def make_terrain(terrain, choice, difficulty):
    terrain.goals = np.zeros((8, 2))
    terrain.goals[:, 0] = np.linspace(50, terrain.width - 50, 8)
    terrain.goals[:, 1] = terrain.length // 2
    terrain.goals *= terrain.horizontal_scale

    def add_noise():
        noise = random.uniform(0.02, 0.04)
        terrain_utils.random_uniform_terrain(terrain, min_height=-noise, max_height=noise, step=0.005, downsampled_scale=0.075)

    if choice < 1/5:
        slope = difficulty * 0.2
        terrain_utils.pyramid_sloped_terrain(terrain, slope=slope)
        add_noise()
        return 0
    elif choice < 2/5:
        amplitude = 0.5 * difficulty
        terrain_utils.wave_terrain(terrain, num_waves=1, amplitude=amplitude)
        add_noise()
        return 1
    elif choice < 3/5:
        step_height = 0.02 + 0.14 * difficulty
        terrain_utils.stairs_terrain(terrain, step_width=1., step_height=step_height)
        add_noise()
        return 2
    elif choice < 4/5:
        discrete_obstacles_height = 0.03 + difficulty * 0.20
        num_rectangles = 20
        rectangle_min_size = 0.5
        rectangle_max_size = 2.
        terrain_utils.discrete_obstacles_terrain(terrain, discrete_obstacles_height, rectangle_min_size, rectangle_max_size, num_rectangles, platform_size=3.)
        add_noise()
        return 3
    else:
        slope = difficulty * 0.2
        terrain_utils.sloped_terrain(terrain, slope=slope)
        add_noise()
        return 4

