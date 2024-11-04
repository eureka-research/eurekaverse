from pathlib import Path

# import lcm
# lc = lcm.LCM("udpm://239.255.76.67:7667?ttl=255")

import pickle
import numpy as np

from go1_deploy.modules.realsense_camera import RealSenseCamera
import torch

def load_action_replay(path):
    action_replay = np.load(path + "/action_replay.npy")
    action_replay = torch.from_numpy(action_replay)
    action_replay = action_replay[200:]
    return action_replay

def load_obs_replay(path):
    obs_replay = np.load(path + "/obs_replay.npy")
    obs_replay = torch.from_numpy(obs_replay)
    obs_replay = obs_replay[200:]
    return obs_replay

def load_depth_replay(path):
    depth_replay = np.load(path + "/depth_replay.npy")
    depth_replay = torch.from_numpy(depth_replay)
    depth_replay = depth_replay[10:]
    return depth_replay

debug_flags = {
    "realsense_camera": False,
    "lcm_agent": False,
    "depth_encoder": False,
    "parkour_actor": False,
    "deployment_runner": False,
}

replay_flags = {
    "action": False,
    "obs": False,
    "depth": False,
}

save_flags = {
    "obs": False,
    "depth": False,
    "action": False,
}

if __name__ == "__main__":
    import time

    from go1_deploy.modules.lcm_agent import LCMAgent
    from go1_deploy.modules.state_estimator import StateEstimator
    from go1_deploy.modules.deployment_runner import DeploymentRunner
    from go1_deploy.modules.parkour_actor import ParkourActor
    from go1_deploy.modules.depth_encoder import DepthEncoder

    load_dir = ""  # Insert your policy run name here
    if load_dir == "":
        print("Please insert your policy run name in the 'load_dir' variable!")
        exit()
    load_dir = f"../../extreme-parkour/legged_gym/logs/deploy/{load_dir}"

    device = "cuda"

    config_path = Path(load_dir) / "legged_robot_config.pkl"
    if not config_path.exists():
        print(f"No config found at {config_path}!")
        exit()
    with open(config_path, "rb") as f:
        env_cfg, train_cfg = pickle.load(f)
    
    action_replay, obs_replay, depth_replay = None, None, None
    if replay_flags["action"]:
        action_replay = load_action_replay(load_dir)
    if replay_flags["obs"]:
        obs_replay = load_obs_replay(load_dir)
    if replay_flags["depth"]:
        depth_replay = load_depth_replay(load_dir)

    assert env_cfg.depth.use_direction_distillation == False
    assert env_cfg.commands.ranges.ang_vel_yaw == [-0.5, 0.5]

    print("===== CONFIG PARAMETERS =====")
    print(f"Loading policy: {load_dir}")
    print()
    print(f"Control dt: {env_cfg.sim.dt * env_cfg.control.decimation}")
    print(f"Control stiffness (Kp): {env_cfg.control.stiffness['joint']}")
    print(f"Control damping (Kd): {env_cfg.control.damping['joint']}")
    print()
    print(f"Depth update interval: {env_cfg.depth.update_interval}")
    print()
    print(f"Command speed range: {env_cfg.commands.ranges.lin_vel_x}")
    print(f"Command yaw range: {env_cfg.commands.ranges.ang_vel_yaw}")
    print("=============================")
    print()

    # Start up asynchonous processes for camera (60fps), state estimator (1000Hz), and depth encoder (50Hz)
    state_estimator = StateEstimator("cpu")
    state_estimator.spin_process()
    time.sleep(0.1)

    camera_fps = 1 / (env_cfg.sim.dt * env_cfg.control.decimation * env_cfg.depth.update_interval)
    camera = RealSenseCamera(camera_fps, debug=debug_flags["realsense_camera"])
    camera.spin_process()
    time.sleep(0.1)

    lcm_agent = LCMAgent(env_cfg, device=device, debug=debug_flags["lcm_agent"])

    depth_encoder = DepthEncoder(env_cfg, train_cfg, load_dir, device=device, depth_replay_log=depth_replay, debug=debug_flags["depth_encoder"], save_depth=save_flags["depth"])
    depth_encoder.spin_process()
    time.sleep(3)  # Takes a while to start up since it's spawning a new process

    # Start running policy in this process (50Hz)
    actor = ParkourActor(env_cfg, load_dir, depth_encoder, device=device, debug=debug_flags["parkour_actor"], save_obs=save_flags["obs"], save_actions=save_flags["action"])
    deployment_runner = DeploymentRunner(actor, lcm_agent, debug=debug_flags["deployment_runner"])
    deployment_runner.run(max_steps=int(1e8), action_replay_log=action_replay, obs_replay_log=action_replay)
