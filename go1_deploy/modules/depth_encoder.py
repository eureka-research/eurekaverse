import threading
import time
from pathlib import Path
import multiprocessing as mp

import numpy as np
import torch
import torchvision
import os

from go1_deploy.modules.base_node import BaseNode, shared_memory_wrapper
from go1_deploy.modules.realsense_camera import width, height

class DepthEncoder(BaseNode):
    def __init__(self, env_cfg, train_cfg, load_dir, device, depth_replay_log=None, debug=False, save_depth=False):
        super().__init__()

        self.env_cfg = env_cfg
        self.train_cfg = train_cfg
        self.load_dir = load_dir
        self.depth_replay_log = depth_replay_log
        if depth_replay_log is not None:
            print("Using depth replay!")
        else:
            print("Running depth encoder!")
        self.device = device
        self.debug = debug

        self.dt = env_cfg.sim.dt * env_cfg.control.decimation * env_cfg.depth.update_interval
        # Settings for lock-step polling, unused
        self.dt_ms = self.dt * 1000
        self.offset_ms = self.dt_ms / 10 * 1  # Lock-step with realsense camera
        self.sleep_ms = 0

        self.near_clip = self.env_cfg.depth.near_clip
        self.far_clip = env_cfg.depth.far_clip
        original_width, original_height = env_cfg.depth.original_resolution
        processed_width, processed_height = env_cfg.depth.processed_resolution
        self.resize_transform = torchvision.transforms.Resize(
            (original_height, original_width), interpolation=torchvision.transforms.InterpolationMode.BICUBIC
        )
        self.update_interval = env_cfg.depth.update_interval
        self.use_direction_distillation = env_cfg.depth.use_direction_distillation
        self.t = 0

        self.create_buffer_infos = {
            "depth_encoder-processed_depth": ((processed_height, processed_width), np.float32),
            "depth_encoder-depth_latent": ((1, 32), np.float32),
            "depth_encoder-yaw": ((1, 2), np.float32),
            "depth_encoder-stop": ((1), bool),
            "depth_encoder-reset": ((1), bool),
            "depth_encoder-ready": ((1), bool)
        }
        self.access_buffer_infos = {
            "lcm_agent-obs_proprio": ((1, 48), np.float32),
            "realsense_camera-depth": ((height, width), np.float32)
        }

        self.save_depth = save_depth
        if self.save_depth:
            self.saved_depth = []
            self.saved_depth_path = f"{load_dir}/deployed_depth.npy"
            print(f"Saving depth to {self.saved_depth_path}")
            np.save(self.saved_depth_path, [])

            self.saved_latent = []
            self.saved_latent_path = f"{load_dir}/deployed_depth_latent.npy"
            print(f"Saving depth latent to {self.saved_latent_path}")
            np.save(self.saved_latent_path, [])


    def load(self, load_dir):
        load_dir = Path(load_dir)
        self.depth_encoder = torch.jit.load(load_dir / "traced" / "depth_latest.jit", map_location=self.device)
        self.depth_encoder.eval()
        self.depth_encoder.hidden_states = self.depth_encoder.hidden_states.to(self.device)

        # Dryrun
        with torch.no_grad():
            self.depth_encoder(self.process_depth(torch.rand(height, width, device=self.device)), torch.rand(1, self.env_cfg.env.n_proprio, device=self.device))
    
    def process_depth(self, depth):
        if depth is None:
            return
        depth = self.resize_transform(depth[None, :]).squeeze()
        height, width = depth.shape
        depth = depth[self.env_cfg.depth.crop_top:height-self.env_cfg.depth.crop_bottom, self.env_cfg.depth.crop_left:width-self.env_cfg.depth.crop_right]
        depth = torch.clip(depth, self.near_clip, self.far_clip)
        depth = (depth - self.near_clip) / (self.far_clip - self.near_clip) - 0.5
        return depth[None, ...]
    
    def run_encoder(self):
        if self.depth_replay_log is not None:
            depth = self.depth_replay_log[self.t].to(self.device)
        else:
            depth = self.process_depth(self.read_buffer("realsense_camera-depth", as_torch=True))
        self.write_buffer("depth_encoder-processed_depth", depth[0].cpu())  # Not necessary, just for visualization

        obs_proprio = self.read_buffer("lcm_agent-obs_proprio", as_torch=True)
        obs_proprio[:, 5:7] = 0

        self.start_profile("depth_encoder/depth_encoder")
        with torch.no_grad():
            depth_encoder_output = self.depth_encoder(depth, obs_proprio)
            if self.save_depth:
                self.saved_depth.append(depth.cpu().numpy()[0])
                self.saved_latent.append(depth_encoder_output.cpu().numpy())
        self.stop_profile("depth_encoder/depth_encoder")

        if self.save_depth and len(self.saved_depth) >= 100:
            self.flush_saving()

        if self.train_cfg.depth_encoder.train_direction_distillation:
            depth_latent = depth_encoder_output[:, :-2]
            if self.use_direction_distillation:
                yaw = depth_encoder_output[:, -2:]
                self.write_buffer("depth_encoder-yaw", (1.5 * yaw).cpu())
        else:
            depth_latent = depth_encoder_output
        self.write_buffer("depth_encoder-depth_latent", depth_latent.cpu())

        self.last_latent = depth_latent
    
    def flush_saving(self):
        if self.save_depth:
            if len(self.saved_depth) == 0 and len(self.saved_latent) == 0:
                return

            self.saved_depth = np.array(self.saved_depth)
            self.saved_latent = np.array(self.saved_latent)

            saved_depth = np.load(self.saved_depth_path)
            if len(saved_depth) == 0:
                saved_depth = self.saved_depth
            else:
                saved_depth = np.concatenate([saved_depth, self.saved_depth])

            saved_latent = np.load(self.saved_latent_path)
            if len(saved_latent) == 0:
                saved_latent = self.saved_latent
            else:
                saved_latent = np.concatenate([saved_latent, self.saved_latent])

            saved_depth = np.array(saved_depth)
            saved_latent = np.array(saved_latent)
            print("Flushed depth: ", saved_depth.shape, saved_latent.shape, self.saved_depth.shape, self.saved_latent.shape)
            np.save(self.saved_depth_path, saved_depth)
            np.save(self.saved_latent_path, saved_latent)
            self.saved_depth = []
            self.saved_latent = []

    def reset_hiddens(self):
        print("Resetting hidden state in depth encoder")
        self.depth_encoder.hidden_states *= 0

    @shared_memory_wrapper()
    def poll(self):
        self.write_buffer("depth_encoder-stop", True)
        self.load(self.load_dir)

        self.reset_hiddens()
        self.write_buffer("depth_encoder-ready", True)

        while True:
            stop = self.read_buffer("depth_encoder-stop")
            reset = self.read_buffer("depth_encoder-reset")
            if stop and not reset:
                self.flush_saving()
                continue
            if reset:
                self.reset_hiddens()
                self.write_buffer("depth_encoder-stop", False)
                self.write_buffer("depth_encoder-reset", False)

            self.start_profile("depth_encoder")
            self.run_encoder()
            time_elapsed = self.stop_profile("depth_encoder", save=False)
            if time_elapsed + self.time_eps < self.dt:
                time.sleep(self.dt - time_elapsed - self.time_eps)
            elif time_elapsed > self.dt + self.time_eps:
                print(f"Warning: depth encoder is running behind by {time_elapsed - self.dt:.4f}s!")

            self.t += 1

        # while True:
        #     if (time.perf_counter() * 1000 - self.offset_ms) % self.dt_ms < 4:
        #         t = int((time.perf_counter() * 1000) / self.dt_ms)
        #         if self.t > 0 and t > self.t + 1:
        #             print(f"Warning: Depth encoder is running behind by {t - self.t} steps!")
        #         self.t = t

        #         reset = self.read_buffer("depth_encoder-reset")
        #         if reset:
        #             self.reset_hiddens()
        #             self.write_buffer("depth_encoder-reset", False)

        #         self.start_profile("depth_encoder")
        #         self.run_encoder()
        #     else:
        #         time.sleep(self.sleep_ms / 1000)

    def spin_process(self):
        # Spawn process instead of fork, as needed for CUDA
        cuda_context = mp.get_context("spawn")
        self.process = cuda_context.Process(target=self.poll, daemon=False)
        self.process.start()
        return self.process

    def spin_thread(self):
        self.run_thread = threading.Thread(target=self.poll, daemon=True)
        self.run_thread.start()
        return self
