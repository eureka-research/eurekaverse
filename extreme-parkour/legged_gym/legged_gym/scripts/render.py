
import numpy as np
import os
from datetime import datetime
import argparse
from pathlib import Path
from PIL import Image
import shutil

from legged_gym.envs import *
from legged_gym.utils import task_registry, add_shared_args, process_args
import imageio
import copy

file_dir = os.path.dirname(os.path.abspath(__file__))  # Location of this file
gif_fps = 1 / 100

def create_grid_image(images):
    """Combine multiple images into one grid."""
    grid_len = int(np.ceil(np.sqrt(len(images))))
    grid_height, grid_width = grid_len, grid_len
    grid_width = grid_len - (grid_len ** 2 - len(images)) // grid_len

    image_height, image_width, image_channels = images[0].shape
    combined_height = image_height * grid_height
    combined_width = image_width * grid_width

    grid_image = np.ones((combined_height, combined_width, image_channels), dtype=np.uint8) * 255
    for i, img in enumerate(images):
        img = copy.deepcopy(img)
        img[:, 0], img[:, -1], img[0, :], img[-1, :] = 255, 255, 255, 255  # Add white border
        row, col = i // grid_width, i % grid_width
        grid_image[row * image_height:(row + 1) * image_height, col * image_width:(col + 1) * image_width, :] = img

    return grid_image

def render(args):
    """Renders the simulation setup, used to visualize terrain and robot."""

    env_cfg, _ = task_registry.get_cfgs(name=args.task)
    env_cfg.env.render_envs = True

    env, env_cfg = task_registry.make_env(name=args.task, args=args, env_cfg=env_cfg)
    env_imgs = env.render_envs()

    save_dir = Path(args.save_dir)
    if save_dir.exists():
        # To avoid confusion, delete the directory if it already exists
        print(f"Directory {save_dir} already exists, overwriting...")
        shutil.rmtree(save_dir)
    save_dir.mkdir(parents=True)
    for viewpoint_name, imgs in env_imgs.items():
        # Create summary picture out of the average difficulty of each terrain
        # NOTE: Terrain class indentifies the function used to generate it (the idx returned by set_terrain()), terrain type is the specific instance of that class (the row in the grid)

        seen_classes = set()
        imgs_per_class_level = {}  # Used to construct per-class gif
        imgs_per_level_class = {}  # Used ot construct summary gif
        for env_id, img in enumerate(imgs):
            terrain_class = env.env_class[env_id].cpu().item()
            if terrain_class in seen_classes:
                # There can be multiple terrain types per class, we only want to show one
                continue
            terrain_level = env.terrain_levels[env_id].cpu().item()

            if terrain_class not in imgs_per_class_level:
                imgs_per_class_level[terrain_class] = {}
            imgs_per_class_level[terrain_class][terrain_level] = img

            if terrain_level not in imgs_per_level_class:
                imgs_per_level_class[terrain_level] = {}
            imgs_per_level_class[terrain_level][terrain_class] = img
        mid_terrain_level = int((env_cfg.terrain.num_rows-1) / 2)
        
        # Construct summary image and gif
        summary_frames = []
        summary_filename = "summary" if viewpoint_name == "main" else f"summary_{viewpoint_name}"
        for terrain_level in imgs_per_level_class.keys():
            imgs = [imgs_per_level_class[terrain_level][terrain_class] for terrain_class in sorted(imgs_per_level_class[terrain_level].keys())]
            summary_img = create_grid_image(imgs)
            summary_frames.extend([summary_img] * int(1 / gif_fps))
            if terrain_level == mid_terrain_level:
                summary_img = Image.fromarray(summary_img)
                summary_img.save(save_dir / f"{summary_filename}.png")
        imageio.mimsave(save_dir / f"{summary_filename}.gif", summary_frames, duration = int(len(summary_frames) * gif_fps))

        # Construct per-class image and gif
        if args.save_everything:
            save_terrains_subdir = save_dir / ("terrain_classes" if viewpoint_name == "main" else f"terrain_classes_{viewpoint_name}")
            save_terrains_subdir.mkdir(parents=True)
            for terrain_class in imgs_per_class_level.keys():
                imgs = [imgs_per_class_level[terrain_class][terrain_level] for terrain_level in sorted(imgs_per_class_level[terrain_class].keys())]
                frames = []
                for terrain_level in sorted(imgs_per_class_level[terrain_class].keys()):
                    img = imgs_per_class_level[terrain_class][terrain_level]
                    frames.extend([img] * int(1 / gif_fps))
                    if terrain_level == mid_terrain_level:
                        img = Image.fromarray(img)
                        img.save(save_terrains_subdir / f"terrain_{terrain_class}.png")
                imageio.mimsave(save_terrains_subdir / f"terrain_{terrain_class}.gif", frames, duration = int(len(frames) * gif_fps))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    add_shared_args(parser)

    parser.add_argument("--save_dir", type=str, required=True, help="Directory to save the rendered images")
    parser.add_argument("--save_everything", action="store_true", default=False, help="Save everything instead of only summary")

    args = parser.parse_args()
    args = process_args(args)
    if not args.headless:
        print("Setting headless to True, overriding")
        args.headless = True

    # Setting up exactly one env per terrain grid cell
    env_cfg, _ = task_registry.get_cfgs(name=args.task)
    if args.terrain_rows is None:
        print("Setting terrain_rows to 1 as default")
        args.terrain_rows = 1
    if args.terrain_cols is None:
        args.terrain_cols = env_cfg.terrain.num_cols
    if args.num_envs is None:
        args.num_envs = args.terrain_rows * args.terrain_cols
    # Disable the curriculum to assign robots evenly across terrain types and difficulties
    env_cfg.terrain.curriculum = False
    
    assert args.num_envs <= 100, "Too many environments to render, this will cause CPU soft lockup!"

    args.script = "render"
    render(args)
