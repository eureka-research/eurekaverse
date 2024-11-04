# Based on /geyang_parkour/go1_gym_deploy/utils/deployment_runner.py
import copy
import time
import warnings

import numpy as np
import torch

from go1_deploy.modules.base_node import BaseNode, shared_memory_wrapper, shared_memory_cleanup_wrapper
from go1_deploy.modules.parkour_actor import ParkourActor
from go1_deploy.modules.lcm_agent import LCMAgent

class DeploymentRunner(BaseNode):
    def __init__(self, policy: ParkourActor, lcm_agent: LCMAgent, debug=False):
        super().__init__()

        self.policy = policy
        self.lcm_agent = lcm_agent
        self.debug = debug

        self.log_dict = {}

        self.access_buffer_infos = {
            "depth_encoder-stop": ((1), bool),
            "depth_encoder-reset": ((1), bool),
            "depth_encoder-ready": ((1), bool),
        }


    def calibrate(self, wait=True, low=False):
        print("Waiting for LCM agent to start publishing data...")
        while True:
            self.lcm_agent.compute_observations()
            joint_pos = self.lcm_agent.dof_pos
            if not torch.all(joint_pos == 0):
                break

        if low:
            final_goal = np.array([0., 0.3, -0.7,
                                    0., 0.3, -0.7,
                                    0., 0.3, -0.7,
                                    0., 0.3, -0.7,])
        else:
            final_goal = np.zeros(12)

        nominal_joint_pos = self.lcm_agent.default_dof_pos
        print("About to calibrate; the robot will stand [Press R2 to calibrate]")
        while wait:
            if self.lcm_agent.read_buffer("state_estimator-trigger")[1]:
                break
        print("Trigger pressed, starting calibration")
        time.sleep(0.5)

        cal_action = np.zeros((1, 12))
        target_sequence = []

        # target is the next position, relative to the nominal pose
        target = (joint_pos - nominal_joint_pos).cpu()
        while torch.max(torch.abs(target - final_goal)) > 0.01:
            target -= np.clip((target - final_goal), -0.05, 0.05)
            target_sequence += [copy.deepcopy(target)]

        self.lcm_agent.reset()
        for target in target_sequence:
            next_target = copy.deepcopy(target)

            action_scale = self.lcm_agent.action_scale
            next_target = next_target / action_scale
            cal_action[:, 0:12] = next_target

            self.lcm_agent.step(torch.from_numpy(cal_action).to(device=self.lcm_agent.default_dof_pos.device), debug=False)
            self.lcm_agent.compute_observations()

        print("Starting pose calibrated [Press R2 to start running]")
        while wait:
            if self.lcm_agent.read_buffer("state_estimator-trigger")[1]:
                break
        print("Trigger pressed, starting run")
        time.sleep(0.5)

    @shared_memory_wrapper()
    @shared_memory_cleanup_wrapper("lcm_agent")
    @shared_memory_cleanup_wrapper("policy")
    def run(self, max_steps=100000000, action_replay_log=None, obs_replay_log=None):
        assert all((self.lcm_agent is not None, self.policy is not None)), "Missing modules!"

        if action_replay_log is not None:
            print("Using action replay!")
            max_steps = min(max_steps, len(action_replay_log))
        elif obs_replay_log is not None:
            print("Using observation replay!")
            max_steps = min(max_steps, len(obs_replay_log))
        else:
            print("Running the policy!")

        self.calibrate(wait=True)
        obs = self.lcm_agent.reset()

        vision_latent = None

        self.log_dict["obs"] = []
        self.log_dict["actions_unitree"] = []
        self.log_dict["depths"] = []

        print("Waiting for depth encoder to be ready...")
        while not self.read_buffer("depth_encoder-ready"):
            time.sleep(0.1)

        print("Starting the control loop now!")
        self.write_buffer("depth_encoder-reset", True)

        self.start_profile("deployment_runner/iteration")
        for t in range(max_steps):
            self.start_profile("deployment_runner/policy")
            if action_replay_log is not None:
                actions = action_replay_log[t].to(self.policy.device)
            elif obs_replay_log is not None:
                raise NotImplementedError
                obs = obs_replay_log[t].to(self.policy.device)
                if depth is not None:
                    depth = depth.to(self.policy.device)
                with torch.no_grad():
                    actions, vision_latent = self.policy(depth, obs, vision_latent=vision_latent)
            else:
                with torch.no_grad():
                    actions, vision_latent = self.policy(obs)
            self.stop_profile("deployment_runner/policy")

            self.start_profile("deployment_runner/lcm_step")
            obs, infos = self.lcm_agent.step(actions, debug=False)
            self.stop_profile("deployment_runner/lcm_step")

            # Bad orientation emergency stop
            rpy = self.lcm_agent.imu[0]
            if abs(rpy[0]) > 1.6 or abs(rpy[1]) > 1.6:
                print("Bad orientation detected, stopping!")
                self.calibrate(wait=False, low=True)

            if self.lcm_agent.read_buffer("state_estimator-trigger")[1]:
                self.write_buffer("depth_encoder-stop", True)
                self.policy.flush_saving()

                self.calibrate(wait=True)
                obs = self.lcm_agent.reset()
                self.write_buffer("depth_encoder-reset", True)
                print("Starting again now!")

            self.stop_profile("deployment_runner/iteration")
            if t % 100 == 0 and self.debug:
                self.print_profile()
                self.clear_profile()
                print()
            self.start_profile("deployment_runner/iteration")

        self.calibrate(wait=False)
        print("Finished running, returning to nominal pose")
