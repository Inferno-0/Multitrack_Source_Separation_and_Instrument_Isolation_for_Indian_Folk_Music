import torch
import yaml
import demucs.states
from pathlib import Path
from demucs.apply import apply_model
import torchaudio
import os

ckpt_path = Path(r'D:\finetune_htdemucs_runs\run_002\best.pt')

try:
    model = demucs.states.load_model(ckpt_path)
    print("Model loaded successfully via load_model!")
except Exception as e:
    print(f"Failed to load via load_model: {e}")
