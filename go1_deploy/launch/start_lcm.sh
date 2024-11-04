#!/bin/bash
ps -aux | grep point_cloud_node | awk '{print $2}' | xargs kill -9
ps -aux | grep mqttControlNode | awk '{print $2}' | xargs kill -9
ps -aux | grep live_human_pose | awk '{print $2}' | xargs kill -9
ps -aux | grep rosnode | awk '{print $2}' | xargs kill -9

sudo docker stop foxy_controller || true
sudo docker rm foxy_controller || true

sudo kill $(ps aux |grep lcm_position | awk '{print $2}')
cd ~/go1_gym/go1_gym_deploy/unitree_legged_sdk_bin/
yes "" | sudo ./lcm_position