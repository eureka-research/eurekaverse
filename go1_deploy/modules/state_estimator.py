import select
import subprocess
import threading
import time
from functools import partial
from multiprocessing import Process
from typing import Tuple

import lcm
import numpy as np
import torch

from go1_deploy.modules import lc_addr
from go1_deploy.modules.base_node import BaseNode, shared_memory_wrapper
from go1_deploy.lcm_types.leg_control_data_lcmt import leg_control_data_lcmt
from go1_deploy.lcm_types.rc_command_lcmt import rc_command_lcmt
from go1_deploy.lcm_types.state_estimator_lcmt import state_estimator_lcmt

JOINT_IDX_MAPPING = [3, 4, 5, 0, 1, 2, 9, 10, 11, 6, 7, 8]
CONTACT_IDX_MAPPING = [1, 0, 3, 2]

lc = lcm.LCM(lc_addr)

def get_rpy_from_quaternion(q):
    w, x, y, z = q
    r = torch.arctan2(2 * (w * x + y * z), 1 - 2 * (x ** 2 + y ** 2))
    p = torch.arcsin(2 * (w * y - z * x))
    y = torch.arctan2(2 * (w * z + x * y), 1 - 2 * (y ** 2 + z ** 2))
    return torch.tensor([r, p, y], device=q.device)

def get_rotation_matrix_from_rpy(rpy):
    """
    Get rotation matrix from the given quaternion.
    Args:
        q (np.array[float[4]]): quaternion [w,x,y,z]
    Returns:
        np.array[float[3,3]]: rotation matrix.
    """
    r, p, y = rpy
    R_x = torch.tensor([[1, 0, 0], [0, torch.cos(r), -torch.sin(r)], [0, torch.sin(r), torch.cos(r)]], device=rpy.device)
    R_y = torch.tensor([[torch.cos(p), 0, torch.sin(p)], [0, 1, 0], [-torch.sin(p), 0, torch.cos(p)]], device=rpy.device)
    R_z = torch.tensor([[torch.cos(y), -torch.sin(y), 0], [torch.sin(y), torch.cos(y), 0], [0, 0, 1]], device=rpy.device)
    rot = R_z @ (R_y @ R_x)
    return rot

