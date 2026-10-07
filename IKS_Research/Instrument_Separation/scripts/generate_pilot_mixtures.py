import json
import os
import torch
import torchaudio
import io

random_seed = 42
torch.manual_seed(random_seed)

matrix_path = r'D:\IKS_Research\Instrument_Separation\mixtures\pilot_matrix.json'
out_dir = r'D:\IKS_Research\Instrument_Separation\mixtures\pilot'
os.makedirs(out_dir, exist_ok=True)

with open(matrix_path, 'r') as f:
    matrix = json.load(f)

mix_dur = 6.0
query_dur = 10.0
sr = 44100
mix_samples = int(mix_dur * sr)
query_samples = int(query_dur * sr)

def load_and_crop(path, expected_samples, offset_seconds=0.0):
    with open(path, 'rb') as f:
        data = f.read()
    waveform, file_sr = torchaudio.load(io.BytesIO(data), format="wav")
    
    if file_sr != sr:
        waveform = torchaudio.functional.resample(waveform, file_sr, sr)
    if waveform.shape[0] > 1:
        waveform = waveform[0:1, :]
    length = waveform.shape[1]
    
    offset_samples = int(offset_seconds * sr)
    
    if length > expected_samples + offset_samples:
        waveform = waveform[:, offset_samples : offset_samples + expected_samples]
    else:
        if length > offset_samples:
            waveform = waveform[:, offset_samples:]
            pad = expected_samples - waveform.shape[1]
            waveform = torch.nn.functional.pad(waveform, (0, pad))
        else:
            waveform = torch.zeros(1, expected_samples)
    return waveform

final_metadata = []

for ex in matrix:
    ex_id = ex['id']
    ex_dir = os.path.join(out_dir, ex_id)
    stems_dir = os.path.join(ex_dir, 'stems')
    os.makedirs(stems_dir, exist_ok=True)
    
    mix_waveform = torch.zeros(1, mix_samples)
    
    for inst, info in ex['sources'].items():
        stem = load_and_crop(info['path'], mix_samples, offset_seconds=10.0)
        gain = 1.0 / len(ex['sources'])
        stem_scaled = stem * gain
        
        stem_out = os.path.join(stems_dir, f"{inst}.wav")
        torchaudio.save(stem_out, stem, sr)
        
        info['gain_applied_in_mix'] = gain
        mix_waveform += stem_scaled
        
    mix_out = os.path.join(ex_dir, "clean_mixture.wav")
    torchaudio.save(mix_out, mix_waveform, sr)
    
    query_stem = load_and_crop(ex['query_file']['path'], query_samples, offset_seconds=0.0)
    query_out = os.path.join(ex_dir, "query.wav")
    torchaudio.save(query_out, query_stem, sr)
    
    if ex['target_present']:
        ex['target_path'] = os.path.join(stems_dir, f"{ex['query_instrument']}.wav")
    else:
        ex['target_path'] = None
        
    ex['mixture_path'] = mix_out
    ex['query_path'] = query_out
    
    with open(os.path.join(ex_dir, "metadata.json"), 'w') as f:
        json.dump(ex, f, indent=4)
        
    final_metadata.append(ex)

with open(os.path.join(out_dir, 'pilot_dataset_metadata.json'), 'w') as f:
    json.dump(final_metadata, f, indent=4)

print("Generated all pilot mixtures.")
