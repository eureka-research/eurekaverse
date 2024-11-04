import matplotlib.pyplot as plt
import argparse
from pathlib import Path
import os
from legged_gym import LEGGED_GYM_ROOT_DIR
import numpy as np
import matplotlib.animation as animation

def plot_depth(args):
    load_dir = Path(LEGGED_GYM_ROOT_DIR) / "logs" / args.proj_name / args.exptid / "depth_images"
    depth_min, depth_max = 0, 0
    frames = []
    for root, dirs, files in os.walk(load_dir, topdown=False):
        for name in files:
            image = np.load(os.path.join(root, name))
            if len(image.shape) >= 3:
                image = image[-2:]
            depth_min = min(depth_min, np.min(image))
            depth_max = max(depth_max, np.max(image))
            frames.append(image)
    print(f"Frame count: {len(frames)}")
    frames = np.stack(frames)
    print(frames.shape)
    fig, ax = plt.subplots()

    # Create an image plot object, initialized with the first frame
    im = ax.imshow(frames[0], cmap='inferno', vmin=-1, vmax=1)

    # Update function for the animation
    def update(frame):
        im.set_array(frame)
        return [im]

    # Create the animation
    ani = animation.FuncAnimation(fig, update, frames=frames, blit=True, interval=args.interval)
    ax.set_title(f"{args.exptid} Depth Visualization")

    # Show the animation
    plt.show()
            
    print(f"Depth_min: {depth_min}")
    print(f"Depth_max: {depth_max}")
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--exptid", type=str, help="Experiment name, used for logging and saving", required=True)
    parser.add_argument("--proj_name", type=str, default="parkour", help="Main project name, used for logging and saving")
    parser.add_argument("--interval", type=int, default=200, help="Rate frame should be changed at during video display")

    args = parser.parse_args()
    plot_depth(args)
    
    