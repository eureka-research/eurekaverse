# Extreme Parkour with Legged Robots #
<p align="center">
<img src="./images/teaser.jpeg" width="80%"/>
</p>

**Authors**: [Xuxin Cheng*](https://chengxuxin.github.io/), [Kexin Shi*](https://tenhearts.github.io/), [Ananye Agarwal](https://anag.me/), [Deepak Pathak](https://www.cs.cmu.edu/~dpathak/)  
**Website**: https://extreme-parkour.github.io  
**Paper**: https://arxiv.org/abs/2309.14341

### Installation ###
```bash
conda create -n parkour python=3.8
conda activate parkour
cd
pip3 install torch==1.10.0+cu113 torchvision==0.11.1+cu113 torchaudio==0.10.0+cu113 -f https://download.pytorch.org/whl/cu113/torch_stable.html
git clone git@github.com:chengxuxin/extreme-parkour.git
cd extreme-parkour
# Download the Isaac Gym binaries from https://developer.nvidia.com/isaac-gym 
# Originally trained with Preview3, but haven't seen bugs using Preview4.
cd isaacgym/python && pip install -e .
cd ~/extreme-parkour/rsl_rl && pip install -e .
cd ~/extreme-parkour/legged_gym && pip install -e .
pip install "numpy<1.24" pydelatin wandb tqdm opencv-python ipdb pyfqmr flask
```

### Usage ###
`cd legged_gym/scripts`
1. Train base policy:  
```bash
python train.py --exptid xxx-xx-WHATEVER --device cuda:0
```
Train 10-15k iterations (8-10 hours on 3090) (at least 15k recommended).

2. Train distillation policy:
```bash
python train.py --exptid yyy-yy-WHATEVER --device cuda:0 --resume --resumeid xxx-xx --delay --use_camera
```
Train 5-10k iterations (5-10 hours on 3090) (at least 5k recommended). 
>You can run either base or distillation policy at arbitary gpu # as long as you set `--device cuda:#`, no need to set `CUDA_VISIBLE_DEVICES`.

3. Play base policy:
```bash
python play.py --exptid xxx-xx
```
No need to write the full exptid. The parser will auto match runs with first 6 strings (xxx-xx). So better make sure you don't reuse xxx-xx. Delay is added after 8k iters. If you want to play after 8k, add `--delay`

4. Play distillation policy:
```bash
python play.py --exptid yyy-yy --delay --use_camera
```

5. Save models for deployment:
```bash
python save_jit.py --exptid xxx-xx
```
This will save the models in `legged_gym/logs/parkour_new/xxx-xx/traced/`.

### Viewer Usage
Can be used in both IsaacGym and web viewer.
- `ALT + Mouse Left + Drag Mouse`: move view.
- `[ ]`: switch to next/prev robot.
- `Space`: pause/unpause.
- `F`: switch between free camera and following camera.

### Arguments
- --exptid: string, can be `xxx-xx-WHATEVER`, `xxx-xx` is typically numbers only. `WHATEVER` is the description of the run. 
- --device: can be `cuda:0`, `cpu`, etc.
- --delay: whether add delay or not.
- --checkpoint: the specific checkpoint you want to load. If not specified load the latest one.
- --resume: resume from another checkpoint, used together with `--resumeid`.
- --seed: random seed.
- --no_wandb: no wandb logging.
- --use_camera: use camera or scandots.
- --web: used for playing on headless machines. It will forward a port with vscode and you can visualize seemlessly in vscode with your idle gpu or cpu. [Live Preview](https://marketplace.visualstudio.com/items?itemName=ms-vscode.live-server) vscode extension required, otherwise you can view it in any browser.

### Tips
3 pre-trained models are provided in `legged_gym/logs/parkour_new`. You can play with them directly.
- `051-40`: base policy with scandots as input.
- `051-41`: distillation policy with depth as input. No heading direction distillation.
- `051-42`: distillation policy with depth as input. With heading direction distillation. 

If you don't need direction distillation, comment out the following [line](https://github.com/chengxuxin/extreme-parkour/blob/4fe8b3d138a8516ca3e96e61f48717d37ddf6e79/rsl_rl/rsl_rl/runners/on_policy_runner.py#L270
) in `rsl_rl/rsl_rl/runners/on_policy_runner.py`:
```python
obs_student[infos["delta_yaw_ok"], 6:8] = yaw.detach()[infos["delta_yaw_ok"]]
```
and [line](https://github.com/chengxuxin/extreme-parkour/blob/4fe8b3d138a8516ca3e96e61f48717d37ddf6e79/legged_gym/legged_gym/scripts/play.py#L157) in `legged_gym/legged_gym/scripts/play.py`:
```python
obs[:, 6:8] = 1.5*yaw
```

### Deployment
A1 + internal realsense D435i + Jetson Xavier NX.  
Hardware code and Go1 support coming later.


### Acknowledgement
https://github.com/leggedrobotics/legged_gym  
https://github.com/Toni-SM/skrl

### Citation
If you found any part of this code useful, please consider citing:
```
@article{cheng2023parkour,
title={Extreme Parkour with Legged Robots},
author={Cheng, Xuxin and Shi, Kexin and Agarwal, Ananye and Pathak, Deepak},
journal={arXiv preprint arXiv:2309.14341},
year={2023}
}
```