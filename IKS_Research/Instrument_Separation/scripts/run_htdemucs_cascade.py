import os
import torch
import torchaudio
from demucs.htdemucs import HTDemucs
from demucs.apply import apply_model

INIT_PT = r"D:\finetune_htdemucs_runs\init_2stem_model.pt"
BEST_PT = r"D:\finetune_htdemucs_runs\run_002\best.pt"

init_ckpt = torch.load(INIT_PT, weights_only=False, map_location="cpu")
args, kwargs = init_ckpt["init_args_kwargs"]
model = HTDemucs(*args, **kwargs) if args else HTDemucs(**kwargs)

fine_ckpt = torch.load(BEST_PT, weights_only=False, map_location="cpu")
model.load_state_dict(fine_ckpt["model_state"])
model.eval()

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)
print(f"Loaded HT-Demucs on {device}")

pilot_dir = r'D:\IKS_Research\Instrument_Separation\mixtures\pilot'
subdirs = [d for d in os.listdir(pilot_dir) if d.startswith('pilot_')]

for d in subdirs:
    ex_dir = os.path.join(pilot_dir, d)
    mix_path = os.path.join(ex_dir, 'clean_mixture.wav')
    if not os.path.exists(mix_path):
        continue
        
    wav, sr = torchaudio.load(mix_path)
    if sr != 44100:
        wav = torchaudio.functional.resample(wav, sr, 44100)
        
    # The evaluation script duplicated the mono input to stereo [1, 2, N] 
    # and averaged the output channels.
    wav = wav.expand(2, -1).unsqueeze(0).to(device)
    
    with torch.no_grad():
        preds = apply_model(model, wav, shifts=1, split=True, overlap=0.25)
    
    # preds: (1, 2, 2, N) -> (1, sources, channels, time)
    preds = preds.squeeze(0).mean(dim=1).cpu() # [2, N] -> averaged to mono -> [sources, N]
    
    vocab_pred = preds[0:1, :]
    acc_pred = preds[1:2, :]
    
    torchaudio.save(os.path.join(ex_dir, 'htdemucs_vocals_pred.wav'), vocab_pred, 44100)
    torchaudio.save(os.path.join(ex_dir, 'htdemucs_accompaniment_pred.wav'), acc_pred, 44100)
    print(f"Processed {d}")

print("HT-Demucs cascade complete.")
