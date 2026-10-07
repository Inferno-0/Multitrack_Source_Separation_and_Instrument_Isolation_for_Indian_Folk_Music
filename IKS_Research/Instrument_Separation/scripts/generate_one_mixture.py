import os
import pandas as pd
import numpy as np
import soundfile as sf
import json

prepared_dir = r'D:\ISOLATED_INSTRUMENTS_PREPARED'
manifest_path = r'D:\IKS_Research\Instrument_Separation\datasets\source_split_manifest.csv'
out_dir = r'D:\IKS_Research\Instrument_Separation\mixtures\pilot_example_0'
os.makedirs(out_dir, exist_ok=True)

df = pd.read_csv(manifest_path)
train_df = df[df['split'] == 'TRAIN']

np.random.seed(42)

def read_chunk(filepath, sr=44100, chunk_sec=6.0):
    info = sf.info(filepath)
    tot_samples = info.frames
    chunk_samples = int(chunk_sec * sr)
    if tot_samples <= chunk_samples:
        data, _ = sf.read(filepath)
        # Pad with zeros
        padded = np.zeros(chunk_samples)
        padded[:len(data)] = data
        return padded
    else:
        start = np.random.randint(0, tot_samples - chunk_samples)
        data, _ = sf.read(filepath, start=start, frames=chunk_samples)
        return data

# Select instruments
inst_choices = ['tabla', 'flute']
selected_stems = {}
meta = {'instruments': inst_choices, 'vocals_present': True, 'target': 'flute', 'sources': {}}

# Vocals
v_df = train_df[train_df['instrument'] == 'vocals']
v_row = v_df.sample(1).iloc[0]
v_path = os.path.join(prepared_dir, 'vocals', 'audio', v_row['prepared_filename'])
v_audio = read_chunk(v_path, chunk_sec=6.0)
selected_stems['vocals'] = v_audio * 0.5  # Gain reduction
meta['sources']['vocals'] = str(v_row['original_filename'])

# Instruments
for inst in inst_choices:
    i_df = train_df[(train_df['instrument'] == inst) & (train_df['eligible_as_mixture_source'] == True)]
    i_row = i_df.sample(1).iloc[0]
    i_path = os.path.join(prepared_dir, inst, 'audio', i_row['prepared_filename'])
    selected_stems[inst] = read_chunk(i_path, chunk_sec=6.0) * 0.5
    meta['sources'][inst] = str(i_row['original_filename'])

# Mix
mixture = np.zeros(int(6.0 * 44100))
for k, v in selected_stems.items():
    mixture += v

# Normalize mixture to prevent clipping safely
peak = float(np.abs(mixture).max())
if peak > 0.9:
    mixture = (mixture / peak) * 0.9
    meta['normalization_applied'] = peak

sf.write(os.path.join(out_dir, 'mixture_clean.wav'), mixture, 44100)
sf.write(os.path.join(out_dir, 'vocals.wav'), selected_stems['vocals'], 44100)
for inst in inst_choices:
    sf.write(os.path.join(out_dir, f'{inst}.wav'), selected_stems[inst], 44100)
    if inst == meta['target']:
        sf.write(os.path.join(out_dir, 'target.wav'), selected_stems[inst], 44100)

# Query Selection (Target = flute)
q_df = train_df[(train_df['instrument'] == meta['target']) & (train_df['eligible_as_query_source'] == True)]
# Ensure no leakage from the mixture source!
q_df = q_df[q_df['original_filename'] != meta['sources'][meta['target']]]
q_row = q_df.sample(1).iloc[0]
q_path = os.path.join(prepared_dir, meta['target'], 'audio', q_row['prepared_filename'])
q_audio = read_chunk(q_path, chunk_sec=10.0)

sf.write(os.path.join(out_dir, 'query.wav'), q_audio, 44100)
meta['query_source'] = str(q_row['original_filename'])
meta['query_padding_needed'] = bool(q_row['duration_seconds'] < 10.0)

with open(os.path.join(out_dir, 'metadata.json'), 'w') as f:
    json.dump(meta, f, indent=2)

print("One pilot mixture created successfully at:", out_dir)
