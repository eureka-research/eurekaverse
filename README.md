# Eurekaverse: Environment Curriculum Generation via Large Language Models

<div align="center">

[[Website]](https://eureka-research.github.io/eurekaverse/)
[[arXiv]](https://arxiv.org/abs/2411.01775)
[[PDF]](https://eureka-research.github.io/eurekaverse/assets/eurekaverse_paper.pdf)

[William Liang](https://willjhliang.github.io), [Sam Wang](https://samuelwang23.github.io/), [Hung-Ju Wang](https://www.linkedin.com/in/hungju-wang),<br>
[Osbert Bastani](https://obastani.github.io/), [Dinesh Jayaraman<sup>†</sup>](https://www.seas.upenn.edu/~dineshj/), [Yecheng Jason Ma<sup>†</sup>](https://jasonma2016.github.io/)

University of Pennsylvania

[![Python Version](https://img.shields.io/badge/Python-3.8-blue.svg)](https://github.com/eureka-research/Eurekaverse)
[<img src="https://img.shields.io/badge/Framework-PyTorch-red.svg"/>](https://pytorch.org/)
[![GitHub license](https://img.shields.io/github/license/eureka-research/eurekaverse)](https://github.com/eureka-research/Eurekaverse/blob/main/LICENSE)

______________________________________________________________________

</div>

https://github.com/user-attachments/assets/c197081e-90ce-4d70-9ac9-b656d7ea630f

https://github.com/user-attachments/assets/e682cf81-bffd-428f-a13d-c3bb903823dc

Recent work has demonstrated that a promising strategy for teaching robots a wide range of complex skills is by training them on a curriculum of progressively more challenging environments. However, developing an effective curriculum of environment distributions currently requires significant expertise, which must be repeated for every new domain. Our key insight is that environments are often naturally represented as code. Thus, we probe whether effective environment curriculum design can be achieved and automated via code generation by large language models (LLM). In this paper, we introduce Eurekaverse, an unsupervised environment design algorithm that uses LLMs to sample progressively more challenging, diverse, and learnable environments for skill training. We validate Eurekaverse's effectiveness in the domain of quadrupedal parkour learning, in which a quadruped robot must traverse through a variety of obstacle courses. The automatic curriculum designed by Eurekaverse enables gradual learning of complex parkour skills in simulation and can successfully transfer to the real-world, outperforming manual training courses designed by humans.


# Installation
The following instructions will install everything under one Conda environment. We have tested on Ubuntu 20.04.

1. Create a new Conda environment with:
    ```
    conda create -n eurekaverse python=3.8
    conda activate eurekaverse
    ```

2. Install IsaacGym:
    1. Download and install IsaacGym from NVIDIA: https://developer.nvidia.com/isaac-gym.
    2. Unzip the file:
        ```
        tar -xf IsaacGym_Preview_4_Package.tar.gz
        ```
    3. Install the python package:
        ```
        cd isaacgym/python
        pip install -e .
        ```

3. Install Eurekaverse:
    ```
    cd eurekaverse
    pip install -e .
    ```

4. Install `legged_gym` and `rsl_rl`, base code used for quadruped reinforcement learning in simulation, extended from [Extreme Parkour](https://github.com/chengxuxin/extreme-parkour):
    ```
    pip install -e extreme-parkour/legged_gym
    pip install -e extreme-parkour/rsl_rl
    ```

# Usage
1. Set your OpenAI API key via:
    ```
    export OPENAI_API_KEY=<YOUR_KEY>
    ```

2. To ensure that necessary libraries are being detected properly, update `LD_LIBRARY_PATH` with:
    ```
    export LD_LIBRARY_PATH=~/anaconda3/envs/eurekaverse/lib:$LD_LIBRARY_PATH
    ```

3. First, train a walking policy. This will be the initial policy for Eurekaverse.
    ```
    cd extreme-parkour/legged_gym/legged_gym/scripts
    python train.py --exptid walk_pretrain --max_iterations 1000 --terrain_type simple
    ```

4. Now, we are ready to begin environment curriculum generation and training. Review the configuration in `eurekaverse/eurekaverse/config/config.yaml`. The current parameters were used for our experiments. To run generation:
    ```
    cd ../../../../eurekaverse
    python run_eurekaverse.py
    ```
    The outputs will be saved in `eurekaverse/outputs/run_eurekaverse/<RUN_ID>`.

5. Afterwards, distill the final policy via:
    ```
    python distill_eurekaverse.py <YOUR_RUN_ID>
    ```
    Similarly, the outputs will be saved in `eurekaverse/outputs/distill_eurekaverse/<RUN_ID>`.

## Visualization
To visualize a trained policy, run:
```
cd extreme-parkour/legged_gym/legged_gym/scripts
python evaluate.py --exptid <EXPTID> --terrain_type benchmark --terrain_rows 3 --terrain_cols 20
```

You can use a mouse to move the camera and `[` or `]` to switch between different agents.

# Deployment
Our deployment infrastructure on the Unitree Go1 uses LCM for low-level commands and Docker to run the policy. Note that our Docker is only tested on the Jetson Xavier NX on the Go1. Our setup is loosely based on [LucidSim](https://github.com/lucidsim/lucidsim) and [Walk These Ways](https://github.com/Improbable-AI/walk-these-ways).

## Initial Setup

1. Connect a Realsense D435 to the middle USB port on the Go1. 3D print and mount the Realsense using [this design](https://github.com/ZiwenZhuang/parkour/blob/main/go1_ckpts/go1_camMount_30Down.step) from [Robot Parkour Learning](https://github.com/ZiwenZhuang/parkour).

2. Start up the Go1 and connect to it on your machine via Ethernet. Make sure you can ssh onto the NX (192.168.123.15).

3. Put the robot into damping mode with the controller: L2+A, L2+B, L1+L2+START. The robot should be lying on the ground afterwards.

4. Build the Docker image with:
    ```
    cd go1_deploy/docker
    docker buildx build --platform linux/arm64 -t go1-deploy:latest . --load
    ```

5. Save the image:
    ```
    docker save go1-deploy -o go1_deploy.tar
    ```

6. Copy the Docker and other necessary files over to the Go1:
    ```
    ./send_to_unitree.sh
    scp go1_deploy.tar go1-nx:/home/unitree/go1_gym/go1_gym_deploy/scripts
    ```

6. Connect onto the Go1 NX, then load the Docker:
    ```
    sudo docker load -i go1_deploy.tar
    ```

## Running the Policy

1. Connect onto the Go1 NX. You should see `eurekaverse` in the home directory (from `./send_to_unitree.sh`).

2. Start LCM:
    ```
    cd eurekaverse/go1_deploy/launch
    ./start_lcm.sh
    ```

3. Start and enter the Docker container:
    ```
    sudo -E ./start_docker.sh
    ./enter_docker.sh
    ```

4. Within the container, run the policy:
    ```
    python3 deploy_policy.py
    ```

5. Monitor the output, and when it's ready to calibrate, press R2. Pressing R2 again will start the policy, and R2 again will stop.

## Acknowledgements

We thank the following open-sourced projects:
* Our simulation runs in [IsaacGym](https://developer.nvidia.com/isaac-gym).
* Our parkour simulation builds on [Extreme Parkour](https://github.com/chengxuxin/extreme-parkour).
* Our deployment infrastructure builds on [LucidSim](https://github.com/lucidsim/lucidsim) and [Walk These Ways](https://github.com/Improbable-AI/walk-these-ways).
* Our Realsense mount was released in [Robot Parkour Learning](https://github.com/ZiwenZhuang/parkour).
* The environment structure and training code build on [Legged Gym](https://github.com/leggedrobotics/legged_gym) and [RSL_RL](https://github.com/leggedrobotics/rsl_rl).

# License
This codebase is released under [MIT License](LICENSE).

## Citation
If you find our work useful, please consider citing us!
```bibtex
@inproceedings{liang2024eurekaverse,
    title   = {Eurekaverse: Environment Curriculum Generation via Large Language Models},
    author  = {William Liang and Sam Wang and Hungju Wang and Osbert Bastani and Dinesh Jayaraman and Jason Ma}
    year    = {2024},
  booktitle = {Conference on Robot Learning (CoRL)}
}
```
