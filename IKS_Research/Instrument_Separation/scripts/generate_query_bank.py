import os
import csv
import json
import random
import torchaudio
import torch
import io

def generate_query_bank():
    manifest_path = r'D:\IKS_Research\Instrument_Separation\datasets\source_split_manifest.csv'
    source_dir = r'D:\ISOLATED_INSTRUMENTS_PREPARED'
    output_dir = r'D:\IKS_Research\Instrument_Separation\datasets\query_bank'
    
    os.makedirs(output_dir, exist_ok=True)
    
    target_instruments = ['tabla', 'harmonium', 'flute', 'dholak', 'dhul']
    
    # Read manifest
    candidates = {inst: [] for inst in target_instruments}
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            inst = row['instrument']
            split = row['split']
            orig_name = row['original_filename']
            
            if inst in target_instruments and split == 'TRAIN':
                if orig_name == 'Dholak Sample - 26.wav':
                    continue
                
                candidates[inst].append(row)
                
    metadata = {}
    query_length_samples = 44100 * 10 # 10 seconds at 44.1kHz
    
    random.seed(42)
    
    for inst in target_instruments:
        inst_dir = os.path.join(output_dir, inst)
        os.makedirs(inst_dir, exist_ok=True)
        
        inst_candidates = candidates[inst]
        # Pick 5 random candidates
        selected = random.sample(inst_candidates, min(5, len(inst_candidates)))
        
        metadata[inst] = []
        
        for i, row in enumerate(selected):
            src_path = os.path.join(source_dir, inst, 'audio', row['prepared_filename'])
            
            # Load audio robustly
            with open(src_path, 'rb') as f:
                waveform, sr = torchaudio.load(io.BytesIO(f.read()), format="wav")
            
            # Make stereo
            if waveform.shape[0] == 1:
                waveform = waveform.repeat(2, 1)
            elif waveform.shape[0] > 2:
                waveform = waveform[:2, :]
                
            # Pad or truncate to exactly 10 seconds
            length = waveform.shape[1]
            if length < query_length_samples:
                pad = query_length_samples - length
                waveform = torch.nn.functional.pad(waveform, (0, pad))
            elif length > query_length_samples:
                waveform = waveform[:, :query_length_samples]
                
            out_filename = f"query_{i:03d}_{row['prepared_filename']}"
            out_path = os.path.join(inst_dir, out_filename)
            
            torchaudio.save(out_path, waveform, sr)
            
            metadata[inst].append({
                "query_file": out_filename,
                "source_file": row['prepared_filename'],
                "original_name": row['original_filename']
            })
            
    with open(os.path.join(output_dir, "metadata.json"), 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=4)
        
    print(f"Generated query bank at {output_dir}")
    for inst, items in metadata.items():
        print(f"  {inst}: {len(items)} queries")
        
if __name__ == '__main__':
    generate_query_bank()
