
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
    """Renders the simulation setup, used to visulize terrain and robot."""

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
        # summary_imgs = []
        # seen_terrains = set()
        # for i, img in enumerate(imgs):
        #     terrain_class = env.env_class[i].cpu().item()
        #     terrain_level = env.terrain_levels[i].cpu().item()
        #     if terrain_class in seen_terrains or terrain_level != int((env_cfg.terrain.num_rows-1) / 2):
        #         continue
        #     seen_terrains.add(terrain_class)
        #     summary_imgs.append(img)

        # summary_img = create_grid_image(summary_imgs)
        # summary_img = Image.fromarray(summary_img)
        # summary_img_filename = "summary.png" if viewpoint_name == "main" else f"summary_{viewpoint_name}.png"
        # summary_img.save(save_dir / summary_img_filename)

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
            # difficulty = terrain_level / (env_cfg.terrain.num_rows-1) if env_cfg.terrain.num_rows > 1 else 0.5  # From terrain_gpt.py

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

        # summary_img = create_grid_image(summary_imgs)
        # summary_img = Image.fromarray(summary_img)
        # summary_img_filename = "summary.png" if viewpoint_name == "main" else f"summary_{viewpoint_name}.png"
        # summary_img.save(save_dir / summary_img_filename)

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

        # images_per_row = {}  # Maps terrain class and environment index to list of images and difficulty
        # if args.save_all_imgs:
        #     save_envs_subdir = save_dir / ("env_renders" if viewpoint_name == "main" else f"env_renders_{viewpoint_name}")
        #     save_envs_subdir.mkdir(parents=True)
        # for env_id, img in enumerate(imgs):
            # terrain_class = env.env_class[env_id].cpu().item()
            # terrain_type = env.terrain_types[env_id].cpu().item()
            # terrain_level = env.terrain_levels[env_id].cpu().item()
            # difficulty = terrain_level / (env_cfg.terrain.num_rows-1) if env_cfg.terrain.num_rows > 1 else 0.5  # From terrain_gpt.py

            # if terrain_class not in images_per_row:
            #     images_per_row[terrain_class] = {}
            # if terrain_type not in images_per_row[terrain_class]:
            #     images_per_row[terrain_class][terrain_type] = []
            # images_per_row[terrain_class][terrain_type].append((difficulty, img))

        #     if args.save_all_imgs:
        #         img = Image.fromarray(img)
        #         terrain_filename = f"terrain-{terrain_class}_difficulty-{difficulty:.1f}.png"
        #         env_filename = f"env-{env_id}_terrain-{terrain_class}_difficulty-{difficulty:.1f}.png"
        #         img.save(save_terrains_subdir / terrain_filename)
        #         img.save(save_envs_subdir / env_filename)
            
        # for terrain_class in images_per_row.keys():
        #     for terrain_type in images_per_row[terrain_class].keys():
        #         images_per_row[terrain_class][terrain_type] = [x[1] for x in sorted(images_per_row[terrain_class][terrain_type], key=lambda x: x[0])]

        # for terrain_class in images_per_row.keys():
        #     terrain_type = next(iter(images_per_row[terrain_class].keys()))  # Get any env to represent this terrain class
        #     frames = []
        #     for img in images_per_row[terrain_class][terrain_type]:
        #         frames.extend([img] * int(1 / gif_fps))
        #     imageio.mimsave(save_terrains_subdir / f"rendered_{terrain_class}.gif", frames, duration = len(images_per_row[terrain_class][terrain_type]))

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
    
    import socket
    if socket.gethostname() == "sn4622125587":
        # On exx, graphics only works on cuda:0
        print("Detected exx, overriding device to cuda:0")
        args.device = "cuda:0"

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
