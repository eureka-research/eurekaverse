
import time
import numpy as np
import cv2

from go1_deploy.modules.base_node import BaseNode, shared_memory_wrapper

class DepthLatentVisualizer(BaseNode):
    def __init__(self, fps):
        super().__init__()
        self.fps = fps
        self.dt = 1 / self.fps

        self.access_buffer_infos = {
            "depth_encoder-depth_latent": ((1, 32), np.float32),
        }
    
    def visualize(self, show_window=True):
        depth_latent = self.read_buffer("depth_encoder-depth_latent")
        depth_latent_min, depth_latent_max = np.min(depth_latent), np.max(depth_latent)
        if depth_latent_min != depth_latent_max:
            depth_latent = (depth_latent - depth_latent_min) / (depth_latent_max - depth_latent_min)
        else:
            depth_latent = np.zeros_like(depth_latent)

        depth_latent = depth_latent.reshape((4, 8))
        upscale_factor = 10
        depth_latent = np.kron(depth_latent, np.ones((upscale_factor, upscale_factor)))
        depth_latent = cv2.applyColorMap(cv2.convertScaleAbs(depth_latent, alpha=255), cv2.COLORMAP_JET)
        
        if show_window:
            cv2.imshow('Depth Latent', depth_latent)
            cv2.waitKey(1)
        else:
            return depth_latent

    @shared_memory_wrapper()
    def poll(self):
        cv2.namedWindow('Depth Latent', cv2.WINDOW_AUTOSIZE)
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
    visualizer = DepthLatentVisualizer(fps=10)
    visualizer.poll()