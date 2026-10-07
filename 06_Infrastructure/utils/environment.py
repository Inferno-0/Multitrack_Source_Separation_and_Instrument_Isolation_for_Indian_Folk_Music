"""
Utilities for inspecting and displaying environment and hardware configurations.
"""

import sys
import platform
from typing import Dict, Any, Tuple


def check_gpu() -> Tuple[bool, str]:
    """
    Checks if a CUDA-compatible GPU is available using PyTorch.

    Returns:
        A tuple containing a boolean (True if CUDA is available) and 
        the name of the GPU (or 'CPU' if CUDA is unavailable).
    """
    try:
        import torch
        if torch.cuda.is_available():
            return True, torch.cuda.get_device_name(0)
    except ImportError:
        pass
    
    return False, "CPU"


def get_environment_info() -> Dict[str, Any]:
    """
    Gathers crucial environment metadata including OS, Python, PyTorch, 
    and Demucs versions.

    Returns:
        A dictionary containing environment metadata.
    """
    info = {
        "Operating System": platform.system(),
        "OS Release": platform.release(),
        "Python Version": sys.version.split(" ")[0],
        "PyTorch Version": "Not Installed",
        "Demucs Version": "Not Installed",
        "CUDA Available": False,
        "GPU Name": "CPU"
    }

    try:
        import torch
        info["PyTorch Version"] = torch.__version__
    except ImportError:
        pass

    try:
        import demucs
        info["Demucs Version"] = demucs.__version__
    except ImportError:
        pass
        
    cuda_available, gpu_name = check_gpu()
    info["CUDA Available"] = cuda_available
    info["GPU Name"] = gpu_name

    return info


def print_environment_info() -> None:
    """
    Prints a formatted summary of the current execution environment.
    """
    info = get_environment_info()
    
    print("=" * 40)
    print("Environment Information Summary")
    print("=" * 40)
    for key, value in info.items():
        print(f"{key:<20}: {value}")
    print("=" * 40)
