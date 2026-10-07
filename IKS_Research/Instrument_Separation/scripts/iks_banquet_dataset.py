import torch
from torch.utils.data import Dataset
import pytorch_lightning as pl
from torch.utils.data import DataLoader
import torchaudio
import pandas as pd
import json

class IKSSourceSeparationDataset(Dataset):
    def __init__(self, manifest_path, split, mixture_metadata_path, chunk_size_seconds=6.0, query_size_seconds=10.0, sample_rate=44100):
        self.manifest = pd.read_csv(manifest_path)
        self.split = split
        self.chunk_size_samples = int(chunk_size_seconds * sample_rate)
        self.query_size_samples = int(query_size_seconds * sample_rate)
        self.sample_rate = sample_rate
        
        with open(mixture_metadata_path, 'r') as f:
            self.mixtures = json.load(f)

    def __len__(self):
        return len(self.mixtures)

    def _load_audio(self, path, expected_samples):
        waveform, sr = torchaudio.load(path)
        if sr != self.sample_rate:
            raise ValueError(f"Expected sample rate {self.sample_rate}, got {sr} in {path}")
            
        if waveform.shape[0] == 1:
            waveform = waveform.repeat(2, 1) # [2, N]
        elif waveform.shape[0] > 2:
            waveform = waveform[:2, :]
            
        length = waveform.shape[1]
        if length < expected_samples:
            pad = expected_samples - length
            waveform = torch.nn.functional.pad(waveform, (0, pad))
        elif length > expected_samples:
            waveform = waveform[:, :expected_samples]
            
        return waveform

    def __getitem__(self, idx):
        mix_info = self.mixtures[idx]
        
        mix_audio = self._load_audio(mix_info['mixture_path'], self.chunk_size_samples)
        
        if mix_info['target_present']:
            target_audio = self._load_audio(mix_info['target_path'], self.chunk_size_samples)
        else:
            target_audio = torch.zeros(2, self.chunk_size_samples, dtype=torch.float32)
            
        query_audio = self._load_audio(mix_info['query_path'], self.query_size_samples)
        
        return {
            "mixture": {"audio": mix_audio},
            "query": {"audio": query_audio},
            "sources": {"target": {"audio": target_audio}},
            "metadata": mix_info
        }

class IKSSourceSeparationDataModule(pl.LightningDataModule):
    def __init__(self, manifest_path, mixture_metadata_path, batch_size=1):
        super().__init__()
        self.manifest_path = manifest_path
        self.mixture_metadata_path = mixture_metadata_path
        self.batch_size = batch_size
        
    def setup(self, stage=None):
        self.dataset = IKSSourceSeparationDataset(
            manifest_path=self.manifest_path,
            split="TEST",
            mixture_metadata_path=self.mixture_metadata_path
        )
        
    def train_dataloader(self):
        return DataLoader(self.dataset, batch_size=self.batch_size, shuffle=False)
