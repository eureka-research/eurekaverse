import numpy as np
import cv2
from shared_memory import SharedMemory
import time

from go1_deploy.modules.base_node import BaseNode, shared_memory_wrapper
from go1_deploy.modules.realsense_camera import width, height


class RealSenseVisualizer(BaseNode):
    def __init__(self, fps):
        super().__init__()
        self.fps = fps
        self.dt = 1 / self.fps

        self.access_buffer_infos = {
            "realsense_camera-depth": ((height, width), np.float32),
        }
    
    def visualize(self):
        while True:
            depth_image = self.read_buffer("realsense_camera-depth") * 1000  # Convert back to mm
            if np.all(depth_image == 0):
                print("No data in the shared memory.")
                time.sleep(0.1)
                continue

            crop_top, crop_bottom, crop_left, crop_right = 0, 0, 8 * 6, 8 * 6
            depth_image = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.1), cv2.COLORMAP_JET)
            cv2.rectangle(depth_image, (crop_left, crop_top), (depth_image.shape[1] - crop_right, depth_image.shape[0] - crop_bottom), (255, 255, 255), 4)                
            cv2.imshow('RealSense', depth_image)
            cv2.waitKey(1)

    @shared_memory_wrapper()
    def poll(self):
        cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        prev_time = time.perf_counter()
        while True:
            self.visualize()

            time_elapsed = time.perf_counter() - prev_time
            if time_elapsed + self.time_eps < self.dt:
                time.sleep(self.dt - time_elapsed - self.time_eps)
            elif time_elapsed > self.dt + self.time_eps:
                print(f"Warning: realsense visualizer is running behind by {time_elapsed - self.dt:.4f}s!")
            prev_time = time.perf_counter()

if __name__ == "__main__":
    visualizer = RealSenseVisualizer(fps=10)
    visualizer.poll()