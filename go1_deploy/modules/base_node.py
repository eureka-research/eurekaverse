import numpy as np
from shared_memory import SharedMemory
from typing import Union, Tuple
import torch
from functools import wraps
import time

class BaseNode:
    def __init__(self):
        super().__init__()

        # These should be overridden by the child class
        self.create_buffer_infos = {}
        self.access_buffer_infos = {}

        self._created_buffers = {}
        self._accessed_buffers = {}
        self._created_shms = []
        self._accessed_shms = []

        self.time_eps = 1e-6

        self._profile_start_times = {}
        self._profile_durations = {}
    
    def _create_buffers(self):
        for name, (shape, dtype) in self.create_buffer_infos.items():
            np_buffer = self._create_buffer(name, shape, dtype)
            self._created_buffers[name] = np_buffer

    def _create_buffer(self, name, shape, dtype=np.uint8):
        size = np.prod(shape) * np.dtype(dtype).itemsize
        shm = SharedMemory(create=True, size=size, name=name)
        np_buffer = np.ndarray(shape, dtype=dtype, buffer=shm.buf)

        self._created_shms.append(shm)
        print(f"Create buffer: {name} {shape} ({size / 1024:.2f} KB)")
        return np_buffer

    def _access_buffers(self):
        for name, (shape, dtype) in self.access_buffer_infos.items():
            np_buffer = self._access_buffer(name, shape, dtype)
            self._accessed_buffers[name] = np_buffer

    def _access_buffer(self, name, shape, dtype=np.uint8):
        size = np.prod(shape) * np.dtype(dtype).itemsize
        shm = SharedMemory(name=name, size=size)
        np_buffer = np.ndarray(shape, dtype=dtype, buffer=shm.buf)

        self._accessed_shms.append(shm)
        print(f"Access buffer: {name} {shape}")
        return np_buffer
    
    def _cleanup(self):
        for shm in self._created_shms:
            shm.close()
            shm.unlink()
        for shm in self._accessed_shms:
            shm.close()

    def read_buffer(self, name, as_torch=False):
        buffer = self._created_buffers[name] if name in self._created_buffers else self._accessed_buffers[name]
        if as_torch:
            return torch.from_numpy(buffer).to(self.device)
        return buffer

    def write_buffer(self, name, data):
        buffer = self._accessed_buffers[name] if name in self._accessed_buffers else self._created_buffers[name]
        np.copyto(buffer, data)
    
    def start_profile(self, name):
        self._profile_start_times[name] = time.perf_counter()
    
    def stop_profile(self, name, save=True):
        duration = time.perf_counter() - self._profile_start_times[name] if name in self._profile_start_times else 0
        if save and self.debug:
            if name not in self._profile_durations:
                self._profile_durations[name] = []
            self._profile_durations[name].append(duration)
        else:
            return duration
    
    def clear_profile(self):
        for name in self._profile_durations:
            self._profile_durations[name] = []
    
    def print_profile(self):
        if not self.debug:
            raise ValueError("Debug mode must be enabled to saved durations and print profile!")
        for name, durations in self._profile_durations.items():
            print(f"{name}: {max(durations):.4f} (max), {sum(durations) / len(durations):.4f} (avg)")

def shared_memory_wrapper(obj=None):
    # Used to automatically create and clean up shared memory buffers
    def decorator(fn):
        @wraps(fn)
        def wrapper(self, *args, **kwargs):
            target = getattr(self, obj) if obj else self
            target._create_buffers()
            target._access_buffers()
            try:
                return fn(self, *args, **kwargs)
            finally:
                target._cleanup()
        return wrapper
    return decorator

def shared_memory_cleanup_wrapper(obj=None):
    # Used when the looping function is called sometime after shared memory creation or access is needed
    def decorator(fn):
        @wraps(fn)
        def wrapper(self, *args, **kwargs):
            target = getattr(self, obj) if obj else self
            try:
                return fn(self, *args, **kwargs)
            finally:
                target._cleanup()
        return wrapper
    return decorator