class StateEstimator(BaseNode):
    def __init__(self, device: str):
        super().__init__()

        self.device = device

        self.joint_pos = torch.zeros(12, device=self.device)
        self.joint_vel = torch.zeros(12, device=self.device)
        self.tau_est = torch.zeros(12, device=self.device)
        self.euler = torch.zeros(3, device=self.device)
        self.R = torch.eye(3, device=self.device)
        self.buf_idx = 0

        self.smoothing_length = 1
        self.deuler_history = torch.zeros((self.smoothing_length, 3), device=self.device)
        self.dt_history = torch.zeros((self.smoothing_length, 1), device=self.device)
        self.euler_prev = torch.zeros(3, device=self.device)
        self.timuprev = time.time()

        self.deuler = torch.zeros(3, device=self.device)

        self.body_ang_vel = torch.zeros(3, device=self.device)
        self.smoothing_ratio = 0.9

        self.contact_state = torch.ones(4, device=self.device)

        self.mode = 0
        self.left_stick = [0, 0]
        self.right_stick = [0, 0]
        self.joysticks = np.array([0, 0, 0, 0])
        self.left_upper_switch = 0
        self.left_lower_left_switch = 0
        self.left_lower_right_switch = 0
        self.right_upper_switch = 0
        self.right_lower_left_switch = 0
        self.left_upper_switch_pressed = 0
        self.left_lower_left_switch_pressed = 0
        self.left_lower_right_switch_pressed = 0
        self.right_upper_switch_pressed = 0
        self.right_lower_left_switch_pressed = 0

        self.right_lower_right_switch = 0
        self.right_lower_right_switch_pressed = 0
        self.trigger = np.array([self.right_lower_right_switch, self.right_lower_right_switch_pressed])

        self.init_time = time.perf_counter()
        self.received_first_legdata = False

        self.create_buffer_infos = {
            "state_estimator-euler": ((1, 3), np.float32),
            "state_estimator-deuler": ((1, 3), np.float32),
            "state_estimator-joint_pos": ((1, 12), np.float32),
            "state_estimator-joint_vel": ((1, 12), np.float32),
            "state_estimator-contact_state": ((1, 4), np.float32),
            "state_estimator-joysticks": ((4,), np.float32),
            "state_estimator-trigger": ((2,), np.float32)
        }

    def __enter__(self):
        imu = lc.subscribe("state_estimator_data", self._imu_cb, )
        leg = lc.subscribe("leg_control_data", self._legdata_cb, )
        cmd = lc.subscribe("rc_command", self._rc_command_cb, )

    def __exit__(self, *args):
        pass

    def get_euler(self):
        return self.euler

    def get_yaw(self):
        return self.euler[2]

    def get_deuler(self):
        return self.deuler

    def get_dof_pos(self):
        return self.joint_pos[JOINT_IDX_MAPPING]

    def get_dof_vel(self):
        return self.joint_vel[JOINT_IDX_MAPPING]

    def get_tau_est(self):
        return self.tau_est[JOINT_IDX_MAPPING]

    def get_gravity_vector(self):
        grav = torch.dot(self.R.T, torch.tensor([0, 0, -1], device=self.device))
        return grav

    def get_contact_state(self):
        return self.contact_state[CONTACT_IDX_MAPPING]

    def get_buttons(self):
        return np.array([
            self.left_lower_left_switch,
            self.left_upper_switch,
            self.right_lower_right_switch,
            self.right_upper_switch,
        ])

    def _legdata_cb(self, channel, data):
        msg = leg_control_data_lcmt.decode(data)
        self.joint_pos = torch.tensor(msg.q, device=self.device)
        self.joint_vel = torch.tensor(msg.qd, device=self.device)
        self.tau_est = torch.tensor(msg.tau_est, device=self.device)

        self.write_buffer("state_estimator-joint_pos", self.get_dof_pos())
        self.write_buffer("state_estimator-joint_vel", self.get_dof_vel())

        if not self.received_first_legdata:
            print(f"Received first legdata after {time.time() - self.init_time}s")
            self.received_first_legdata = True

    def _imu_cb(self, channel, data):
        msg = state_estimator_lcmt.decode(data)

        self.euler = torch.tensor(msg.rpy, device=self.device)
        self.deuler[:3] = torch.tensor(msg.omegaBody, device=self.device)
        self.R = get_rotation_matrix_from_rpy(self.euler)
        self.contact_state = 1.0 * (torch.tensor(msg.contact_estimate, device=self.device) > 200)
        self.deuler_history[self.buf_idx % self.smoothing_length, :] = self.euler - self.euler_prev
        self.dt_history[self.buf_idx % self.smoothing_length] = time.time() - self.timuprev
        self.timuprev = time.time()

        self.buf_idx += 1
        self.euler_prev = torch.tensor(msg.rpy, device=self.device)

        self.write_buffer("state_estimator-euler", self.get_euler())
        self.write_buffer("state_estimator-deuler", self.get_deuler())
        self.write_buffer("state_estimator-contact_state", self.get_contact_state())

    def _sensor_cb(self, channel, data):
        pass

    def _rc_command_cb(self, channel, data):
        msg = rc_command_lcmt.decode(data)

        self.left_upper_switch_pressed = \
            (msg.left_upper_switch and not self.left_upper_switch) or self.left_upper_switch_pressed
        self.left_lower_left_switch_pressed = \
            (msg.left_lower_left_switch and not self.left_lower_left_switch) or self.left_lower_left_switch_pressed
        self.left_lower_right_switch_pressed = \
            (msg.left_lower_right_switch and not self.left_lower_right_switch) or self.left_lower_right_switch_pressed
        self.right_upper_switch_pressed = \
            (msg.right_upper_switch and not self.right_upper_switch) or self.right_upper_switch_pressed
        self.right_lower_left_switch_pressed = \
            (msg.right_lower_left_switch and not self.right_lower_left_switch) or self.right_lower_left_switch_pressed
        self.right_lower_right_switch_pressed = msg.right_lower_right_switch

        self.mode = msg.mode
        self.right_stick = msg.right_stick
        self.left_stick = msg.left_stick
        self.left_upper_switch = msg.left_upper_switch
        self.left_lower_left_switch = msg.left_lower_left_switch
        self.left_lower_right_switch = msg.left_lower_right_switch
        self.right_upper_switch = msg.right_upper_switch
        self.right_lower_left_switch = msg.right_lower_left_switch
        self.right_lower_right_switch = msg.right_lower_right_switch

        self.joysticks = np.array([*self.left_stick, *self.right_stick])
        self.trigger = np.array([self.right_lower_right_switch, self.right_lower_right_switch_pressed])
        self.write_buffer("state_estimator-joysticks", self.joysticks)
        self.write_buffer("state_estimator-trigger", self.trigger)

    @shared_memory_wrapper()
    def poll(self):
        self.write_buffer("state_estimator-trigger", np.array([0.0, 0.0]))
        with self:
            while True:
                timeout = 0.01
                rfds, wfds, efds = select.select([lc.fileno()], [], [], timeout)
                if rfds:
                    lc.handle()
                else:
                    continue

    def spin_process(self):
        self.process = Process(target=self.poll, daemon=False)
        self.process.start()
        return self.process

    def spin_thread(self):
        self.thread = threading.Thread(target=self.poll, daemon=False)
        self.thread.start()
