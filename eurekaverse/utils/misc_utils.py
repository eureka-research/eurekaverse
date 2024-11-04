
import subprocess
import json
import os
import logging
import time
import threading
import contextlib
import re

gpustat_lock = threading.Lock()
gpustat_next_ready_time = time.time()

def get_freest_gpu(gpustat_delay=10):
    # We use the lock to ensure that gpustat is used by only one thread at a time
    global gpustat_lock, gpustat_next_ready_time
    with gpustat_lock:
        if time.time() < gpustat_next_ready_time:
            time.sleep(gpustat_next_ready_time - time.time())
        sp = subprocess.Popen(['gpustat', '--json'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out_str, _ = sp.communicate()
        gpustat_next_ready_time = time.time() + gpustat_delay  # Give gpustat some time to refresh

    gpustats = json.loads(out_str.decode('utf-8'))
    freest_gpu = min(gpustats['gpus'], key=lambda x: x['memory.used'])
    return f"cuda:{freest_gpu['index']}"

def get_num_gpus():
    sp = subprocess.Popen(['gpustat', '--json'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out_str, _ = sp.communicate()
    gpustats = json.loads(out_str.decode('utf-8'))
    return len(gpustats['gpus'])

def run_subprocess(command, log_file):
    if log_file == None:
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, env={**os.environ.copy(), "TQDM_DISABLE": "1"})
    else:
        with open(log_file, "a") as f:
            f.write("\n" + "="*100 + "\n" + f"Running command: {command}\n" + "="*100 + "\n")
            process = subprocess.Popen(command.split(), stdout=f, stderr=f, env={**os.environ.copy(), "TQDM_DISABLE": "1"})
    return process

def wait_subprocess(process, log_file, success_log, failure_log, timeout=60):
    timeout = time.time() + timeout
    while True:
        if log_file is None:
            output = process.stdout.readline()
        else: 
            with open(log_file, 'r') as file:
                output = file.read()
        if output:
            if success_log in output:
                return True, False
            if failure_log in output:
                time.sleep(1)  # Wait for the process to finish writing to the log file
                return False, False

        retcode = process.poll()
        if retcode is not None:
            logging.warning(f"Process terminated while waiting with code {retcode}")
            return False, False
        if time.time() > timeout:
            return False, True

        time.sleep(1)

@contextlib.contextmanager
def suppress_output():
    with open(os.devnull, "w") as fnull:
        with contextlib.redirect_stdout(fnull), contextlib.redirect_stderr(fnull):
            yield

@contextlib.contextmanager
def seeded():
    import random
    import numpy as np
    import torch

    state = {}
    state['random'] = random.getstate()
    state['np_random'] = np.random.get_state()
    state['torch_rng_cpu'] = torch.get_rng_state()
    state['torch_rng_gpu'] = torch.cuda.get_rng_state_all()
    state['torch_rng_deterministic'] = torch.backends.cudnn.deterministic
    state['os_hash_seed'] = os.environ.get('PYTHONHASHSEED', None)
    
    try:
        yield
    finally:
        random.setstate(state['random'])
        np.random.set_state(state['np_random'])
        torch.set_rng_state(state['torch_rng_cpu'])
        for i, state_gpu in enumerate(state['torch_rng_gpu']):
            torch.cuda.set_rng_state(state_gpu, i)
        if state['os_hash_seed'] is None:
            del os.environ['PYTHONHASHSEED']
        else:
            os.environ['PYTHONHASHSEED'] = state['os_hash_seed']
        torch.backends.cudnn.deterministic = state['torch_rng_deterministic']

def alphanum_key(s):
    # Use this with sorted() to sort a list of strings alphanumerically
    return [int(text) if text.isdigit() else text for text in re.split('(\d+)', s)]