#!/bin/bash

rsync -av --relative -e ssh \
    --exclude=*.pt \
    --exclude=*.mp4 \
    --exclude=extreme-parkour/legged_gym/logs/deploy/old \
    --exclude=go1_deploy/docker \
    go1_deploy \
    extreme-parkour/legged_gym/logs/deploy \
    extreme-parkour/legged_gym/legged_gym/envs/base \
    extreme-parkour/legged_gym/legged_gym/envs/go1 \
    extreme-parkour/legged_gym/setup.py \
    setup.py \
    unitree@192.168.123.15:/home/unitree/eurekaverse