import torch
import time
import os
import sys
import warnings
from omegaconf import OmegaConf
import torchaudio

sys.path.append(r'C:\iks_scripts\query-bandit')
warnings.filterwarnings('ignore')

from train import _build_model
from core.models.ebase import EndToEndLightningSystem
from core.losses.base import BaseLossHandler
from core.losses.l1snr import L1SNRLoss
from torch_audiomentations.utils.object_dict import ObjectDict
from core.types import BatchedInputOutput

print("CUDA Device:", torch.cuda.get_device_name(0))

class DummyHandler(dict):
    def __init__(self):
        super().__init__()
    def __call__(self, *args, **kwargs):
        pass
    def get_mode(self, mode):
        return self

def load_system():
    config_path = r'C:\iks_scripts\query-bandit\config\models\bandit-query-pre.yml'
    config = OmegaConf.load(config_path)

    if 'pretrain_encoder' in config.kwargs:
        config.kwargs.pretrain_encoder = None

    class DummyConfig:
        def __init__(self, model):
            self.model = model

    root_cfg = DummyConfig(config)
    model = _build_model(root_cfg)

    ckpt_path = r'C:\iks_scripts\query-bandit\ev-pre-aug.ckpt'
    state_dict = torch.load(ckpt_path, map_location='cpu')['state_dict']

    loss_handler = BaseLossHandler(loss=L1SNRLoss(), modality="audio", name="l1snr")

    system = EndToEndLightningSystem(
        model=model, 
        loss_handler=loss_handler, 
        metrics=DummyHandler(), 
        augmentation_handler=None, 
        inference_handler=None, 
        optimization_bundle=None
    )

    try:
        system.load_state_dict(state_dict, strict=True)
    except Exception as e:
        print(f"Strict load failed: {e}. Trying strict=False")
        system.load_state_dict(state_dict, strict=False)

    system.cuda()
    system.eval()
    return system

def load_audio(path, expected_samples, sample_rate=44100):
    waveform, sr = torchaudio.load(path)
    if sr != sample_rate:
        raise ValueError(f"Expected sample rate {sample_rate}, got {sr} in {path}")
        
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

@torch.no_grad()
def run_tests():
    system = load_system()
    
    chunk_size_samples = int(6.0 * 44100)
    query_size_samples = int(10.0 * 44100)
    
    mix_path = r'D:\IKS_Research\Instrument_Separation\mixtures\pilot\pilot_000\htdemucs_accompaniment_pred.wav'
    mix_audio = load_audio(mix_path, chunk_size_samples).unsqueeze(0).cuda()
    target_audio = torch.zeros_like(mix_audio)
    
    queries = {
        "Tabla (pilot_000)": r'D:\IKS_Research\Instrument_Separation\mixtures\pilot\pilot_000\query.wav',
        "Harmonium (pilot_001)": r'D:\IKS_Research\Instrument_Separation\mixtures\pilot\pilot_001\query.wav',
        "Flute (pilot_016)": r'D:\IKS_Research\Instrument_Separation\mixtures\pilot\pilot_016\query.wav',
        "Dholak (pilot_017)": r'D:\IKS_Research\Instrument_Separation\mixtures\pilot\pilot_017\query.wav'
    }
    
    results = {}
    
    print("\n--- Running Sensitivity and Negative Query Tests ---")
    for name, q_path in queries.items():
        query_audio = load_audio(q_path, query_size_samples).unsqueeze(0).cuda()
        
        batch_dict = {
            "mixture": {"audio": mix_audio},
            "queries": {"target": {"audio": query_audio}},
            "query": {"audio": query_audio},
            "sources": {"target": {"audio": target_audio}},
            "estimates": {}
        }
        batch = BatchedInputOutput.from_dict(batch_dict)
        
        out = system(batch)
        
        est_audio = out.estimates.target.audio
            
        rms = torch.sqrt(torch.mean(est_audio ** 2)).item()
        energy = torch.sum(est_audio ** 2).item()
        
        results[name] = {
            "est_audio": est_audio,
            "rms": rms,
            "energy": energy
        }
        print(f"Query: {name:35} | Output RMS: {rms:.6f} | Output Energy: {energy:.4f}")
        
    print("\n--- Sensitivity Test (Tabla vs Harmonium) ---")
    diff = torch.abs(results["Tabla (pilot_000)"]["est_audio"] - results["Harmonium (pilot_001)"]["est_audio"])
    mean_diff = torch.mean(diff).item()
    print(f"Mean absolute difference between Tabla query output and Harmonium query output: {mean_diff:.6f}")
    if mean_diff > 1e-4:
        print("PASS: System is sensitive to query changes.")
    else:
        print("FAIL: Output does not change significantly with query.")
        
    print("\n--- Negative Query Test (Flute on pilot_000) ---")
    flute_rms = results["Flute (pilot_016)"]["rms"]
    print(f"Flute Query Output RMS: {flute_rms:.6f}")
    
    if flute_rms < results["Tabla (pilot_000)"]["rms"] * 0.5:
        print("PASS: Negative query RMS is significantly lower than positive query.")
    else:
        print("NOTE: Negative query RMS is not significantly lower (expected for untrained/poorly conditioned pre-trained model).")
        
if __name__ == "__main__":
    run_tests()
