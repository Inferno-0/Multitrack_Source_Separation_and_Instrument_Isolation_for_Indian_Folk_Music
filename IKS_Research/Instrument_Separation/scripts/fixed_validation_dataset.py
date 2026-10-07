import os
import json
import random
import torch
import torchaudio
import io
import sys
sys.path.append(r'C:\iks_scripts\query-bandit')
from torch.utils.data import Dataset, DataLoader

class IKSValidationDataset(Dataset):
    def __init__(self, manifest_path, source_dir):
        self.source_dir = source_dir
        self.chunk_size_samples = int(6.0 * 44100)
        self.query_size_samples = int(10.0 * 44100)
        
        with open(manifest_path, 'r', encoding='utf-8') as f:
            self.samples = json.load(f)

    def __len__(self):
        return len(self.samples)
        
    def _load_chunk(self, file_path, target_length, rng, exclude_interval=None):
        with open(file_path, 'rb') as f:
            waveform, sr = torchaudio.load(io.BytesIO(f.read()), format="wav")
            
        if waveform.shape[0] == 1:
            waveform = waveform.repeat(2, 1)
        elif waveform.shape[0] > 2:
            waveform = waveform[:2, :]
            
        length = waveform.shape[1]
        start = 0
        
        if length > target_length:
            if exclude_interval is not None:
                ex_start, ex_end = exclude_interval
                valid_starts = []
                
                max_start_1 = ex_start - target_length
                if max_start_1 >= 0:
                    valid_starts.extend(range(0, max_start_1 + 1))
                    
                max_start_2 = length - target_length
                if max_start_2 >= ex_end:
                    valid_starts.extend(range(ex_end, max_start_2 + 1))
                    
                if not valid_starts:
                    max_start = length - target_length
                    start = rng.randint(0, max_start)
                else:
                    start = rng.choice(valid_starts)
            else:
                max_start = length - target_length
                start = rng.randint(0, max_start)
                
            waveform = waveform[:, start:start+target_length]
        elif length < target_length:
            pad = target_length - length
            waveform = torch.nn.functional.pad(waveform, (0, pad))
            
        return waveform, start, length

    def __getitem__(self, idx):
        sample = self.samples[idx]
        
        # Deterministic RNG for this exact sample index
        rng = random.Random(42 + idx)
        
        target_inst = sample['target_instrument']
        is_positive = sample['is_positive']
        
        mix_tensor = torch.zeros((2, self.chunk_size_samples))
        target_tensor = torch.zeros((2, self.chunk_size_samples))
        
        target_start = None
        target_end = None
        target_file = None
        
        mix_intervals = []
        
        for src in sample['mixture_sources']:
            inst = src['instrument']
            path = os.path.join(self.source_dir, inst, 'audio', src['file'])
            chunk, start_idx, file_len = self._load_chunk(path, self.chunk_size_samples, rng)
            
            gain = src['gain']
            chunk = chunk * gain
            mix_tensor += chunk
            
            mix_intervals.append({
                "instrument": inst,
                "file": src['file'],
                "start": start_idx,
                "end": start_idx + self.chunk_size_samples,
                "file_len": file_len
            })
            
            if inst == target_inst and is_positive:
                target_tensor += chunk
                target_start = start_idx
                target_end = start_idx + self.chunk_size_samples
                target_file = src['file']
                
        # Simple peak normalization
        max_val = torch.max(torch.abs(mix_tensor))
        if max_val > 1.0:
            scale = 0.99 / max_val
            mix_tensor *= scale
            target_tensor *= scale
            
        # Query
        q_inst = sample['query']['instrument']
        q_path = os.path.join(self.source_dir, q_inst, 'audio', sample['query']['file'])
        
        # Determine if query uses the exact same recording as the target mixture source
        is_same_file = False
        exclude_interval = None
        if target_inst == q_inst and is_positive:
            if target_file == sample['query']['file']:
                is_same_file = True
                exclude_interval = (target_start, target_end)
        
        q_waveform, q_start, q_len = self._load_chunk(q_path, self.query_size_samples, rng, exclude_interval=exclude_interval)
        
        return {
            "mixture": {"audio": mix_tensor},
            "queries": {"target": {"audio": q_waveform}},
            "query": {"audio": q_waveform},
            "sources": {"target": {"audio": target_tensor}},
            "estimates": {},
            "meta": {
                "id": sample['id'],
                "target_instrument": target_inst,
                "is_positive": is_positive,
                "mixture_intervals": mix_intervals,
                "query_interval": {
                    "instrument": q_inst,
                    "file": sample['query']['file'],
                    "start": q_start,
                    "end": q_start + self.query_size_samples,
                    "file_len": q_len,
                    "is_same_file": is_same_file
                }
            }
        }

def validation_collate(batch):
    mix_audios = torch.stack([item["mixture"]["audio"] for item in batch])
    q_audios = torch.stack([item["queries"]["target"]["audio"] for item in batch])
    target_audios = torch.stack([item["sources"]["target"]["audio"] for item in batch])
    metas = [item["meta"] for item in batch]
    
    return {
        "mixture": {"audio": mix_audios},
        "queries": {"target": {"audio": q_audios}},
        "query": {"audio": q_audios},
        "sources": {"target": {"audio": target_audios}},
        "estimates": {},
        "meta": metas
    }

if __name__ == "__main__":
    dataset = IKSValidationDataset(
        manifest_path=r'D:\IKS_Research\Instrument_Separation\finetune_banquet_runs\run_002\validation_manifest.json',
        source_dir=r'D:\ISOLATED_INSTRUMENTS_PREPARED'
    )
    dl = DataLoader(dataset, batch_size=1, collate_fn=validation_collate)
    for batch in dl:
        print(batch['meta'])
        break
