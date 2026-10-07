import os
import torch
import soundfile as sf
import yaml
import numpy as np
from demucs.htdemucs import HTDemucs
from demucs.apply import apply_model

ckpt_path = r'D:\finetune_htdemucs_runs\run_002\best.pt'
init_ckpt_path = r'D:\finetune_htdemucs_runs\init_2stem_model.pt'
mix_path = r'D:\IKS_Research\Instrument_Separation\mixtures\pilot_example_0\mixture_clean.wav'
out_dir = r'D:\IKS_Research\Instrument_Separation\demucs_outputs\pilot\pilot_example_0'
os.makedirs(out_dir, exist_ok=True)

print("Loading model from:", ckpt_path)

init_ckpt = torch.load(init_ckpt_path, weights_only=False, map_location="cpu")
args, kwargs = init_ckpt["init_args_kwargs"]
model = HTDemucs(*args, **kwargs) if args else HTDemucs(**kwargs)

fine_ckpt = torch.load(ckpt_path, weights_only=False, map_location="cpu")
model.load_state_dict(fine_ckpt["model_state"])
model.eval()

print("Model loaded. Sources:", model.sources)
print("Sample rate:", model.samplerate)
print("Audio channels:", model.audio_channels)

mix, sr = sf.read(mix_path)
assert sr == 44100
if mix.ndim == 1:
    mix = mix[None, :] 
    if model.audio_channels == 2:
        mix = np.concatenate([mix, mix], axis=0)
mix_tensor = torch.from_numpy(mix).float()
mix_tensor = mix_tensor.unsqueeze(0)

print("Input tensor shape:", mix_tensor.shape)

with torch.no_grad():
    sources = apply_model(model, mix_tensor, shifts=1, split=True, overlap=0.25, progress=True)

sources = sources[0] 
print("Output sources shape:", sources.shape)

for i, src_name in enumerate(model.sources):
    out_wav = sources[i].numpy()
    if out_wav.shape[0] == 2:
        out_wav = out_wav.mean(axis=0) # Mix down stereo output to mono for simplicity
        
    out_path = os.path.join(out_dir, f'demucs_{src_name}.wav')
    sf.write(out_path, out_wav, sr)
    print(f"Saved {out_path}")

print("HT-Demucs cascade test completed successfully.")
