import numpy as np
import cv2
from shared_memory import SharedMemory
import time

from go1_deploy.modules.base_node import BaseNode, shared_memory_wrapper


class ProcessedDepthVisualizer(BaseNode):
    def __init__(self, fps):
        super().__init__()
        self.fps = fps
        self.dt = 1 / self.fps

        self.access_buffer_infos = {
            "depth_encoder-processed_depth": ((60, 90), np.float32),
        }
    
    def visualize(self, show_window=True):
        depth_image = self.read_buffer("depth_encoder-processed_depth")
        depth_image = (depth_image + 0.5) * 255
        depth_image = cv2.applyColorMap(cv2.convertScaleAbs(depth_image), cv2.COLORMAP_PLASMA)
        if show_window:
            cv2.imshow('Processed Depth', depth_image)
            cv2.waitKey(1)
        else:
            return depth_image

    @shared_memory_wrapper()
    def poll(self):
        cv2.namedWindow('Processed Depth', cv2.WINDOW_AUTOSIZE)
        prev_time = time.perf_counter()
        while True:
            self.visualize()

            time_elapsed = time.perf_counter() - prev_time
            if time_elapsed + self.time_eps < self.dt:
                time.sleep(self.dt - time_elapsed - self.time_eps)
            elif time_elapsed > self.dt + self.time_eps:
                print(f"Warning: processed depth visualizer is running behind by {time_elapsed - self.dt:.4f}s!")
            prev_time = time.perf_counter()

if __name__ == "__main__":
    visualizer = ProcessedDepthVisualizer(fps=10)
    visualizer.poll()