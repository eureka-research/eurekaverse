import os
import subprocess
import threading
import time
from functools import partial
from multiprocessing import Process
from typing import Union, Tuple
import numpy as np
import pyrealsense2 as rs

from go1_deploy.modules.base_node import BaseNode, shared_memory_wrapper

# Was originally 640, 360 at maximum 30fps
width, height = 480, 270

class RealSenseCamera(BaseNode):
    verbose = False

    def __init__(self, fps, exposure=None, debug=False):
        super().__init__()

        self.debug = debug

        self.fps = fps
        self.exposure = exposure
        self.t = 0
        self.dt = 1 / self.fps
        # Settings for lock-step polling, unused
        self.dt_ms = self.dt * 1000
        self.offset_ms = self.dt_ms / 10 * 0
        self.sleep_ms = 0

        self.hole_filling_filter_duration = []
        self.spatial_filter_duration = []
        self.temporal_filter_duration = []

        self.create_buffer_infos = {
            "realsense_camera-depth": ((height, width), np.float32)
        }

    def __enter__(self):
        self.pipeline = rs.pipeline()
        config = rs.config()
        realsense_fps = min([fps for fps in [15, 30, 60] if fps >= self.fps])
        config.enable_stream(rs.stream.depth, width, height, rs.format.z16, realsense_fps)

        profile = self.pipeline.start(config)
        # Hole filling options: 0 = left, 1 = farthest around, 2 = nearest around
        self.hole_filling_filter = rs.hole_filling_filter(2)
        self.spatial_filter = rs.spatial_filter()
        self.spatial_filter.set_option(rs.option.filter_magnitude, 5)
        self.spatial_filter.set_option(rs.option.filter_smooth_alpha, 0.75)
        self.spatial_filter.set_option(rs.option.filter_smooth_delta, 1)
        self.spatial_filter.set_option(rs.option.holes_fill, 4)
        self.temporal_filter = rs.temporal_filter()
        self.temporal_filter.set_option(rs.option.filter_smooth_alpha, 0.75)
        self.temporal_filter.set_option(rs.option.filter_smooth_delta, 1)

        color_sensor = profile.get_device().first_color_sensor()
        color_sensor.set_option(rs.option.enable_auto_exposure, 1)
        if self.exposure is not None:
            color_sensor.set_option(rs.option.exposure, self.exposure)
        color_sensor.set_option(rs.option.enable_auto_white_balance, 1)

        # AE control is important. If it is too dark, the range map will look bad.
        depth_sensor = profile.get_device().first_depth_sensor()
        depth_sensor.set_option(rs.option.enable_auto_exposure, 0)
        depth_sensor.set_option(rs.option.exposure, 8500.00)


        return self

    def __exit__(self, *args):
        self.pipeline.stop()

    def grab(self, *keys):
        frames = None
        pipeline_exception = None
        for attempts in range(10):
            try:
                frames = self.pipeline.wait_for_frames()
                break
            except Exception as e:
                pipeline_exception = e
                time.sleep(0.01)
        if frames is None:
            raise pipeline_exception
        if attempts > 0:
            print(f"Warning: RealSense failed to grab frames, succeeded after {attempts} attempts!")

        for k in keys:
            if k == "depth":
                self.depth_frame = frames.get_depth_frame()
                buff = self.depth_frame

                # Realsense filters
                self.start_profile("realsense_camera/hole_filling_filter")
                buff = self.hole_filling_filter.process(buff)
                self.stop_profile("realsense_camera/hole_filling_filter")


                self.start_profile("realsense_camera/spatial_filter")
                # buff = self.spatial_filter.process(buff)
                self.stop_profile("realsense_camera/spatial_filter")

                self.start_profile("realsense_camera/temporal_filter")
                buff = self.temporal_filter.process(buff)
                self.stop_profile("realsense_camera/temporal_filter")

                results = np.asanyarray(buff.get_data())
                results = np.asanyarray(results) / 1000  # Convert to meters
                self.write_buffer("realsense_camera-depth", results)
            else:
                raise ValueError(f"Unknown key {k}")


    @shared_memory_wrapper()
    def poll(self):
        with self:
            while True:
                self.grab("depth")
                time_elapsed = self.stop_profile("realsense_camera", save=False)
                if time_elapsed + self.time_eps < self.dt:
                    time.sleep(self.dt - time_elapsed - self.time_eps)
                elif time_elapsed > self.dt + self.time_eps:
                    print(f"Warning: realsense camera is running behind by {time_elapsed - self.dt:.4f}s!")
                self.stop_profile("realsense_camera")
                self.start_profile("realsense_camera")

                if self.t % 100 == 0 and self.debug:
                    self.print_profile()
                    self.clear_profile()
                    print()
                self.t += 1

            # while True:
            #     if (time.perf_counter() * 1000 - self.offset_ms) % self.dt_ms < 4:
            #         t = int((time.perf_counter() * 1000) / self.dt_ms)
            #         if self.t is not None and t > self.t + 1:
            #             print(f"Warning: RealSense camera is running behind by {t - self.t} frames!")
            #         self.t = t
            #         self.grab("depth")
            #     else:
            #         time.sleep(self.sleep_ms / 1000)
            #     self.stop_profile("realsense_camera")
            #     self.start_profile("realsense_camera")

            #     if self.t is not None and self.t % 100 == 0 and self.debug:
            #         self.print_profile()
            #         self.clear_profile()
            #         print()

    def spin_process(self):
        self.process = Process(target=self.poll, daemon=False)
        self.process.start()
        return self.process

    def spin_thread(self, *keys):
        self.process = threading.Thread(target=partial(self.poll, *keys), daemon=True)
        self.process.start()
        return self
