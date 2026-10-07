import os
import csv
import json
import random
import torch
import torchaudio
import io
import sys
sys.path.append(r'C:\iks_scripts\query-bandit')

from torch.utils.data import Dataset, DataLoader
from torch_audiomentations.utils.object_dict import ObjectDict
from core.types import BatchedInputOutput

class IKSDynamicDataset(Dataset):
    def __init__(self, manifest_path, source_dir, query_bank_dir, split='TRAIN', num_samples=2000):
        self.source_dir = source_dir
        self.query_bank_dir = query_bank_dir
        self.num_samples = num_samples
        self.chunk_size_samples = int(6.0 * 44100)
        self.query_size_samples = int(10.0 * 44100)
        
        self.instruments = ['tabla', 'harmonium', 'flute', 'dholak', 'dhul']
        self.vocals = 'vocals'
        
        self.sources = {inst: [] for inst in self.instruments + [self.vocals]}
        
        # Load manifest
        with open(manifest_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['split'] == split:
                    inst = row['instrument']
                    if inst in self.sources:
                        # Exclude Dholak 26
                        if row['original_filename'] == 'Dholak Sample - 26.wav':
                            continue
                        self.sources[inst].append(row)
                        
        # Load query bank metadata
        with open(os.path.join(query_bank_dir, 'metadata.json'), 'r', encoding='utf-8') as f:
            self.query_metadata = json.load(f)

    def __len__(self):
        return self.num_samples
        
    def _load_random_chunk(self, file_path, target_length):
        with open(file_path, 'rb') as f:
            waveform, sr = torchaudio.load(io.BytesIO(f.read()), format="wav")
            
        if waveform.shape[0] == 1:
            waveform = waveform.repeat(2, 1)
        elif waveform.shape[0] > 2:
            waveform = waveform[:2, :]
            
        length = waveform.shape[1]
        
        if length > target_length:
            max_start = length - target_length
            start = random.randint(0, max_start)
            waveform = waveform[:, start:start+target_length]
        elif length < target_length:
            pad = target_length - length
            waveform = torch.nn.functional.pad(waveform, (0, pad))
            
        return waveform

    def __getitem__(self, idx):
        # 1. Target instrument
        target_inst = random.choice(self.instruments)
        
        # 2. Positive or negative (10% negative)
        is_positive = random.random() > 0.1
        
        # 3. Number of instruments (1 to 5)
        num_insts = random.randint(1, 5)
        
        selected_insts = []
        if is_positive:
            selected_insts.append(target_inst)
            pool = [i for i in self.instruments if i != target_inst]
            num_others = min(num_insts - 1, len(pool))
            if num_others > 0:
                selected_insts.extend(random.sample(pool, num_others))
        else:
            pool = [i for i in self.instruments if i != target_inst]
            num_others = min(num_insts, len(pool))
            selected_insts.extend(random.sample(pool, num_others))
            
        # Add vocals
        selected_insts.append(self.vocals)
        
        # 4. Mix
        mix_tensor = torch.zeros((2, self.chunk_size_samples))
        target_tensor = torch.zeros((2, self.chunk_size_samples))
        
        for inst in selected_insts:
            row = random.choice(self.sources[inst])
            path = os.path.join(self.source_dir, inst, 'audio', row['prepared_filename'])
            chunk = self._load_random_chunk(path, self.chunk_size_samples)
            
            # Gain variation [-3dB to +3dB]
            gain = 10 ** (random.uniform(-3, 3) / 20.0)
            chunk = chunk * gain
            
            mix_tensor += chunk
            if inst == target_inst and is_positive:
                target_tensor += chunk
                
        # Simple peak normalization if clipping
        max_val = torch.max(torch.abs(mix_tensor))
        if max_val > 1.0:
            scale = 0.99 / max_val
            mix_tensor *= scale
            target_tensor *= scale
            
        # 5. Query
        q_meta = random.choice(self.query_metadata[target_inst])
        q_path = os.path.join(self.query_bank_dir, target_inst, q_meta['query_file'])
        
        with open(q_path, 'rb') as f:
            q_waveform, sr = torchaudio.load(io.BytesIO(f.read()), format="wav")
            
        # 6. Return exact dict structure
        # Bandit uses ObjectDict wrapped inside BatchedInputOutput internally, 
        # but the dataloader can just return the raw dict, then we wrap it in the training loop.
        
        return {
            "mixture": {"audio": mix_tensor},
            "queries": {"target": {"audio": q_waveform}},
            "query": {"audio": q_waveform},
            "sources": {"target": {"audio": target_tensor}},
            "estimates": {}
        }

def custom_collate(batch):
    # Stack the tensors
    mix_audios = torch.stack([item["mixture"]["audio"] for item in batch])
    q_audios = torch.stack([item["queries"]["target"]["audio"] for item in batch])
    target_audios = torch.stack([item["sources"]["target"]["audio"] for item in batch])
    
    return {
        "mixture": {"audio": mix_audios},
        "queries": {"target": {"audio": q_audios}},
        "query": {"audio": q_audios},
        "sources": {"target": {"audio": target_audios}},
        "estimates": {}
    }

if __name__ == "__main__":
    dataset = IKSDynamicDataset(
        manifest_path=r'D:\IKS_Research\Instrument_Separation\datasets\source_split_manifest.csv',
        source_dir=r'D:\ISOLATED_INSTRUMENTS_PREPARED',
        query_bank_dir=r'D:\IKS_Research\Instrument_Separation\datasets\query_bank'
    )
    
    dl = DataLoader(dataset, batch_size=1, collate_fn=custom_collate)
    for batch in dl:
        print("Mixture shape:", batch["mixture"]["audio"].shape)
        print("Query shape:", batch["queries"]["target"]["audio"].shape)
        print("Target shape:", batch["sources"]["target"]["audio"].shape)
        break
