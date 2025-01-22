import os
import sys
import isaacgym
import torch
import torch.nn as nn
from pathlib import Path
import argparse
import code
import shutil

from legged_gym import LEGGED_GYM_ROOT_DIR
from legged_gym.envs.base.legged_robot_config import LeggedRobotCfg as DefaultCfg, LeggedRobotCfgPPO as DefaultCfgPPO
from legged_gym.utils.helpers import get_checkpoint, class_to_dict
from legged_gym.utils import task_registry

from rsl_rl.modules.actor_critic import Actor, StateHistoryEncoder, get_activation, ActorCriticRMA
from rsl_rl.modules.estimator import Estimator
from rsl_rl.modules.depth_backbone import DepthOnlyFCBackbone58x87, RecurrentDepthBackbone

# This is based on ActorCriticRMA and OnPolicyRunner
class HardwareVisionNN(nn.Module):
    def __init__(self,  num_prop,
                        num_scan,
                        num_priv_latent, 
                        num_priv_explicit,
                        num_hist,
                        num_actions,
                        scan_encoder_dims=[256, 256, 256],
                        actor_hidden_dims=[256, 256, 256],
                        activation='elu',
                        **kwargs):
        super(HardwareVisionNN, self).__init__()

        self.num_prop = num_prop
        self.num_scan = num_scan
        self.num_hist = num_hist
        self.num_actions = num_actions
        self.num_priv_latent = num_priv_latent
        self.num_priv_explicit = num_priv_explicit
        num_obs = num_prop + num_scan + num_hist * num_prop + num_priv_latent + num_priv_explicit
        self.num_obs = num_obs

        priv_encoder_dims= kwargs['priv_encoder_dims']
        activation = get_activation(activation)
        self.actor = Actor(num_prop, num_scan, num_actions, scan_encoder_dims, actor_hidden_dims, priv_encoder_dims, num_priv_latent, num_priv_explicit, num_hist, activation, tanh_encoder_output=kwargs['tanh_encoder_output'])
        self.estimator = Estimator(input_dim=num_prop, output_dim=num_priv_explicit, hidden_dims=[128, 64])

    def forward(self, obs, depth_latent):
        obs[:, self.num_prop+self.num_scan : self.num_prop+self.num_scan+self.num_priv_explicit] = self.estimator(obs[:, :self.num_prop])
        return self.actor(obs, hist_encoding=True, eval=False, scandots_latent=depth_latent)


def save_jit(args):    
    load_dir = Path(LEGGED_GYM_ROOT_DIR) / "logs" / args.proj_name / args.exptid
    model = get_checkpoint(load_dir, checkpoint=args.checkpoint)
    load_path = os.path.join(load_dir, model)

    env_cfg, train_cfg = task_registry.get_saved_cfgs(load_dir=load_dir)
    if env_cfg is None or train_cfg is None:
        print("Warning: failed to load saved config, defaulting to current config")
        env_cfg, train_cfg = task_registry.get_cfgs(name=args.task)
    
    train_cfg = class_to_dict(train_cfg)
    policy = HardwareVisionNN(
        env_cfg.env.n_proprio,
        env_cfg.env.n_scan,
        env_cfg.env.n_priv_latent,
        env_cfg.env.n_priv,
        env_cfg.env.history_len,
        env_cfg.env.num_actions,
        **train_cfg["policy"]
    )

    print(f"Loading model from: {load_path}")
    ac_state_dict = torch.load(load_path, map_location="cpu")
    # policy.load_state_dict(ac_state_dict['model_state_dict'], strict=False)
    policy.actor.load_state_dict(ac_state_dict['depth_actor_state_dict'], strict=True)
    policy.estimator.load_state_dict(ac_state_dict['estimator_state_dict'])
    
    policy = policy.cpu()
    if not os.path.exists(os.path.join(load_dir, "traced")):
        os.mkdir(os.path.join(load_dir, "traced"))

    # Save the traced actor
    policy.eval()
    policy.actor.eval()
    policy.estimator.eval()
    with torch.no_grad(): 
        num_envs = 1
        obs_input = torch.ones(num_envs, policy.num_obs, device="cpu")
        depth_latent = torch.ones(1, 32, device="cpu")
        traced_policy = torch.jit.trace(policy, (obs_input, depth_latent))
        # traced_policy = torch.jit.script(policy)
        save_filename = "policy_latest.jit" if args.checkpoint == -1 else f"policy_{args.checkpoint}.jit"
        save_path = os.path.join(load_dir, "traced", save_filename)
        traced_policy.save(save_path)
        print("Saved traced_actor at ", os.path.abspath(save_path))
    
    # Save Depth Encoder
    # state_dict = {'depth_encoder_state_dict': ac_state_dict['depth_encoder_state_dict']}
    # torch.save(state_dict, os.path.join(load_dir, "traced", args.exptid + "-" + str(args.checkpoint) + "-vision_weight.pt"))
    depth_backbone = DepthOnlyFCBackbone58x87(
        env_cfg.env.n_proprio,
        train_cfg["policy"]["scan_encoder_dims"][-1],
        train_cfg["depth_encoder"]["hidden_dims"],
        )
    depth_encoder = RecurrentDepthBackbone(depth_backbone, env_cfg, output_yaw=train_cfg["depth_encoder"]["train_direction_distillation"])
    # depth_encoder = DepthEncoder()
    depth_encoder.load_state_dict(ac_state_dict['depth_encoder_state_dict'])
    depth_encoder = depth_encoder.cpu()    
    depth_encoder.eval()

    with torch.no_grad():
        depth_save_filename = "depth_latest.jit" if args.checkpoint == -1 else f"depth_{args.checkpoint}.jit"
        depth_save_path = os.path.join(load_dir, "traced", depth_save_filename)
        torch.jit.save(torch.jit.script(depth_encoder), depth_save_path)
        print("Saved traced_depth at ", os.path.abspath(depth_save_path))

    loaded_depth = torch.jit.load(depth_save_path)
    loaded_depth.eval()
    loaded_depth(torch.zeros(10, 60, 90), torch.zeros(10, 48))

    if args.deploy:
        deploy_dir = Path(LEGGED_GYM_ROOT_DIR) / "logs" / "deploy" / args.exptid
        if not os.path.exists(deploy_dir):
            os.makedirs(deploy_dir)
        if not os.path.exists(deploy_dir / "traced"):
            os.makedirs(deploy_dir / "traced")
        shutil.copy(save_path, deploy_dir / "traced" / save_filename)
        shutil.copy(depth_save_path, deploy_dir / "traced" / depth_save_filename)
        config_path = os.path.join(load_dir, "legged_robot_config.pkl")
        shutil.copy(config_path, deploy_dir / "legged_robot_config.pkl")
        print(f"Deployed traced models to {deploy_dir}")
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--proj_name", type=str, default="parkour", help="Main project name, used for logging and saving")
    parser.add_argument("--exptid", type=str, help="Experiment name, used for logging and saving")
    parser.add_argument('--checkpoint', type=int, default=-1)
    parser.add_argument("--deploy", action="store_true", help="Move model to deployment directory")
    args = parser.parse_args()

    save_jit(args)
    