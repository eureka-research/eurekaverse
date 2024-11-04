
import time
import numpy as np
import cv2

from go1_deploy.modules.base_node import BaseNode, shared_memory_wrapper
from go1_deploy.scripts.visualize_processed_depth import ProcessedDepthVisualizer
from go1_deploy.scripts.visualize_encoded_latent import DepthLatentVisualizer

class DepthVisualizer(BaseNode):
    def __init__(self, fps):
        super().__init__()
        self.fps = fps
        self.dt = 1 / self.fps

        self.depth_latent_visualizer = DepthLatentVisualizer(fps=fps)
        self.processed_depth_visualizer = ProcessedDepthVisualizer(fps=fps)

    def visualize(self):
        depth_latent = self.depth_latent_visualizer.visualize(show_window=False)
        processed_depth = self.processed_depth_visualizer.visualize(show_window=False)
        # Turn 40x80 to 40x90
        depth_latent = np.pad(depth_latent, ((0, 0), (0, 10), (0, 0)), mode="constant", constant_values=0)
        # Concatenate 40x90 with 60x90
        depth = np.concatenate((depth_latent, processed_depth), axis=0)
        cv2.imshow('Depth', depth)
        cv2.waitKey(1)

    @shared_memory_wrapper("depth_latent_visualizer")
    @shared_memory_wrapper("processed_depth_visualizer")
    def poll(self):
        cv2.namedWindow('Depth', cv2.WINDOW_AUTOSIZE)
        prev_time = time.perf_counter()
        while True:
            self.visualize()

            time_elapsed = time.perf_counter() - prev_time
            if time_elapsed + self.time_eps < self.dt:
                time.sleep(self.dt - time_elapsed - self.time_eps)
            elif time_elapsed > self.dt + self.time_eps:
                print(f"Warning: depth latent visualizer is running behind by {time_elapsed - self.dt:.4f}s!")
            prev_time = time.perf_counter()

if __name__ == "__main__":
    visualizer = DepthVisualizer(fps=10)
    visualizer.poll()