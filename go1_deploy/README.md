# Go1 Deployment

Put the Go1 in its prone position.

Boot up the Go1 and Orin. Give the Go1 a few minutes for calibration.

### Initial Setup

Upload all code to the Orin.

```bash
rsync -zvhra $HOME/mit/parkour orin[01,02]:mit/parkour
```

On orin, set up networking:

```bash
# on orin
cd $HOME
./setup_network.sh eth0 # configure IP on eth0 and route LCM traffic
```

### On the Go1

Enter the Go1 from the Orin.

```bash
# on orin

# Depending on which unit, this will kill the default controller.
# On unit 1 (red), the default controller is killed on boot. 
ssh go1-pi
```

Start the LCM.

```bash
# on orin

ssh go1-nx

# make sure the go1 is in prone position.
./setup_lcm.sh
```

### Run Inference on Orin


```bash
# on orin

conda activate torch
cd mit/parkour
export PYTHONPATH=$PWD:$PYTHONPATH

cd go1_gym_deploy/scripts

# blind policy
python deploy_policy.py [args]

# vision policy
python deploy_vision.py [args]
```

You can change the policy through CLI or by editing the script. 
The arguments are as follows:

```bash
❯ python deploy_vision.py -h
usage: deploy_vision.py [-h] [--checkpoint] [--device] [--offline-mode]

optional arguments:
    -h, --help      show this help message and exit
    --checkpoint  :str '/lucid-sim/lucid-sim/scripts/train/2024-0...
                    Path to the model checkpoint.
    --device      :str 'cuda' Device to run the model on.
    --offline-mode  :bool False
                    -> True Run the model in offline mode, with downloaded checkpoint.
```
