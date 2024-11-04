from setuptools import find_packages
from distutils.core import setup

setup(
    name='eurekaverse',
    author='William Liang',
    version='1.0',
    description='Accompanying code for Environment Curriculum Generation via Large Language Models',
    python_requires='>=3.8',
    install_requires=[
        'torch@https://download.pytorch.org/whl/cu113/torch-1.10.0%2Bcu113-cp38-cp38-linux_x86_64.whl',
        'torchvision@https://download.pytorch.org/whl/cu113/torchvision-0.11.1%2Bcu113-cp38-cp38-linux_x86_64.whl',
        'torchaudio@https://download.pytorch.org/whl/cu113/torchaudio-0.10.0%2Bcu113-cp38-cp38-linux_x86_64.whl',
        'numpy<1.24',
        'scipy>=0.13.0',
        'matplotlib',
        'openai',
        'opencv-python',
        'pydelatin',
        'pyfqmr',
        'hydra-core',
        'wandb',
        'gpustat',
        'tqdm',
        'ipdb',
    ],
    packages=find_packages()
)